import tempfile
import unittest
from pathlib import Path

from mockroute.storage import Storage
from mockroute.router import Router


class TestRouter(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.storage = Storage(Path(self._tmp.name))
        self.storage.add_route("/api/v1/auth", "POST")
        self.storage.add_route("/health", "GET")
        self.router = Router(self.storage)

    def tearDown(self):
        self._tmp.cleanup()

    def test_registered_route_is_found(self):
        self.assertEqual(self.router.resolve("POST", "/api/v1/auth"), "found")

    def test_wrong_method_is_reported(self):
        self.assertEqual(self.router.resolve("GET", "/api/v1/auth"), "wrong_method")

    def test_unknown_path_is_not_found(self):
        self.assertEqual(self.router.resolve("GET", "/nothing"), "not_found")

    def test_method_is_case_insensitive(self):
        self.assertEqual(self.router.resolve("post", "/api/v1/auth"), "found")

    def test_route_added_later_is_seen(self):
        self.storage.add_route("/api/v1/auth", "GET")
        self.assertEqual(self.router.resolve("GET", "/api/v1/auth"), "found")


if __name__ == "__main__":
    unittest.main()
