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


if __name__ == "__main__":
    unittest.main()
