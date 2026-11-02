import tempfile
import unittest
from pathlib import Path
import io
from contextlib import redirect_stderr

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

    def test_init_reports_storage_error(self):
        blocker = Path(self._tmp.name) / "blocker"
        blocker.write_text("I am a file, not a folder")

        err = io.StringIO()
        with redirect_stderr(err):
            code = main(["init"], base_dir=blocker)

        self.assertEqual(code, 1)
        self.assertIn("Error:", err.getvalue())


if __name__ == "__main__":
    unittest.main()
