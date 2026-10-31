import tempfile
import unittest
from pathlib import Path
import os

from mockroute.storage import Storage, StorageError


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

    def test_read_missing_file_raises_storage_error(self):
        with self.assertRaises(StorageError):
            self.storage.read_json("data/missing.json")

    def test_read_invalid_json_raises_storage_error(self):
        bad = self.base / "bad.json"
        bad.write_text('{"name": "Jane",}')      # trailing comma = invalid JSON
        with self.assertRaises(StorageError):
            self.storage.read_json("bad.json")

    def test_write_json_leaves_no_temp_file(self):
        self.storage.write_json("data/test.json", {"a": 1})
        leftovers = list((self.base / "data").glob("*.tmp"))
        self.assertEqual(leftovers, [])

    def test_read_directory_raises_storage_error(self):
        (self.base / "data").mkdir()
        with self.assertRaises(StorageError):
            self.storage.read_json("data")

    def test_failed_write_keeps_original_file(self):
        self.storage.write_json("data/users.json", {"name": "john"})

        with self.assertRaises(StorageError):
            self.storage.write_json("data/users.json", {"bad": Path("x")})

        self.assertEqual(
            self.storage.read_json("data/users.json"),
            {"name": "john"},
        )

    def test_init_works_with_relative_base_dir(self):
        original = Path.cwd()
        os.chdir(self.base)
        try:
            storage = Storage("workspace")
            storage.init_workspace()
            self.assertTrue((self.base / "workspace" / "config.json").exists())
            self.assertFalse((self.base / "workspace" / "workspace").exists())
        finally:
            os.chdir(original)

if __name__ == "__main__":
    unittest.main()
