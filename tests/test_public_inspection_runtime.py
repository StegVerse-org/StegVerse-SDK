from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from stegverse.public_inspection_runtime import PublicInspectionRuntimeError, _preflight_master_records, _runtime_input, reconstruct_manifest_receipt, replay_manifest_receipt, run_public_inspection_test


class _FakeRequest(dict):
    @classmethod
    def model_validate(cls, value):
        return cls(value)

    def model_dump(self, mode="json", exclude_none=False):
        return dict(self)


class _FakeEval:
    disposition = "ALLOW"
    candidate_hash = "candidate-hash"


class _FakeResult:
    transaction_id = "TX-TEST"
    chain_verified = True
    execution_observation = {"evaluation": {"disposition": "ALLOW", "candidate_hash": "candidate-hash"}, "executor_invoked": True}


class _FakeRecord:
    manifest_receipt_id = "MR-" + "A" * 64
    transaction_id = "TX-TEST"


class _FakeRegistry:
    seen_paths = []
    def __init__(self, path=None):
        self.path = path
        self.__class__.seen_paths.append(path)
    def register(self, result):
        return _FakeRecord()
    def evidence_package(self, receipt_id):
        return {"manifest_receipt_id": receipt_id, "transaction_id": "TX-TEST", "manifest": {"manifest_hash": "b" * 64, "metadata": {"governance_request": {"candidate": {"action": "inspect"}}}}, "receipt_chain_head": "c" * 64, "canonical_runtime_identity": "runtime", "locator_grants_authority": False}


class _FakeLedger:
    seen_paths = []
    def __init__(self, path=None):
        self.path = path
        self.__class__.seen_paths.append(path)


def _fake_run(request, executor, **kwargs):
    assert executor()["external_side_effect"] is False
    return _FakeResult()


def _fake_build(record, evidence):
    return {"schema": "stegverse.master-records.manifest-receipt-submission.v1", "evidence_package": evidence, "custody_requested": True, "authority_requested": False}


class PublicInspectionRuntimeTests(unittest.TestCase):
    def setUp(self):
        _FakeRegistry.seen_paths.clear()
        _FakeLedger.seen_paths.clear()

    def request(self):
        return {"schema_version": "1.0", "request_id": "runtime-001", "case_profile": "ordinary", "input": {"steggate_request": {"candidate": {"action": "inspect"}}, "input_data": {"value": 420}}, "return_projection": "ALL", "manifest_labels": True, "authority_claim": False}

    def test_requires_steggate_request_for_execution(self):
        request = self.request()
        request["input"].pop("steggate_request")
        with self.assertRaises(PublicInspectionRuntimeError):
            _runtime_input(request)

    @patch("stegverse.public_inspection_runtime.requests.get")
    def test_preflight_requires_admitted_exact_run_route(self, get):
        get.return_value = Mock(status_code=404)
        _preflight_master_records("https://records.example", "token")
        self.assertIn("/api/master-records/manifest-receipts/MR-", get.call_args.args[0])
        self.assertEqual(get.call_args.kwargs["headers"]["Authorization"], "Bearer token")
        get.return_value = Mock(status_code=401)
        with self.assertRaises(PublicInspectionRuntimeError):
            _preflight_master_records("https://records.example", "bad")

    @patch("stegverse.public_inspection_runtime._retain_in_master_records", return_value={"custody_status": "RECORDED"})
    @patch("stegverse.public_inspection_runtime._preflight_master_records")
    @patch("stegverse.public_inspection_runtime._load_stegcore", return_value=(_fake_build, _FakeRegistry, _FakeRequest, lambda req: _FakeEval(), _FakeLedger, _fake_run))
    def test_run_requires_and_confirms_master_records(self, _load, _preflight, _retain):
        result = run_public_inspection_test(self.request(), master_records_url="https://records.example", master_records_token="test-token")
        self.assertEqual(result["governance_state"], "ALLOW")
        self.assertEqual(result["master_records_custody_status"], "RECORDED")
        self.assertEqual(result["ecosystem_commit_status"], "RECORDED")
        self.assertFalse(result["external_side_effect"])
        self.assertEqual(_FakeRegistry.seen_paths, [None])
        self.assertEqual(_FakeLedger.seen_paths, [None])

    def test_run_without_master_records_configuration_fails_before_governance(self):
        with patch.dict("os.environ", {}, clear=True):
            with patch("stegverse.public_inspection_runtime._load_stegcore") as load:
                with self.assertRaises(PublicInspectionRuntimeError):
                    run_public_inspection_test(self.request())
                load.assert_not_called()

    @patch("stegverse.public_inspection_runtime._retain_in_master_records", side_effect=PublicInspectionRuntimeError("custody failed"))
    @patch("stegverse.public_inspection_runtime._preflight_master_records")
    @patch("stegverse.public_inspection_runtime._load_stegcore", return_value=(_fake_build, _FakeRegistry, _FakeRequest, lambda req: _FakeEval(), _FakeLedger, _fake_run))
    def test_custody_failure_never_returns_success(self, _load, _preflight, _retain):
        with self.assertRaises(PublicInspectionRuntimeError):
            run_public_inspection_test(self.request(), master_records_url="https://records.example", master_records_token="test-token")

    @patch("stegverse.public_inspection_runtime._get_json")
    @patch("stegverse.public_inspection_runtime._load_stegcore", return_value=(_fake_build, _FakeRegistry, _FakeRequest, lambda req: _FakeEval(), _FakeLedger, _fake_run))
    def test_replay_is_read_only_and_deterministic(self, _load, get_json):
        get_json.return_value = {"evidence_package": {"manifest": {"metadata": {"governance_request": {"candidate": {"action": "inspect"}}}}, "execution_observation": {"evaluation": {"disposition": "ALLOW", "candidate_hash": "candidate-hash"}}}}
        result = replay_manifest_receipt("MR-" + "A" * 64, master_records_url="https://records.example", master_records_token="test-token")
        self.assertTrue(result["deterministic_disposition_match"])
        self.assertFalse(result["consequence_reexecuted"])
        self.assertFalse(result["original_record_mutated"])
        self.assertTrue(result["operation_is_read_only"])

    @patch("stegverse.public_inspection_runtime._get_json", return_value={"consequence_reexecuted": False, "reconstruction_grants_authority": False})
    def test_reconstruction_comes_from_master_records_read_only(self, _get):
        result = reconstruct_manifest_receipt("MR-" + "A" * 64, master_records_url="https://records.example", master_records_token="test-token")
        self.assertFalse(result["consequence_reexecuted"])
        self.assertTrue(result["operation_is_read_only"])


if __name__ == "__main__":
    unittest.main()
