import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

from mockroute.storage import Storage
from mockroute.server import create_server


class TestServer(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        storage = Storage(Path(self._tmp.name))
        storage.add_route("/api/v1/auth", "POST")

        self.httpd = create_server(storage, port=0)
        self.port = self.httpd.server_address[1]
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        self.thread.join()
        self._tmp.cleanup()

    def request(self, method, path, payload=None, raw=None):
        if raw is not None:
            data = raw
        elif payload is not None:
            data = json.dumps(payload).encode("utf-8")
        else:
            data = None
        req = urllib.request.Request(
            f"http://127.0.0.1:{self.port}{path}",
            data=data,
            method=method,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req) as resp:
                return resp.status, json.loads(resp.read())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read())

    def test_unknown_path_returns_404(self):
        status, body = self.request("POST", "/api/v1/nothing", {"a": 1})
        self.assertEqual(status, 404)

    def test_wrong_method_returns_405(self):
        status, body = self.request("GET", "/api/v1/auth")
        self.assertEqual(status, 405)


if __name__ == "__main__":
    unittest.main()
