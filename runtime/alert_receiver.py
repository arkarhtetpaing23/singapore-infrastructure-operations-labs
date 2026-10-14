"""Local-only webhook receiver retaining actual Alertmanager deliveries."""
import datetime as dt
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from pathlib import Path

PATH=Path('/tmp/deliveries.jsonl')
class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path!='/alerts': self.send_error(404); return
        size=int(self.headers.get('Content-Length','0'))
        if not 0<size<100000: self.send_error(413); return
        try: payload=json.loads(self.rfile.read(size))
        except ValueError: self.send_error(400); return
        record={'received_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'payload':payload}
        with PATH.open('a') as f: f.write(json.dumps(record)+'\n')
        print(json.dumps(record),flush=True)
        self.send_response(200); self.end_headers(); self.wfile.write(b'accepted')

    def do_GET(self):
        if self.path!='/events': self.send_error(404); return
        events=[json.loads(x) for x in PATH.read_text().splitlines()] if PATH.exists() else []
        body=json.dumps(events).encode()
        self.send_response(200); self.send_header('Content-Type','application/json')
        self.send_header('Content-Length',str(len(body))); self.end_headers(); self.wfile.write(body)

HTTPServer(('0.0.0.0',8080),Handler).serve_forever()
