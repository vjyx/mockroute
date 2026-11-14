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
        if result == "wrong_method":
            self._send_json(405, {"error": "Method not allowed"})
            return

        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            self._send_json(400, {"error": "Request body must be valid JSON"})
            return

        if not isinstance(data, dict):
            self._send_json(400, {"error": "Request body must be a JSON object"})
            return
        email = data.get("email")
        password = data.get("password")
        if email is None or password is None:
            self._send_json(400, {"error": "email and password are required"})
            return
        status, body = self.server.authenticator.authenticate(email, password)
        self._send_json(status, body)

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
