from __future__ import annotations

import unittest
from unittest.mock import patch

from stegverse.public_inspection_runtime import PublicInspectionRuntimeError, _runtime_input, run_public_inspection_test


class _FakeRequest:
    @classmethod
    def model_validate(cls, value):
        return dict(value)


class _FakeResult:
    transaction_id = "TX-TEST"
    chain_verified = True
    execution_observation = {"evaluation": {"disposition": "ALLOW"}, "executor_invoked": True}


class _FakeRecord:
    manifest_receipt_id = "MR-ABCDEF0123456789"
    transaction_id = "TX-TEST"


class _FakeReconstruction:
    def model_dump(self, mode="json"):
        return {"chain_verified": True, "consequence_reexecuted": False}


class _FakeRegistry:
    def __init__(self, path=None):
        self.path = path

    def register(self, result):
        return _FakeRecord()

    def evidence_package(self, receipt_id):
        return {"manifest_receipt_id": receipt_id, "chain_verified": True}

    def reconstruct(self, receipt_id):
        return _FakeReconstruction()


class _FakeLedger:
    def __init__(self, path=None):
        self.path = path


def _fake_run(request, executor, **kwargs):
    value = executor()
    assert value["external_side_effect"] is False
    return _FakeResult()


class PublicInspectionRuntimeTests(unittest.TestCase):
    def request(self):
        return {
            "schema_version": "1.0",
            "request_id": "runtime-001",
            "case_profile": "ordinary",
            "input": {
                "steggate_request": {"candidate": {"action": "inspect"}},
                "input_data": {"value": 420},
            },
            "return_projection": "ALL",
            "manifest_labels": True,
            "authority_claim": False,
        }

    def test_requires_steggate_request_for_execution(self):
        request = self.request()
        request["input"].pop("steggate_request")
        with self.assertRaises(PublicInspectionRuntimeError):
            _runtime_input(request)

    @patch("stegverse.public_inspection_runtime._load_stegcore", return_value=(_FakeRegistry, _FakeRequest, _FakeLedger, _fake_run))
    def test_returns_governed_result_and_receipt(self, _mock):
        result = run_public_inspection_test(
            self.request(),
            registry_path="manifest-receipts.jsonl",
            ledger_path="transaction-receipts.jsonl",
        )
        self.assertEqual(result["governance_state"], "ALLOW")
        self.assertEqual(result["manifest_receipt_id"], "MR-ABCDEF0123456789")
        self.assertTrue(result["chain_verified"])
        self.assertTrue(result["local_exact_run_retained"])
        self.assertFalse(result["production_master_records_custody"])
        self.assertFalse(result["external_side_effect"])

    @patch("stegverse.public_inspection_runtime._load_stegcore", return_value=(_FakeRegistry, _FakeRequest, _FakeLedger, _fake_run))
    def test_programmatic_in_memory_run_is_not_claimed_persisted(self, _mock):
        result = run_public_inspection_test(self.request())
        self.assertFalse(result["local_exact_run_retained"])


if __name__ == "__main__":
    unittest.main()
