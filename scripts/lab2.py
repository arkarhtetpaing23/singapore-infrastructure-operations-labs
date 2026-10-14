"""Real service/configuration, permission, bounded-storage and backup/restore tests."""
import hashlib
import json
from pathlib import Path
import time

def request(lab,path='/data.json',method='GET',node='client',target='app'):
    extra=" -X POST -H 'Content-Type: application/json' --data '{\"action\":\"lab-event\"}'" if method=='POST' else ''
    p=lab.ex(node,f"curl --noproxy '*' -sS --connect-timeout 1 --max-time 2 -w '\\n%{{http_code}}' {extra} http://{target}{path}",ok=(0,6,7,28))
    body,_,code=p.stdout.rpartition('\n')
    return {'code':int(code) if code.isdigit() else 0,'body':body,'stderr':p.stderr}

def hashes(lab,node):
    return lab.ex(node,'sha256sum /etc/nginx/nginx.conf /srv/app/data.json; stat -c "%a %n" /etc/nginx/nginx.conf /srv/app/data.json').stdout

def run(lab):
    lab.network('service')
    lab.node('app',network='service',cmd=['python3','-u','/lab/service_supervisor.py'],tmpfs={'/srv/pressure':'8m'})
    lab.node('client',network='service',memory='64m')
    lab.versions()
    lab.wait('service commissioning',lambda:request(lab)['code']==200)
    base=request(lab)
    baseline_data=json.loads(base['body'])
    lab.write('baseline-response.json',base)
    lab.write('baseline-processes-sockets.txt',lab.ex('app','ps -ef; ss -lntp; nginx -t; df -h /srv/pressure').stdout)
    lab.check('Commissioned nginx frontend and backend health',base['code']==200 and request(lab,'/health')['code']==200,base)
    lab.check('Baseline write operation succeeds',request(lab,'/events','POST')['code']==201,request(lab,'/events','POST'))
    # A change that is valid on disk must survive a container restart without regeneration.
    lab.ex('app',"python3 - <<'PY'\nimport json\nfrom pathlib import Path\np=Path('/srv/app/data.json'); d=json.loads(p.read_text()); d['version']=2; p.write_text(json.dumps(d)+'\\n')\nPY")
    saved=hashes(lab,'app')
    lab.write('commissioned-hashes.txt',saved)
    lab.docker('restart',lab.nodes['app'])
    lab.wait('container restart',lambda:request(lab)['code']==200)
    lab.check('Service/data configuration persists through container restart',hashes(lab,'app')==saved and json.loads(request(lab)['body'])['version']==2,request(lab))
    # Backup excludes ephemeral pressure-journal data and all private SSH material.
    lab.ex('app','tar -C / -cf /tmp/service-backup.tar etc/nginx/nginx.conf srv/app/data.json; tar -tvf /tmp/service-backup.tar')
    archive=lab.copy_out('app','/tmp/service-backup.tar','backup/service-backup.tar')
    lab.write('backup/manifest.json',{'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'files':['etc/nginx/nginx.conf','srv/app/data.json'],'excluded':'ephemeral tmpfs events journal; operating-system image; private keys','source_files':saved})
    lab.ex('app',"printf '\nthis_directive_does_not_exist on;\n' >> /etc/nginx/nginx.conf")
    syntax=lab.ex('app','nginx -t',ok=(0,1))
    lab.write('syntax-fault.txt',syntax.stdout+syntax.stderr)
    lab.check('Syntax validation rejects invalid change while current worker still serves',syntax.returncode==1 and request(lab)['code']==200,{'syntax_returncode':syntax.returncode,'current_response':request(lab)})
    networks=json.loads(lab.docker('inspect','--format','{{json .NetworkSettings.Networks}}',lab.nodes['app']).stdout)
    app_ip=next(iter(networks.values()))['IPAddress']
    lab.docker('restart',lab.nodes['app'])
    lab.wait('invalid startup exits',lambda:lab.docker('inspect','--format','{{.State.Running}}',lab.nodes['app']).stdout.strip()=='false')
    down=request(lab,target=app_ip)
    alias_down=request(lab)
    log_result=lab.docker('logs',lab.nodes['app'])
    log=log_result.stdout+log_result.stderr
    lab.write('restart-fault.json',{'direct_ip_response':down,'alias_response':alias_down,'container_logs':log})
    lab.check('Invalid saved config causes actual restart outage',down['code']==0 and 'this_directive_does_not_exist' in log,{'direct_ip_response':down,'alias_response':alias_down})
    # Copy known-good configuration out of the real backup into the stopped container.
    import tarfile
    with tarfile.open(archive) as t:
        member=t.getmember('etc/nginx/nginx.conf')
        config=t.extractfile(member).read()
    known_good=lab.out/'backup/known-good-nginx.conf'
    known_good.write_bytes(config)
    lab.copy_in('app',known_good,'/etc/nginx/nginx.conf')
    lab.docker('start',lab.nodes['app'])
    lab.wait('known-good config recovery',lambda:request(lab)['code']==200)
    lab.check('Config rollback restores useful service',hashes(lab,'app')==saved and request(lab,'/health')['code']==200,request(lab))
    lab.ex('app','chmod 000 /srv/app/data.json')
    denied=request(lab)
    log=lab.ex('app','tail -n 12 /var/log/nginx/error.log; stat -c "%a %n" /srv/app/data.json').stdout
    lab.write('permission-fault.json',{'response':denied,'diagnostics':log})
    lab.check('File permission fault causes HTTP 403 with supporting error',denied['code']==403 and 'Permission denied' in log,denied)
    lab.ex('app','chmod 644 /srv/app/data.json')
    lab.check('Permission recovery restores data',request(lab)['code']==200,request(lab))
    # ENOSPC is confined to this container's 8 MiB tmpfs, never the host filesystem.
    fill=lab.ex('app','dd if=/dev/zero of=/srv/pressure/fill bs=1M count=9; sync',ok=(0,1))
    lab.write('storage-fill.txt',fill.stdout+fill.stderr+lab.ex('app','df -h /srv/pressure; df -i /srv/pressure').stdout)
    degraded=request(lab,'/events','POST')
    lab.write('storage-fault-response.json',degraded)
    lab.check('Bounded full filesystem fails actual writes while reads remain healthy',degraded['code']==507 and json.loads(degraded['body']).get('errno')==28 and request(lab,'/health')['code']==200,degraded)
    lab.ex('app',"python3 - <<'PY'\nfrom pathlib import Path\nPath('/srv/pressure/fill').unlink()\nPY")
    recovered=request(lab,'/events','POST')
    lab.check('Scoped space recovery restores writes',recovered['code']==201,recovered)
    # Demonstrate data loss and restore into a separate freshly commissioned container.
    lab.ex('app',"printf '{\"version\":999,\"message\":\"damaged lab data\"}\n' > /srv/app/data.json")
    damaged=request(lab)
    lab.check('Data corruption observed in actual served content',json.loads(damaged['body'])['version']==999,damaged)
    start=time.monotonic()
    lab.node('restore',network='service',cmd=['python3','-u','/lab/service_supervisor.py'],tmpfs={'/srv/pressure':'8m'})
    lab.wait('clean restore target baseline',lambda:request(lab,target='restore')['code']==200)
    lab.copy_in('restore',archive,'/tmp/service-backup.tar')
    lab.ex('restore','tar -C / -xf /tmp/service-backup.tar; nginx -t; nginx -s reload')
    restored=request(lab,target='restore')
    elapsed=time.monotonic()-start
    lab.check('Backup restores bytes, permissions and useful response on clean target',restored['code']==200 and hashes(lab,'restore')==saved and json.loads(restored['body'])['version']==2,restored)
    lab.check('Restored backend write path is usable',request(lab,'/events','POST',target='restore')['code']==201,request(lab,'/events','POST',target='restore'))
    lab.write('restore.json',{'elapsed_seconds':round(elapsed,3),'measurement_scope':'Includes clean target creation and observed validation; one lab observation, not a production RTO guarantee','response':restored,'restored_hashes':hashes(lab,'restore'),'source_backup_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'ephemeral_events_restored':False})
    # Return the source to its good state as well.
    lab.ex('app','tar -C / -xf /tmp/service-backup.tar; nginx -t; nginx -s reload')
    lab.check('Final source service and writes healthy',hashes(lab,'app')==saved and request(lab)['code']==200 and request(lab,'/events','POST')['code']==201,request(lab))
    lab.write('final-logs.txt',lab.ex('app','tail -n 35 /var/log/nginx/error.log; tail -n 35 /var/log/nginx/access.log').stdout)
    lab.write('final-disk.txt',lab.ex('app','df -h /srv/pressure; df -i /srv/pressure').stdout)
