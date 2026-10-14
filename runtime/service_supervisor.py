"""Container startup supervisor; explicitly not systemd or a VM-boot exercise."""
import json
from pathlib import Path
import shutil
import signal
import subprocess
import sys

data=Path('/srv/app')
data.mkdir(parents=True,exist_ok=True)
Path('/srv/pressure').mkdir(parents=True,exist_ok=True)
if not (data/'.commissioned').exists():
    shutil.copy('/lab/nginx-service.conf','/etc/nginx/nginx.conf')
    (data/'data.json').write_text(json.dumps({'asset':'fictional-app-01','version':1,'message':'verified service data'})+'\n')
    (data/'.commissioned').touch()
backend=subprocess.Popen(['python3','-u','/lab/service_backend.py'])
nginx=subprocess.Popen(['nginx','-g','daemon off;'])

def stop(signum,frame):
    if nginx.poll() is None: nginx.send_signal(signal.SIGQUIT)
    if backend.poll() is None: backend.terminate()

signal.signal(signal.SIGTERM,stop)
signal.signal(signal.SIGINT,stop)
code=nginx.wait()
if backend.poll() is None: backend.terminate()
backend.wait(timeout=5)
sys.exit(code)
