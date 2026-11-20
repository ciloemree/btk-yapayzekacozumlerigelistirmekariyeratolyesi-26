"""Sadece standart kütüphane gerektirir: python -m unittest discover -s testler -v"""
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "kodlar"))

class TestApproval(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        os.environ["CAMPUS_DB"] = str(Path(self.tmp.name) / "test.sqlite3")
        import d7_store
        d7_store.DB_PATH = Path(os.environ["CAMPUS_DB"])
        self.store = d7_store
        self.params = {"request_id": "REQ-1", "ad_soyad": "Test", "esya": "Kulaklık", "konum": "Kütüphane"}

    def tearDown(self):
        self.tmp.cleanup()

    def test_without_approval_fails(self):
        result = self.store.create_ticket(**self.params, approval_token="wrong")
        self.assertFalse(result["ok"])
        self.assertIsNone(self.store.get_ticket("REQ-1"))

    def test_approved_then_idempotent(self):
        token = self.store.issue_approval("REQ-1")
        first = self.store.create_ticket(**self.params, approval_token=token)
        second = self.store.create_ticket(**self.params, approval_token=token)
        self.assertTrue(first["ok"])
        self.assertFalse(first["duplicate"])
        self.assertTrue(second["duplicate"])

    def test_token_cannot_approve_other_request(self):
        token = self.store.issue_approval("REQ-2")
        result = self.store.create_ticket(**self.params, approval_token=token)
        self.assertFalse(result["ok"])

if __name__ == "__main__":
    unittest.main()
