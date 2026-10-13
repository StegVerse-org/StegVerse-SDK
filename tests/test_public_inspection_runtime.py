from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from stegverse.production_validation_runtime import (
    PublicInspectionRuntimeError,
    _runtime_input,
    run_public_inspection_test,
)

SIX_FIELDS = (
    "failure_code",
    "failed_predicate",
    "required_evidence_or_repair",
    "retry_entrypoint",
    "owning_existing_goal",
    "next_attempt",
)


def ledger_sink(calls):
    def sink(route_manifest_id, event):
        calls.append((route_manifest_id, event))
        return {"custody_status": "RECORDED", "event": {"route_receipt_id": "ORG-R-1", "event_hash": "eh"}}
    return sink

PROV = {
    "lane_class": "PRODUCTION_VALIDATION",
    "routing_surface": "CANONICAL_PRODUCTION",
    "containment": "PRODUCTION_ROUTE_BOUNDED_CONSEQUENCE",
    "sandbox_required": False,
    "sandbox_tier": "NONE",
    "origin_surface": "StegVerse-org/StegVerse-SDK:public-inspection",
    "external_consequence_enabled": False,
}


class Req(dict):
    @classmethod
    def model_validate(cls, value):
        return cls(value)

    def model_dump(self, mode="json", exclude_none=False):
        return dict(self)


class Result:
    transaction_id = "TX-ROUTE"
    chain_verified = True
    execution_observation = {"evaluation": {"disposition": "ALLOW", "candidate_hash": "h"}, "executor_invoked": True}


class ManifestedModel:
    @classmethod
    def model_validate(cls, body):
        assert body["transaction_id"] == "TX-ROUTE"
        return Result()


class Ledger:
    pass


STEGCORE_CALLS = []


def run_manifested_transaction(request, executor, **kwargs):
    STEGCORE_CALLS.append((request, kwargs))
    consequence = executor()
    assert consequence["external_side_effect"] is False
    assert kwargs["transaction_id"] == "TX-ROUTE"
    return Result()


IN_PROCESS_STEGCORE = (run_manifested_transaction, Ledger)


class Record:
    manifest_receipt_id = "MR-" + "A" * 64
    transaction_id = "TX-ROUTE"


class Registry:
    def __init__(self, path=None):
        pass

    def register(self, result):
        return Record()

    def evidence_package(self, rid):
        return {
            "manifest_receipt_id": rid,
            "transaction_id": "TX-ROUTE",
            "manifest": {
                "manifest_hash": "b" * 64,
                "metadata": {
                    "governance_request": {"candidate": {"action": "inspect"}},
                    "execution_provenance": dict(PROV),
                },
            },
            "receipt_chain_head": "c" * 64,
            "canonical_runtime_identity": "runtime",
            "locator_grants_authority": False,
        }


class Eval:
    disposition = "ALLOW"
    candidate_hash = "h"


def build(record, evidence):
    return {
        "schema": "stegverse.master-records.manifest-receipt-submission.v1",
        "evidence_package": evidence,
        "custody_requested": True,
        "authority_requested": False,
    }


def make_manifest(**kwargs):
    return {
        "route_manifest_id": "MF-" + "B" * 64,
        "transaction_id": "TX-ROUTE",
        "execution_provenance": dict(PROV),
        "receipt_bindings": [],
        "receipt_chain_head": None,
        "route": [],
    }


class RouteError(RuntimeError):
    pass


class Carrier:
    def __init__(self, manifest, sink):
        self.manifest = manifest
        self.sink = sink

    def run(self, payload, handlers):
        receipt = self.sink(
            {
                "transaction_id": "TX-ROUTE",
                "sequence": 0,
                "event_type": "MANIFEST_ESTABLISHED",
                "checkpoint_id": "sdk:entry",
                "module": "stegverse-sdk",
                "route_index": 0,
                "execution_provenance": dict(PROV),
                "details": {},
                "authority_granted": False,
            }
        )
        if receipt.get("custody_status") != "RECORDED":
            raise RouteError("not recorded")
        handlers["stegcore"](self.manifest, payload)
        return {
            "route_manifest_id": self.manifest["route_manifest_id"],
            "transaction_id": "TX-ROUTE",
            "route_transition_count": 10,
            "receipt_chain_head": "head",
            "route_manifest": self.manifest,
            "completed": True,
        }


class Tests(unittest.TestCase):
    def request(self):
        return {
            "schema_version": "1.0",
            "request_id": "runtime-001",
            "case_profile": "ordinary",
            "execution_provenance": dict(PROV),
            "input": {"steggate_request": {"candidate": {"action": "inspect"}}, "input_data": {"value": 420}},
            "return_projection": "ALL",
            "manifest_labels": True,
            "authority_claim": False,
        }

    def test_requires_steggate(self):
        request = self.request()
        request["input"].pop("steggate_request")
        with self.assertRaises(PublicInspectionRuntimeError):
            _runtime_input(request)

    def test_without_organization_ledger_sink_returns_six_field_refusal_not_master_records(self):
        result = run_public_inspection_test(
            self.request(),
            master_records_url="https://records.example",
            master_records_token="token",
            stegcore_url="https://stegcore.example",
        )
        self.assertEqual(result["disposition"], "FAIL_CLOSED")
        self.assertEqual(result["failure_code"], "ORGANIZATION_LEDGER_SINK_NOT_BOUND")
        for field in SIX_FIELDS:
            self.assertTrue(result[field], field)
        self.assertFalse(result["consequence_committed"])

    @patch("stegverse.production_validation_runtime._load_stegcore_transaction_runtime", return_value=IN_PROCESS_STEGCORE)
    @patch("stegverse.production_validation_runtime.requests.get")
    @patch("stegverse.production_validation_runtime.requests.post")
    @patch("stegverse.production_validation_runtime._load_route_carrier", return_value=(Carrier, RouteError, make_manifest, lambda: []))
    @patch("stegverse.production_validation_runtime._load_stegcore", return_value=(build, Registry, Req, lambda req: Eval(), ManifestedModel))
    def test_route_closes_on_organization_ledger_without_master_records(self, _core, _carrier, post, get, _runtime):
        calls = []
        STEGCORE_CALLS.clear()
        with patch.dict("os.environ", {}, clear=True):
            result = run_public_inspection_test(
                self.request(),
                organization_ledger_sink=ledger_sink(calls),
                stegcore_url="https://stegcore.example",
            )
        self.assertEqual("PRODUCTION_LANE_VALIDATION_TEST", result["runtime_mode"])
        # StegCore runs in process: the URL is never contacted and nothing is awaited.
        self.assertEqual(
            "IN_PROCESS:stegcore.transaction_lifecycle.run_manifested_transaction",
            result["stegcore_execution_surface"],
        )
        self.assertIs(result["external_machine_awaited"], False)
        self.assertNotIn("stegcore_service_url", result)
        get.assert_not_called()
        self.assertEqual(1, len(STEGCORE_CALLS))
        self.assertEqual(STEGCORE_CALLS[0][1]["metadata"]["route_manifest_id"], "MF-" + "B" * 64)
        self.assertEqual("stegverse:steggate:canonical:three-layer:v1", result["stegcore_runtime_identity"])
        self.assertTrue(result["transaction_identity_continuous"])
        self.assertEqual(10, result["route_transition_count"])
        self.assertEqual(calls[0][0], "MF-" + "B" * 64)
        self.assertEqual(result["organization_ledger_closure"]["status"], "RECORDED")
        self.assertEqual(result["master_records_recording"]["status"], "NOT_CONFIGURED")
        self.assertIs(result["master_records_recording"]["gates_completion"], False)
        # No HTTP at all: no StegCore service and nothing sent to Master Records.
        post.assert_not_called()

    @patch("stegverse.production_validation_runtime._load_stegcore_transaction_runtime", return_value=IN_PROCESS_STEGCORE)
    @patch("stegverse.production_validation_runtime.requests.post")
    @patch("stegverse.production_validation_runtime._load_route_carrier", return_value=(Carrier, RouteError, make_manifest, lambda: []))
    @patch("stegverse.production_validation_runtime._load_stegcore", return_value=(build, Registry, Req, lambda req: Eval(), ManifestedModel))
    def test_master_records_recording_failure_does_not_gate_the_run(self, _core, _carrier, post, _runtime):
        unavailable = Mock(status_code=503, text="receiver unavailable")
        post.side_effect = [unavailable]
        result = run_public_inspection_test(
            self.request(),
            organization_ledger_sink=ledger_sink([]),
            master_records_url="https://records.example",
            master_records_token="token",
            stegcore_url="https://stegcore.example",
        )
        self.assertEqual("ALLOW", result["governance_state"])
        self.assertEqual("RECORDED", result["ecosystem_commit_status"])
        recording = result["master_records_recording"]
        self.assertEqual(recording["status"], "NOT_RECORDED")
        self.assertIs(recording["gates_completion"], False)
        for field in SIX_FIELDS:
            self.assertTrue(recording[field], field)
        self.assertEqual(recording["owning_existing_goal"], "LLMA-DECLARED-PATH-CONFORMANCE-368")

        post.side_effect = [Mock(status_code=201, json=lambda: {"record_status": "RECORDED"})]
        recorded = run_public_inspection_test(
            self.request(),
            organization_ledger_sink=ledger_sink([]),
            master_records_url="https://records.example",
            master_records_token="token",
            stegcore_url="https://stegcore.example",
        )
        self.assertEqual(recorded["master_records_recording"]["status"], "RECORDED")
        self.assertEqual(recorded["master_records_organization_record_status"], "RECORDED")

    def test_demo_rejected_from_production_lane(self):
        request = self.request()
        request["execution_provenance"] = {
            "lane_class": "ENCLOSED_DEMO_TEST",
            "routing_surface": "DEMO_TEST_REPOSITORY",
            "containment": "DEMO_REPOSITORY_CONTAINED",
            "sandbox_required": True,
            "external_consequence_enabled": False,
        }
        with self.assertRaises(PublicInspectionRuntimeError):
            run_public_inspection_test(request, organization_ledger_sink=ledger_sink([]), stegcore_url="z")


if __name__ == "__main__":
    unittest.main()
