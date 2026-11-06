import tempfile
import unittest
from pathlib import Path

from mockroute.storage import Storage
from mockroute.auth import Authenticator

USERS = {
    "developer@company.com": {
        "password": "secureToken123",
        "profile": {"uid": 101, "name": "Jane Doe", "role": "Engineer"},
        "account_status": "active",
    },
    "suspended@company.com": {
        "password": "secureToken123",
        "profile": {"uid": 102, "name": "John Smith", "role": "Guest"},
        "account_status": "locked",
    },
}


class TestAuthenticator(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        storage = Storage(Path(self._tmp.name))
        storage.write_json("data/users.json", USERS)
        self.auth = Authenticator(storage)

    def tearDown(self):
        self._tmp.cleanup()

    def test_valid_credentials_return_200_and_profile(self):
        status, body = self.auth.authenticate("developer@company.com", "secureToken123")
        self.assertEqual(status, 200)
        self.assertEqual(body, {"profile": USERS["developer@company.com"]["profile"]})

    def test_wrong_password_returns_401(self):
        status, body = self.auth.authenticate("developer@company.com", "badPassword")
        self.assertEqual(status, 401)
        self.assertEqual(body, {"error": "Invalid client credentials supplied"})

    def test_unknown_email_returns_the_same_401(self):
        status, body = self.auth.authenticate("nobody@company.com", "whatever")
        self.assertEqual(status, 401)
        self.assertEqual(body, {"error": "Invalid client credentials supplied"})

    def test_locked_account_returns_403(self):
        status, body = self.auth.authenticate("suspended@company.com", "secureToken123")
        self.assertEqual(status, 403)
        self.assertEqual(body, {"status": "Access Denied", "reason": "Account Suspended"})

    def test_locked_account_with_wrong_password_returns_401(self):
        status, body = self.auth.authenticate("suspended@company.com", "badPassword")
        self.assertEqual(status, 401)


if __name__ == "__main__":
    unittest.main()
