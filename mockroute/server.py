import json
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer

from mockroute.router import Router
from mockroute.auth import Authenticator

class MockRouteHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self._handle("GET")

    def do_POST(self):
        self._handle("POST")

    def _handle(self, method):
        result = self.server.router.resolve(method, self.path)
        if result == "not_found":
            self._send_json(404, {"error": "Not found"})
            return

    def _send_json(self, status, body):
        reply = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(reply)))
        self.end_headers()
        self.wfile.write(reply)

def create_server(storage, host="127.0.0.1", port=9000):
    httpd = ThreadingHTTPServer((host, port), MockRouteHandler)
    httpd.router = Router(storage)
    httpd.authenticator = Authenticator(storage)
    return httpd
