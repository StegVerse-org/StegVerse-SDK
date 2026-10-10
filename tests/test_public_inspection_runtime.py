from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from stegverse.production_validation_runtime import (
    PublicInspectionRuntimeError,
    _preflight_stegcore,
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

    @patch("stegverse.production_validation_runtime.requests.get")
    def test_preflight_requires_deployed_manifested_stegcore_surface(self, get):
        get.return_value = Mock(
            status_code=200,
            json=lambda: {
                "runtime_identity": "stegverse:steggate:canonical:three-layer:v1",
                "manifested_validation_endpoint": "/v1/manifested-validation",
            },
        )
        identity = _preflight_stegcore("https://stegcore.example")
        self.assertEqual("/v1/manifested-validation", identity["manifested_validation_endpoint"])

    def _stegcore_response(self):
        return Mock(
            status_code=200,
            json=lambda: {
                "transaction_id": "TX-ROUTE",
                "service_runtime_identity": "stegverse:steggate:canonical:three-layer:v1",
                "service_external_side_effect": False,
            },
        )

    @patch("stegverse.production_validation_runtime.requests.post")
    @patch("stegverse.production_validation_runtime._preflight_stegcore", return_value={"runtime_identity": "stegverse:steggate:canonical:three-layer:v1", "manifested_validation_endpoint": "/v1/manifested-validation"})
    @patch("stegverse.production_validation_runtime._load_route_carrier", return_value=(Carrier, RouteError, make_manifest, lambda: []))
    @patch("stegverse.production_validation_runtime._load_stegcore", return_value=(build, Registry, Req, lambda req: Eval(), ManifestedModel))
    def test_route_closes_on_organization_ledger_without_master_records(self, _core, _carrier, _core_preflight, post):
        post.return_value = self._stegcore_response()
        calls = []
        with patch.dict("os.environ", {}, clear=True):
            result = run_public_inspection_test(
                self.request(),
                organization_ledger_sink=ledger_sink(calls),
                stegcore_url="https://stegcore.example",
            )
        self.assertEqual("PRODUCTION_LANE_VALIDATION_TEST", result["runtime_mode"])
        self.assertEqual("https://stegcore.example", result["stegcore_service_url"])
        self.assertTrue(result["transaction_identity_continuous"])
        self.assertEqual(10, result["route_transition_count"])
        self.assertEqual(calls[0][0], "MF-" + "B" * 64)
        self.assertEqual(result["organization_ledger_closure"]["status"], "RECORDED")
        self.assertEqual(result["master_records_recording"]["status"], "NOT_CONFIGURED")
        self.assertIs(result["master_records_recording"]["gates_completion"], False)
        # Only the deployed StegCore call: nothing was sent to Master Records.
        self.assertEqual(1, post.call_count)
        self.assertTrue(post.call_args.args[0].endswith("/v1/manifested-validation"))

    @patch("stegverse.production_validation_runtime.requests.post")
    @patch("stegverse.production_validation_runtime._preflight_stegcore", return_value={"runtime_identity": "stegverse:steggate:canonical:three-layer:v1", "manifested_validation_endpoint": "/v1/manifested-validation"})
    @patch("stegverse.production_validation_runtime._load_route_carrier", return_value=(Carrier, RouteError, make_manifest, lambda: []))
    @patch("stegverse.production_validation_runtime._load_stegcore", return_value=(build, Registry, Req, lambda req: Eval(), ManifestedModel))
    def test_master_records_recording_failure_does_not_gate_the_run(self, _core, _carrier, _core_preflight, post):
        unavailable = Mock(status_code=503, text="receiver unavailable")
        post.side_effect = [self._stegcore_response(), unavailable]
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

        post.side_effect = [self._stegcore_response(), Mock(status_code=201, json=lambda: {"record_status": "RECORDED"})]
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
