import sys
import unittest
import hashlib
from pathlib import Path
from unittest.mock import patch


external_folder_path = Path("source")
sys.path.append(str(external_folder_path))
from mailgun import Hasher


class TestHasher(unittest.TestCase):
    test_data: str = "test data"

    @classmethod
    def setUpClass(cls):
        cls.csv_path = "test.csv"
        with open(cls.csv_path, "wb") as writer:
            writer.write(bytes(cls.test_data, "utf-8"))

    @classmethod
    def tearDownClass(cls):
        Path(cls.csv_path).unlink()

    def test_hash_csv(self):
        expected_hash = hashlib.md5(bytes(self.test_data, "utf-8")).hexdigest()
        with patch.object(Hasher, "csv_path", self.csv_path):
            actual_hash = Hasher.hash_csv()
        self.assertEqual(actual_hash, expected_hash)

    def test_hash_csv_empty_file(self):
        expected_hash = hashlib.md5(b"").hexdigest()
        with open(self.csv_path, "wb"):
            pass  # empty file
        with patch.object(Hasher, "csv_path", self.csv_path):
            actual_hash = Hasher.hash_csv()
        self.assertEqual(actual_hash, expected_hash)

    def test_hash_csv_nonexistent_file(self):
        with patch.object(Hasher, "csv_path", "nonexistent.csv"):
            with self.assertRaises(FileNotFoundError):
                Hasher.hash_csv()

    def test_hash_csv_large_file(self):
        data = b"test data" * 1000000
        expected_hash = hashlib.md5(data).hexdigest()
        with open(self.csv_path, "wb") as writer:
            writer.write(data)
        with patch.object(Hasher, "csv_path", self.csv_path):
            actual_hash = Hasher.hash_csv()
        self.assertEqual(actual_hash, expected_hash)

    def test_hash_csv_unicode_file(self):
        data = "test data €".encode("utf-8")
        expected_hash = hashlib.md5(data).hexdigest()
        with open(self.csv_path, "wb") as writer:
            writer.write(data)
        with patch.object(Hasher, "csv_path", self.csv_path):
            actual_hash = Hasher.hash_csv()
        self.assertEqual(actual_hash, expected_hash)


if __name__ == "__main__":
    unittest.main()
