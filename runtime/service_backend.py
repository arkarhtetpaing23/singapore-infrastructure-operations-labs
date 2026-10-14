"""Small real HTTP service with a bounded journal write path for ENOSPC practice."""
import datetime as dt
import errno
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path

class Handler(BaseHTTPRequestHandler):
    def reply(self,code,body):
        data=json.dumps(body).encode()
        self.send_response(code)
        self.send_header('Content-Type','application/json')
        self.send_header('Content-Length',str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path=='/health': self.reply(200,{'service':'operations-demo','read_health':'ok'})
        else: self.reply(404,{'error':'unknown endpoint'})

    def do_POST(self):
        if self.path!='/events': return self.reply(404,{'error':'unknown endpoint'})
        size=int(self.headers.get('Content-Length','0'))
        if not 0<size<=1024: return self.reply(400,{'error':'invalid body size'})
        try: event=json.loads(self.rfile.read(size))
        except ValueError: return self.reply(400,{'error':'invalid JSON'})
        item={'timestamp_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'event':event}
        try:
            with Path('/srv/pressure/events.jsonl').open('a') as f:
                f.write(json.dumps(item)+'\n'); f.flush()
        except OSError as e:
            print(json.dumps({'write_error':e.errno,'message':str(e)}),flush=True)
            return self.reply(507 if e.errno==errno.ENOSPC else 500,{'error':'journal write failed','errno':e.errno})
        self.reply(201,{'stored':True})

ThreadingHTTPServer(('127.0.0.1',8080),Handler).serve_forever()
