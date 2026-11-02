import tempfile
import unittest
from pathlib import Path

from mockroute.cli import main


class TestCli(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.base = Path(self._tmp.name) / "workspace"

    def tearDown(self):
        self._tmp.cleanup()

    def test_init_creates_workspace(self):
        code = main(["init"], base_dir=self.base)
        self.assertEqual(code, 0)
        self.assertTrue((self.base / "config.json").exists())
        self.assertTrue((self.base / "data" / "users.json").exists())


if __name__ == "__main__":
    unittest.main()
