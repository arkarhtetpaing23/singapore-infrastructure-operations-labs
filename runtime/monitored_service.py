from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path!='/health': self.send_error(404); return
        body=json.dumps({'service':'monitored-demo','healthy':True}).encode()
        self.send_response(200); self.send_header('Content-Type','application/json')
        self.send_header('Content-Length',str(len(body))); self.end_headers(); self.wfile.write(body)

HTTPServer(('0.0.0.0',8080),Handler).serve_forever()
