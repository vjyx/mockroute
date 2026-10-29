import tempfile
import unittest
from pathlib import Path

from mockroute.storage import Storage


class TestStorage(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.base = Path(self._tmp.name)
        self.storage = Storage(base_dir=self.base)

    def tearDown(self):
        self._tmp.cleanup()

    def test_init_creates_config_file(self):
        self.storage.init_workspace()
        self.assertTrue((self.base / "config.json").exists())

    def test_init_creates_users_file(self):
        self.storage.init_workspace()
        self.assertTrue((self.base / "data" / "users.json").exists())

    def test_init_twice_keeps_existing_data(self):
        self.storage.init_workspace()
        users = self.base / "data" / "users.json"
        users.write_text('{"a": 1}')          # simulate the user editing the file

        self.storage.init_workspace()         # run init a second time

        self.assertEqual(users.read_text(), '{"a": 1}')

    def test_write_then_read_json(self):
        data = {"email": "a@b.com", "uid": 101}
        self.storage.write_json("data/test.json", data)
        result = self.storage.read_json("data/test.json")
        self.assertEqual(result, data)


if __name__ == "__main__":
    unittest.main()
