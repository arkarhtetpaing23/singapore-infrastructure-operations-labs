#!/usr/bin/env python3
"""Authorized entry point; build or run only this isolated project."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from labcore import ROOT, IMAGE, Lab

def build():
    out=ROOT/'.local'
    out.mkdir(exist_ok=True)
    p=subprocess.run(['docker','build','--pull','-t',IMAGE,str(ROOT)],text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    (out/'image-build.log').write_text(p.stdout)
    print(p.stdout[-12000:])
    if p.returncode: raise SystemExit(p.returncode)
    info=subprocess.check_output(['docker','image','inspect',IMAGE],text=True)
    obj=json.loads(info)[0]
    (out/'image.json').write_text(json.dumps({'id':obj['Id'],'created':obj['Created'],'repo_digests':obj.get('RepoDigests',[])},indent=2)+'\n')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=['build','lab1','lab2','lab3'])
    p.add_argument('--actor',choices=['assistant','candidate'],default='assistant')
    p.add_argument('--keep',action='store_true',help='Retain only this run\'s containers/networks for manual practice')
    a=p.parse_args()
    if a.action=='build': return build()
    mod=__import__(a.action)
    lab=Lab(a.action,a.actor,a.keep)
    error=None
    try:
        mod.run(lab)
    except BaseException as e:
        error=e
        print('ERROR '+str(e),flush=True)
        raise
    finally:
        lab.finish(error)

if __name__=='__main__': main()
