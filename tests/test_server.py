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

    def test_unknown_path_returns_404(self):
        req = urllib.request.Request(
            f"http://127.0.0.1:{self.port}/api/v1/nothing",
            data=b"{}",
            method="POST",
        )
        with self.assertRaises(urllib.error.HTTPError) as cm:
            urllib.request.urlopen(req)
        self.assertEqual(cm.exception.code, 404)


if __name__ == "__main__":
    unittest.main()
