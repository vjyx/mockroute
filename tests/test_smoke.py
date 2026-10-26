import unittest

class TestSmoke(unittest.TestCase):
    def test_package_imports(self):
        import mockroute
        self.assertIsNotNone(mockroute)

if __name__ == "__main__":
    unittest.main()
