"""Scrape-time exporter probes a real internal HTTP service; no synthetic success."""
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import time
import urllib.request

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path!='/metrics': self.send_error(404); return
        start=time.monotonic(); success=0
        try:
            with urllib.request.urlopen('http://svc:8080/health',timeout=0.5) as r:
                body=json.loads(r.read())
                success=int(r.status==200 and body.get('service')=='monitored-demo' and body.get('healthy') is True)
        except (OSError,ValueError): pass
        duration=time.monotonic()-start
        body=(f'# HELP lab_probe_success Real HTTP application probe result\n'
              f'# TYPE lab_probe_success gauge\nlab_probe_success{{service="demo"}} {success}\n'
              f'# TYPE lab_probe_duration_seconds gauge\nlab_probe_duration_seconds{{service="demo"}} {duration:.6f}\n').encode()
        self.send_response(200); self.send_header('Content-Type','text/plain; version=0.0.4')
        self.send_header('Content-Length',str(len(body))); self.end_headers(); self.wfile.write(body)

HTTPServer(('0.0.0.0',8080),Handler).serve_forever()
