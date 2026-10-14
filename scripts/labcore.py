"""Docker lab controller. Host shell interpolation is deliberately avoided."""
from __future__ import annotations
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
IMAGE = 'arkar-dc-network:bookworm'
LABEL = 'io.arkar.infrastructure-lab'
PROJECT = 'singapore-dc-network'

def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()

def source_manifest():
    roots = ['scripts', 'runtime', 'configs']
    paths = [ROOT/'Dockerfile']
    for d in roots:
        paths.extend(p for p in (ROOT/d).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}

class Lab:
    def __init__(self, name, actor='assistant', keep=False):
        if actor not in ['assistant', 'candidate']:
            raise ValueError('Actor must be assistant or candidate')
        self.name, self.actor, self.keep = name, actor, keep
        self.run_id = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        self.prefix = f'adcn-{name}-{self.run_id[-10:].lower()}'
        self.out = ROOT/'evidence'/'runs'/f'{name}-{self.run_id}'
        self.out.mkdir(parents=True, exist_ok=False)
        self.nodes, self.networks, self.checks = {}, {}, []
        self.steps = 0
        self.meta = {'lab':name, 'run_id':self.run_id, 'started_utc':now(), 'actor':actor,
                     'candidate_understanding_assessed':False, 'source_sha256':source_manifest(),
                     'scope':'Isolated software laboratory; no production or physical-hardware evidence'}
        self.write('metadata.json', self.meta)

    def write(self, rel, value):
        p = self.out/rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(value, indent=2)+'\n' if not isinstance(value,str) else value)

    def command(self, args, *, input=None, ok=(0,), timeout=45, record=True):
        start=now()
        p=subprocess.run(args, input=input, text=True, capture_output=True, timeout=timeout)
        self.steps += 1
        rec={'sequence':self.steps,'started_utc':start,'ended_utc':now(),
             'command':[str(a).replace(str(ROOT),'$PROJECT') for a in args],
             'stdin':input,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
        if record:
            with (self.out/'commands.jsonl').open('a') as f:
                f.write(json.dumps(rec)+'\n')
        if p.returncode not in ok:
            raise RuntimeError(f'Command failed ({p.returncode}): {args}\n{p.stdout}\n{p.stderr}')
        return p

    def docker(self,*args,**kw):
        return self.command(['docker',*map(str,args)],**kw)

    def network(self, name, subnet=None):
        if name in self.networks: return self.networks[name]
        real=self.prefix+'-'+name
        args=['network','create','--internal','--label',f'{LABEL}={PROJECT}',
              '--label',f'{LABEL}.run={self.run_id}']
        if subnet: args.extend(['--subnet',subnet])
        self.docker(*args,real)
        self.networks[name]=real
        return real

    def node(self,name,*,network=None,ip=None,caps=False,cmd=None,env=None,memory='128m',tmpfs=None,sysctls=None,frr=False):
        real=self.prefix+'-'+name
        args=['run','-d','--name',real,'--hostname',name,
              '--label',f'{LABEL}={PROJECT}','--label',f'{LABEL}.run={self.run_id}',
              '--memory',memory,'--memory-swap',memory,'--cpus','0.5','--pids-limit','96',
              '--network',self.networks[network] if network else 'none']
        if ip: args.extend(['--ip',ip])
        if network: args.extend(['--network-alias',name])
        if caps: args.extend(['--cap-add','NET_ADMIN','--cap-add','NET_RAW'])
        if frr:
            if name not in ['r1','r2','r3'] or self.name!='lab1': raise ValueError('FRR capability restricted to lab1 routers')
            args.extend(['--cap-add','SYS_ADMIN'])
        for key,value in (sysctls or {}).items(): args.extend(['--sysctl',f'{key}={value}'])
        for k,v in (env or {}).items(): args.extend(['-e',f'{k}={v}'])
        for path,size in (tmpfs or {}).items(): args.extend(['--tmpfs',f'{path}:size={size},mode=0755'])
        # No privileged container, host network/PID, Docker-socket mount, or host bind mount.
        args.append(IMAGE)
        args.extend(cmd or [])
        self.docker(*args)
        self.nodes[name]=real
        return real

    def link(self,net,a,b):
        self.network(net)
        for node in [a,b]:
            info=json.loads(self.docker('inspect','--format','{{json .NetworkSettings.Networks}}',self.nodes[node]).stdout)
            if self.networks[net] not in info:
                self.docker('network','connect',self.networks[net],self.nodes[node])

    def ex(self,node,script,*,ok=(0,),timeout=30):
        return self.docker('exec',self.nodes[node],'sh','-eu','-c',script,ok=ok,timeout=timeout)

    def configure_interface(self,node,net,newname,address=None):
        info=json.loads(self.docker('inspect',self.nodes[node]).stdout)[0]
        mac=info['NetworkSettings']['Networks'][self.networks[net]]['MacAddress']
        links=json.loads(self.ex(node,'ip -j link show').stdout)
        old=next(x['ifname'] for x in links if x.get('address')==mac)
        s=f'ip addr flush dev {old}; ip link set dev {old} down; '
        if old!=newname: s+=f'ip link set dev {old} name {newname}; '
        s+=f'ip link set dev {newname} up; ip route del default 2>/dev/null || true; '
        if address: s+=f'ip addr add {address} dev {newname}; '
        self.ex(node,s)
        return newname

    def put(self,node,path,text):
        # Validated fixed target paths; argv and stdin avoid host shell expansion.
        if not re.fullmatch(r'/[A-Za-z0-9_./-]+',path): raise ValueError(path)
        return self.docker('exec','-i',self.nodes[node],'sh','-c',f'cat > {path}',input=text)

    def copy_in(self,node,source,target):
        self.docker('cp',str(source),self.nodes[node]+':'+target)

    def copy_out(self,node,source,rel):
        target=self.out/rel
        target.parent.mkdir(parents=True,exist_ok=True)
        self.docker('cp',self.nodes[node]+':'+source,str(target))
        return target

    def check(self,name,passed,detail):
        item={'name':name,'passed':bool(passed),'observed_utc':now(),'detail':detail}
        self.checks.append(item)
        self.write('checks.json',self.checks)
        print(('PASS ' if passed else 'FAIL ')+name,flush=True)
        if not passed: raise AssertionError(f'{name}: {detail}')

    def wait(self,name,predicate,seconds=30):
        deadline=time.monotonic()+seconds
        last=None
        while time.monotonic()<deadline:
            try:
                last=predicate()
                if last: return last
            except RuntimeError as e:
                last=str(e)
            time.sleep(0.5)
        raise TimeoutError(f'{name} timed out; last observation: {last}')

    def versions(self):
        node=next(iter(self.nodes))
        self.write('versions.txt', self.ex(node,"dpkg-query -W python3 frr nginx dnsmasq isc-dhcp-client iproute2 nftables tcpdump prometheus prometheus-alertmanager; uname -r").stdout)
        img=json.loads(self.docker('image','inspect',IMAGE).stdout)[0]
        self.meta['image_id']=img['Id']
        self.write('metadata.json',self.meta)

    def verify_isolation(self):
        observed=[]
        for name,real in self.nodes.items():
            raw=self.docker('inspect','--format','{{json .HostConfig}}',real).stdout
            c=json.loads(raw)
            safe=not c.get('Privileged') and c.get('NetworkMode')!='host' and not c.get('Binds') and not c.get('PortBindings') and c.get('PidMode')!='host' and c.get('Memory',0)>0
            if 'SYS_ADMIN' in (c.get('CapAdd') or []): safe=safe and self.name=='lab1' and name in ['r1','r2','r3']
            observed.append({'node':name,'safe':safe,'privileged':c.get('Privileged'),'network_mode':c.get('NetworkMode'),'binds':c.get('Binds'),'published_ports':c.get('PortBindings'),'memory_bytes':c.get('Memory'),'cap_add':c.get('CapAdd')})
        for name,real in self.networks.items():
            internal=self.docker('network','inspect','--format','{{.Internal}}',real).stdout.strip()=='true'
            observed.append({'network':name,'safe':internal,'internal':internal})
        self.write('isolation.json',observed)
        self.check('Runtime isolation and resource limits',all(x['safe'] for x in observed),observed)

    def cleanup(self):
        errors=[]
        for kind,names in [('container',self.nodes.values()),('network',self.networks.values())]:
            for name in list(names):
                info=self.docker(kind,'inspect',name,ok=(0,1)).stdout
                if not info: continue
                obj=json.loads(info)[0]
                labels=obj.get('Config',{}).get('Labels',{}) if kind=='container' else obj.get('Labels',{})
                if labels.get(LABEL)!=PROJECT or labels.get(LABEL+'.run')!=self.run_id:
                    raise RuntimeError('Refusing to remove resource with incorrect ownership label: '+name)
                args=['container','rm','-f',name] if kind=='container' else ['network','rm',name]
                p=self.docker(*args,ok=(0,1))
                if p.returncode: errors.append(name+': '+p.stderr)
        self.write('cleanup.json',{'finished_utc':now(),'errors':errors,'kept':False})
        if errors: raise RuntimeError('Cleanup incomplete: '+str(errors))

    def finish(self,error=None):
        original_error=error
        if error is None:
            try: self.verify_isolation()
            except BaseException as e: error=e
        self.meta.update({'ended_utc':now(),'status':'failed' if error else 'passed',
                          'error':str(error) if error else None,'check_count':len(self.checks),
                          'resources_retained':self.keep})
        self.write('metadata.json',self.meta)
        if not self.keep: self.cleanup()
        else: self.write('retained_resources.json',{'nodes':self.nodes,'networks':self.networks})
        print('EVIDENCE '+str(self.out),flush=True)
        if original_error is None and error is not None: raise error

