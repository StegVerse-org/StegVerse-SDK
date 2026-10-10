"""Master Records reconstruction is evidence for admission, never a gate (SDK#368)."""
from __future__ import annotations

import copy
import unittest

from stegverse.organization_record_names import ORGANIZATION_RECORD_OBSERVED_FIELD
from stegverse.manifest_state_transition_runtime import (
    MASTER_RECORDS_EVIDENCE_SCHEMA,
    RESULT_SCHEMA,
    admit_runtime_result,
    derive_execution_request,
    validate_runtime_result,
)
from tests.test_organization_batch_manifest_task_binding import TASK_ID, fixture as governance_manifest
from tests.test_universal_manifest_state_transition_runtime import complete_result, manifest as worker_manifest


def _strip_master_records(result: dict) -> dict:
    stripped = copy.deepcopy(result)
    for row in stripped["transition_closures"]:
        row.pop("reconstruction_status", None)
        row.pop("reconstructed_receipt_sha256", None)
    stripped.pop("replay_status", None)
    stripped.pop("reconstruction_status", None)
    return stripped


def _governance_deny(request: dict) -> dict:
    closures = []
    previous = None
    for index, transition in enumerate(["INGRESS_ADMITTED", "GOVERNANCE_DISPOSITION"]):
        receipt = f"{index + 1}" * 64
        row = {
            "transition_id": transition,
            "state": "RECORDED",
            "required_evidence_validation_status": "PASS",
            "receipt_sha256": receipt,
        }
        if previous is not None:
            row["predecessor_receipt_sha256"] = previous
        previous = receipt
        closures.append(row)
    return {
        "schema": RESULT_SCHEMA,
        "state": "DENY",
        "disposition": "DENY",
        "terminal": True,
        "communication_terminal": False,
        "canonical_task_id": TASK_ID,
        "processing_capability": "governance",
        "route_id": request["route_id"],
        "graph_id": request["graph_id"],
        "request_sha256": request["request_sha256"],
        "wire_manifest_sha256": request["wire_manifest_sha256"],
        "canonical_manifest_sha256": request["canonical_manifest_sha256"],
        "resolved_ordered_transitions": ["INGRESS_ADMITTED", "GOVERNANCE_DISPOSITION"],
        "transition_closures": closures,
        "records_authority": "ORGANIZATION_RECORDS_ONLY",
        "publisher_executed": False,
        "site_propagation_executed": False,
        "authority_effect": "NONE_GOVERNANCE_DISPOSITION_ONLY",
    }


class GenericResultAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.source = worker_manifest()
        self.request = derive_execution_request(self.source)
        self.result = complete_result(self.request)

    def test_admission_succeeds_without_master_records_pass(self):
        checked = admit_runtime_result(self.source, self.request, _strip_master_records(self.result))
        self.assertEqual(checked["state"], "COMPLETE")
        evidence = checked["master_records_reconstruction_evidence"]
        self.assertEqual(evidence["schema"], MASTER_RECORDS_EVIDENCE_SCHEMA)
        self.assertEqual(evidence["evidence_status"], "NOT_PROVIDED")
        self.assertIs(evidence["gates_admission"], False)
        self.assertEqual(evidence["authority_effect"], "NONE_EVIDENCE_ONLY")

    def test_request_closes_on_organization_ledger_not_master_records(self):
        self.assertEqual(self.request["transition_receipt_authority"], "ORGANIZATION_LEDGER")
        self.assertEqual(self.request["downstream_batch_receipt_recorder"], "MASTER_RECORDS")
        self.assertIs(self.request["downstream_batch_receipt_recording_gates_transition"], False)
        # The receiver pinned at dd7a334 accepts the organization-ledger value.
        self.assertEqual(self.request["custody_replay_reconstruction_authority"], "ORGANIZATION_LEDGER")
        evidence = validate_runtime_result(self.result, self.request)["master_records_reconstruction_evidence"]
        self.assertNotIn("authority", evidence)
        self.assertEqual(evidence["recorder_role"], "DOWNSTREAM_RELEASED_BATCH_RECEIPT_RECORDING")

    def test_master_records_pass_is_reported(self):
        evidence = validate_runtime_result(self.result, self.request)["master_records_reconstruction_evidence"]
        self.assertEqual(evidence["evidence_status"], "PASS")
        self.assertTrue(all(row["evidence_status"] == "PASS" for row in evidence["closures"]))

    def test_master_records_fail_is_reported_and_does_not_gate(self):
        failed = copy.deepcopy(self.result)
        failed["transition_closures"][0]["reconstructed_receipt_sha256"] = "f" * 64
        failed["transition_closures"][1]["reconstruction_status"] = "FAIL"
        failed["replay_status"] = "FAIL"
        failed["reconstruction_status"] = "FAIL"
        checked = validate_runtime_result(failed, self.request)
        self.assertEqual(checked["state"], "COMPLETE")
        evidence = checked["master_records_reconstruction_evidence"]
        self.assertEqual(evidence["evidence_status"], "FAIL")
        self.assertEqual(evidence["closures"][0]["evidence_status"], "FAIL")
        self.assertIs(evidence["closures"][0]["reconstructed_receipt_matches"], False)
        self.assertEqual(evidence["closures"][1]["evidence_status"], "FAIL")
        self.assertEqual(evidence["replay_status"], "FAIL")
        self.assertIs(evidence["gates_admission"], False)

    def test_manifest_declared_reconstruction_is_validated_as_evidence(self):
        self.assertIs(
            validate_runtime_result(self.result, self.request)["master_records_reconstruction_evidence"]["declared_by_manifest"],
            False,
        )
        declared = copy.deepcopy(self.request)
        declared["state_graph"]["terminal_requirements"]["reconstruction_status"] = "PASS"
        evidence = validate_runtime_result(self.result, declared)["master_records_reconstruction_evidence"]
        self.assertIs(evidence["declared_by_manifest"], True)
        self.assertIs(evidence["declared_requirements_satisfied"], True)
        failed = copy.deepcopy(self.result)
        failed["transition_closures"][2]["reconstruction_status"] = "FAIL"
        checked = validate_runtime_result(failed, declared)
        self.assertEqual(checked["state"], "COMPLETE")
        self.assertIs(checked["master_records_reconstruction_evidence"]["declared_requirements_satisfied"], False)

    def test_result_cannot_supply_its_own_evidence_verdict(self):
        forged = _strip_master_records(self.result)
        forged["master_records_reconstruction_evidence"] = {"evidence_status": "PASS", "gates_admission": True}
        evidence = validate_runtime_result(forged, self.request)["master_records_reconstruction_evidence"]
        self.assertEqual(evidence["evidence_status"], "NOT_PROVIDED")
        self.assertIs(evidence["gates_admission"], False)

    def test_other_refusals_unchanged(self):
        base = _strip_master_records(self.result)
        cases = []

        def case(pattern, mutate):
            broken = copy.deepcopy(base)
            mutate(broken)
            cases.append((pattern, broken))

        case("ORGANIZATION_LEDGER_CLOSURE_REQUIRED:.*:state",
             lambda r: r["transition_closures"][0].update(state="PENDING"))
        case("ORGANIZATION_LEDGER_CLOSURE_REQUIRED:.*:required_evidence_validation_status",
             lambda r: r["transition_closures"][1].update(required_evidence_validation_status="FAIL"))
        case("ORGANIZATION_LEDGER_TRANSITION_RECEIPT_REQUIRED",
             lambda r: r["transition_closures"][0].pop("receipt_sha256"))
        case("ORGANIZATION_LEDGER_IMMEDIATE_PREDECESSOR_MISMATCH",
             lambda r: r["transition_closures"][2].update(predecessor_receipt_sha256="0" * 64))
        case("ORGANIZATION_LEDGER_TRANSITION_ORDER_MISMATCH",
             lambda r: r["transition_closures"][0].update(transition_id="OTHER"))
        case("ORGANIZATION_LEDGER_CLOSURE_COUNT_MISMATCH",
             lambda r: r["transition_closures"].pop())
        case("UNIVERSAL_INTR_RESULT_BINDING_MISMATCH:canonical_manifest_sha256",
             lambda r: r.update(canonical_manifest_sha256="0" * 64))
        case("UNIVERSAL_INTR_RUNTIME_NOT_COMPLETE", lambda r: r.update(state="FAILED"))
        case("TERMINAL_RECORDS_ONLY_REQUIRED", lambda r: r["terminal_state"].update(records_only=False))
        case("TERMINAL_CONTINUED_AUTHORITY_FALSE_REQUIRED",
             lambda r: r["terminal_state"].update(continued_authority=True))
        case("MANIFEST_RECEIPT_ID_REQUIRED", lambda r: r.pop("manifest_receipt_id"))
        for pattern, broken in cases:
            with self.subTest(pattern=pattern):
                with self.assertRaisesRegex(ValueError, pattern):
                    validate_runtime_result(broken, self.request)


class GovernanceResultAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.request = derive_execution_request(governance_manifest())
        self.result = _governance_deny(self.request)

    def test_organization_records_result_admitted_without_master_records(self):
        checked = validate_runtime_result(self.result, self.request)
        self.assertEqual(checked["disposition"], "DENY")
        evidence = checked["master_records_reconstruction_evidence"]
        self.assertEqual(evidence["evidence_status"], "NOT_PROVIDED")
        self.assertIs(evidence["gates_admission"], False)

    def test_master_records_fail_does_not_gate_governance_result(self):
        failed = copy.deepcopy(self.result)
        failed["transition_closures"][1]["reconstruction_status"] = "FAIL"
        failed["transition_closures"][1]["reconstructed_receipt_sha256"] = "e" * 64
        checked = validate_runtime_result(failed, self.request)
        self.assertEqual(checked["disposition"], "DENY")
        self.assertEqual(checked["master_records_reconstruction_evidence"]["evidence_status"], "FAIL")

    def test_governance_refusals_unchanged(self):
        cases = {
            "GOVERNANCE_RESULT_ORGANIZATION_RECORDS_REQUIRED": lambda r: r.update(records_authority="MASTER_RECORDS"),
            "GOVERNANCE_RESULT_MASTER_RECORDS_NOT_IN_GOVERNANCE_PATH": lambda r: r.update({ORGANIZATION_RECORD_OBSERVED_FIELD: True}),
            "GOVERNANCE_RESULT_BINDING_MISMATCH:request_sha256": lambda r: r.update(request_sha256="0" * 64),
            "GOVERNANCE_RESULT_EXTERNAL_MUTATION_ESCALATION": lambda r: r.update(publisher_executed=True),
            "GOVERNANCE_RESULT_STATE_MISMATCH": lambda r: r.update(state="COMPLETE"),
            "ORGANIZATION_LEDGER_IMMEDIATE_PREDECESSOR_MISMATCH":
                lambda r: r["transition_closures"][1].update(predecessor_receipt_sha256="0" * 64),
            "ORGANIZATION_LEDGER_TRANSITION_RECEIPT_REQUIRED": lambda r: r["transition_closures"][1].pop("receipt_sha256"),
            "ORGANIZATION_BATCH_NONALLOW_MUST_NOT_EXECUTE_ACTION": lambda r: r.update(manifest_directed_action={}),
        }
        for pattern, mutate in cases.items():
            broken = copy.deepcopy(self.result)
            mutate(broken)
            with self.subTest(pattern=pattern):
                with self.assertRaisesRegex(ValueError, pattern):
                    validate_runtime_result(broken, self.request)


if __name__ == "__main__":
    unittest.main()
