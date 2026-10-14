#!/usr/bin/env python3
"""Inspect, execute in, or clean only a retained run owned by this project."""
import argparse
import datetime as dt
import json
from pathlib import Path
import subprocess
from labcore import ROOT, LABEL, PROJECT

def call(args): return subprocess.run(args,text=True,capture_output=True)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=['list','exec','cleanup'])
    p.add_argument('--run',required=True,help='Relative evidence run directory, e.g. evidence/runs/lab1-...')
    p.add_argument('--node')
    p.add_argument('--command')
    p.add_argument('--actor',choices=['assistant','candidate','manual'],default='manual',help='Declared operator only; not identity or mastery authentication')
    a=p.parse_args()
    run=(ROOT/a.run).resolve()
    if not run.is_relative_to(ROOT/'evidence/runs'): raise SystemExit('Run must be inside this project evidence/runs')
    resources=json.loads((run/'retained_resources.json').read_text())
    meta=json.loads((run/'metadata.json').read_text())
    rid=meta['run_id']
    def owned(kind,name):
        r=call(['docker',kind,'inspect',name])
        if r.returncode:
            if 'no such' in r.stderr.lower(): return False
            raise SystemExit('Docker inspection failed; resource absence is not established: '+r.stderr.strip())
        o=json.loads(r.stdout)[0]
        labels=o.get('Config',{}).get('Labels',{}) if kind=='container' else o.get('Labels',{})
        if labels.get(LABEL)!=PROJECT or labels.get(LABEL+'.run')!=rid:
            raise SystemExit('Ownership check failed; refusing operation')
        return True
    if a.action=='list':
        for node,name in resources['nodes'].items(): print(node,name,'present' if owned('container',name) else 'absent')
        return
    if a.action=='exec':
        if a.node not in resources['nodes'] or not a.command: raise SystemExit('--node and --command required')
        name=resources['nodes'][a.node]
        if not owned('container',name): raise SystemExit('Container absent; create a new --keep run')
        r=call(['docker','exec',name,'sh','-c',a.command])
        record={'timestamp_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'operator':a.actor,'operator_authentication':'Declared only; not identity-authenticated','node':a.node,'command':a.command,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr}
        with (run/'manual-practice.jsonl').open('a') as f: f.write(json.dumps(record)+'\n')
        print(r.stdout,end=''); print(r.stderr,end='')
        raise SystemExit(r.returncode)
    errors=[]
    for kind,mapping in [('container',resources['nodes']),('network',resources['networks'])]:
        for name in mapping.values():
            if not owned(kind,name): continue
            args=['docker','container','rm','-f',name] if kind=='container' else ['docker','network','rm',name]
            r=call(args)
            if r.returncode: errors.append(r.stderr)
    (run/'manual-cleanup.json').write_text(json.dumps({'timestamp_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'errors':errors},indent=2)+'\n')
    if errors: raise SystemExit(str(errors))
    print('Retained run cleaned; source files and evidence preserved.')

if __name__=='__main__': main()
