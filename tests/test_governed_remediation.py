"""A non-ALLOW is remediated only on a returned governance ALLOW (SDK#368)."""
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from scripts.build_mir_sv_exp3_manifest import build_exp3_manifest
from stegverse.governed_remediation import perform_governed_remediation, remediation_candidate
from stegverse.manifest_builder import build_manifest
from stegverse.manifest_state_transition_runtime import RESULT_SCHEMA, derive_execution_request
from stegverse.route_resolution import canonical_sha256
from tests.test_organization_batch_manifest_task_binding import canonical_request, governance_request
from tests.test_governance_return_evidence import CLOSURE, DECIDED, PACKET, _readback, _return, _sha
from stegverse.governance_return_evidence import RETURN_READBACK_SCHEMA

REMEDIATION_TASK = "STEGHEALTH-ECOSYSTEM-FAILURE-REMEDIATION-001"
BOUNDARY = json.loads((Path(__file__).parent / "fixtures" /
                       "stegverse-labs-interlock-intr-boundary.aa2f89ac.json").read_text(encoding="utf-8"))


def _source_profile_deny(request):
    payload = request["canonical_manifest"]["payload"]
    return {
        "schema": "stegverse.sdk.manifest-profile-disposition/v1",
        "state": "DENY", "disposition": "DENY", "terminal": False,
        "automatic_retry_permitted": False,
        "evaluation_boundary": "SDK_MANIFEST_PROFILE_SOURCE_ONLY",
        "authentic_intr_disposition_observed": False,
        "organization_master_records_organization_record_observed": False,
        **{k: request[k] for k in ("request_sha256", "wire_manifest_sha256", "canonical_manifest_sha256",
                                   "graph_id", "processing_capability")},
        "goal_task_id": payload["goal_task_id"], "cosv": payload["cosv"],
        "reason_code": "ECOSYSTEM_DIAGNOSTIC_NONWORKER_DISPATCH_UNWIRED",
        "failed_predicate": "ECOSYSTEM_DIAGNOSTIC_NONWORKER_DISPATCH_UNWIRED",
        "transition_id": "SDK_ECOSYSTEM_DIAGNOSTIC_DISPATCH",
        "repair_owner": "EXISTING_SDK_ECOSYSTEM_DIAGNOSTIC_AND_STEGBROWSER_INTR_OWNERS",
        "retry_condition": "NEW_GOVERNED_ATTEMPT_AFTER_EXISTING_OWNER_DISPATCH_REPAIR",
        "source_disposition_ref": "runtime-state/sdk-manifest-state-transition/dispositions/verified-request.json",
        "evidence_refs": ["StegVerse-Labs/.github:workers/manifest_state_transition_intr_ingress.py"],
    }


def _classification(request, deny, action):
    # The shape StegVerse-Healer's classify_sdk_deny emits (non-authorizing).
    return {
        "schema": "stegverse.healer.sdk-deny-classification/v1",
        "state": "DETECTED",
        "source_disposition_ref": deny["source_disposition_ref"],
        "original_request_sha256": request["request_sha256"],
        "original_request_document_sha256": canonical_sha256(request),
        "original_wire_manifest_sha256": request.get("wire_manifest_sha256")
            or canonical_sha256(request["canonical_manifest"]),
        "reason_code": deny["reason_code"],
        "failed_predicate": deny["failed_predicate"],
        "suggested_action": action,
        "governance_disposition": "NOT_EVALUATED",
        "execution_authority_granted": False,
        "next_action": "AWAIT_ORGANIZATION_GITHUB_GOVERNED_RETURN",
        "authority_effect": "NONE_CLASSIFICATION_ONLY",
    }


def _governance_manifest(candidate):
    payload = canonical_request()
    payload["task_id"] = REMEDIATION_TASK
    request = governance_request(payload)
    request["candidate"] = candidate
    manifest = build_manifest(
        data=payload, source_framework="StegVerse-Labs/StegVerse-Healer",
        source_output_id=payload["request_id"], processor_request=request, process="governance",
        return_depth="result+evidence", created_at="2026-10-12T23:30:00Z",
        declared_intent="Decide the mapped remediation of a retained SDK non-ALLOW.",
        requested_consequence="On ALLOW only, the SDK prepares the mapped RESUBMIT or RE-MANIFEST as a new attempt.",
        publisher_required=False, initiator_class="canonical_task", initiator_ref=REMEDIATION_TASK)
    return manifest


def _governance_result(request, disposition):
    closures, previous = [], None
    for index, transition in enumerate(["INGRESS_ADMITTED", "GOVERNANCE_DISPOSITION"]):
        receipt = f"{index + 1}" * 64
        row = {"transition_id": transition, "state": "RECORDED",
               "required_evidence_validation_status": "PASS", "receipt_sha256": receipt}
        if previous is not None:
            row["predecessor_receipt_sha256"] = previous
        previous = receipt
        closures.append(row)
    return {
        "schema": RESULT_SCHEMA,
        "state": "COMPLETE" if disposition == "ALLOW" else disposition,
        "disposition": disposition, "terminal": disposition != "ALLOW", "communication_terminal": False,
        "canonical_task_id": request["canonical_task_id"], "processing_capability": "governance",
        **{k: request[k] for k in ("route_id", "graph_id", "request_sha256", "wire_manifest_sha256",
                                   "canonical_manifest_sha256")},
        "resolved_ordered_transitions": ["INGRESS_ADMITTED", "GOVERNANCE_DISPOSITION"],
        "transition_closures": closures, "records_authority": "ORGANIZATION_RECORDS_ONLY",
        "publisher_executed": False, "site_propagation_executed": False,
        "failed_predicate": None if disposition == "ALLOW" else "GOVERNANCE_DENIED_REMEDIATION",
        "authority_effect": "NONE_GOVERNANCE_DISPOSITION_ONLY",
    }


def _evidence(**overrides):
    """Ledger readbacks of a returned governance ALLOW, as verify_governance_decision_return reads them."""
    evidence = {"return_readback": {"schema": RETURN_READBACK_SCHEMA, "returns": [_return()]},
                "sender_readback": _readback(_sha("genesis"), _sha("ingress"), CLOSURE),
                "deciding_readback": _readback(_sha("labs-genesis"), DECIDED),
                "request_packet_id": PACKET}
    evidence.update(overrides)
    return evidence


SIX_FIELDS = ("failure_code", "failed_predicate", "required_evidence_or_repair",
              "retry_entrypoint", "owning_existing_goal", "next_attempt")


class GovernedResubmitTests(unittest.TestCase):
    def setUp(self):
        self.manifest = build_exp3_manifest()
        self.request = derive_execution_request(self.manifest, BOUNDARY)
        self.deny = _source_profile_deny(self.request)
        self.classification = _classification(self.request, self.deny, "RESUBMIT")
        self.candidate = remediation_candidate(self.classification, self.request, self.deny)
        self.gov_manifest = _governance_manifest(self.candidate)
        self.gov_request = derive_execution_request(self.gov_manifest, BOUNDARY)

    def _run(self, result, **overrides):
        args = dict(original_manifest=self.manifest, original_request=self.request, non_allow=self.deny,
                    governance_manifest=self.gov_manifest, governance_result=result,
                    organization_boundary=BOUNDARY, decision_return_evidence=_evidence())
        args.update(overrides)
        return perform_governed_remediation(**args)

    def test_governance_allow_resubmits_the_unchanged_manifest_to_the_same_destination(self):
        out = self._run(_governance_result(self.gov_request, "ALLOW"))
        self.assertEqual(out["action"], "RESUBMIT")
        self.assertEqual(out["disposition"], "ALLOW")
        self.assertEqual(out["state"], "GOVERNED_REMEDIATION_HANDED_OFF")
        remediated = out["remediated_request"]
        for key in ("wire_manifest_sha256", "canonical_manifest_sha256", "manifest_declared_destination"):
            self.assertEqual(remediated[key], self.request[key])
        self.assertFalse(out["handoff"]["receiver_contacted"])
        self.assertFalse(out["handoff"]["intr_admission_observed"])
        self.assertEqual(out["original_disposition"]["disposition"], "DENY")

    def test_governance_deny_leaves_the_original_non_allow_standing(self):
        for disposition in ("DENY", "FAIL_CLOSED"):
            out = self._run(_governance_result(self.gov_request, disposition))
            self.assertEqual(out["state"], "REMEDIATION_NOT_AUTHORIZED")
            self.assertEqual(out["disposition"], disposition)
            self.assertIsNone(out["handoff"])
            self.assertIsNone(out["remediated_request"])

    def test_decision_for_another_governance_request_is_refused(self):
        result = _governance_result(self.gov_request, "ALLOW")
        result["request_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "GOVERNANCE_RESULT_BINDING_MISMATCH:request_sha256"):
            self._run(result)

    def test_candidate_bound_to_another_non_allow_is_refused(self):
        other = copy.deepcopy(self.deny)
        other["source_disposition_ref"] = "runtime-state/other.json"
        result = _governance_result(self.gov_request, "ALLOW")
        with self.assertRaisesRegex(ValueError, "REMEDIATION_CANDIDATE_BINDING_MISMATCH"):
            self._run(result, non_allow=other)

    def test_action_switch_in_candidate_is_refused(self):
        switched = copy.deepcopy(self.candidate)
        switched["action"] = "RE_MANIFEST"
        manifest = _governance_manifest(switched)
        result = _governance_result(derive_execution_request(manifest, BOUNDARY), "ALLOW")
        with self.assertRaisesRegex(ValueError, "REMEDIATION_CANDIDATE_BINDING_MISMATCH"):
            self._run(result, governance_manifest=manifest)

    def test_preapproved_classification_is_refused(self):
        forged = copy.deepcopy(self.classification)
        forged["governance_disposition"] = "ALLOW"
        with self.assertRaisesRegex(ValueError, "REMEDIATION_CLASSIFICATION_AUTHORITY_ESCALATION"):
            remediation_candidate(forged, self.request, self.deny)

    def test_classification_for_another_request_is_refused(self):
        forged = copy.deepcopy(self.classification)
        forged["original_request_sha256"] = "f" * 64
        with self.assertRaisesRegex(ValueError, "REMEDIATION_CLASSIFICATION_BINDING_MISMATCH:original_request_sha256"):
            remediation_candidate(forged, self.request, self.deny)

    def test_resubmit_to_a_changed_destination_is_refused(self):
        original = copy.deepcopy(self.request)
        original["manifest_declared_destination"] = {"endpoint": "elsewhere"}
        deny = _source_profile_deny(original)
        classification = _classification(original, deny, "RESUBMIT")
        manifest = _governance_manifest(remediation_candidate(classification, original, deny))
        result = _governance_result(derive_execution_request(manifest, BOUNDARY), "ALLOW")
        with self.assertRaisesRegex(ValueError, "RESUBMIT_IS_NOT_THE_ORIGINAL_SUBMISSION:manifest_declared_destination"):
            self._run(result, original_request=original, non_allow=deny, governance_manifest=manifest)

    def _assert_not_authorized(self, out, predicate):
        self.assertEqual(out["state"], "REMEDIATION_NOT_AUTHORIZED")
        self.assertEqual(out["disposition"], "FAIL_CLOSED")
        self.assertEqual(out["failed_predicate"], predicate)
        for field in SIX_FIELDS:
            self.assertTrue(out[field], field)
        self.assertIsNone(out["handoff"])
        self.assertIsNone(out["remediated_request"])

    def test_governance_deny_is_actionable_without_reauthorizing_original(self):
        out = self._run(_governance_result(self.gov_request, "DENY"),
                        decision_return_evidence=None)
        self.assertEqual(out["state"], "REMEDIATION_NOT_AUTHORIZED")
        self.assertEqual(out["disposition"], "DENY")
        for field in SIX_FIELDS:
            self.assertTrue(out[field], field)
        self.assertEqual(out["authority_effect"], "NONE_MANIFEST_HANDOFF_ONLY")
        self.assertIsNone(out["handoff"])
        self.assertIsNone(out["remediated_request"])
        self.assertEqual(out["original_disposition"]["disposition"], "DENY")

    def test_caller_supplied_allow_without_ledger_readback_grants_nothing(self):
        allow = _governance_result(self.gov_request, "ALLOW")
        for evidence in (None, {}):
            out = self._run(allow, decision_return_evidence=evidence)
            self._assert_not_authorized(out, "GOVERNANCE_RETURN_READBACK_PRESENT")

    def test_deciding_receipt_absent_from_its_ledger_grants_nothing(self):
        evidence = _evidence(deciding_readback=_readback(_sha("labs-genesis")))
        out = self._run(_governance_result(self.gov_request, "ALLOW"), decision_return_evidence=evidence)
        self._assert_not_authorized(out, "DECIDING_ORGANIZATION_RECEIPT_READ_BACK")

    def test_returned_deny_contradicting_an_allow_result_grants_nothing(self):
        evidence = _evidence(return_readback={"schema": RETURN_READBACK_SCHEMA,
                                              "returns": [_return(governance_disposition="DENY")]})
        out = self._run(_governance_result(self.gov_request, "ALLOW"), decision_return_evidence=evidence)
        self._assert_not_authorized(out, "READ_BACK_GOVERNANCE_DECISION_IS_ALLOW")

    def test_replayed_return_grants_nothing(self):
        evidence = _evidence(return_readback={"schema": RETURN_READBACK_SCHEMA, "returns": [_return(), _return()]})
        out = self._run(_governance_result(self.gov_request, "ALLOW"), decision_return_evidence=evidence)
        self.assertEqual(out["state"], "REMEDIATION_NOT_AUTHORIZED")
        self.assertIsNone(out["handoff"])

    def test_verified_return_is_carried_on_the_attempt(self):
        out = self._run(_governance_result(self.gov_request, "ALLOW"))
        acceptance = out["decision_return_acceptance"]
        self.assertEqual(acceptance["disposition"], "ALLOW")
        self.assertEqual(acceptance["deciding_organization_receipt_sha256"], DECIDED)
        self.assertEqual(acceptance["authority_effect"], "NONE_VERIFICATION_ONLY")

    def test_an_allow_is_not_a_remediation_input(self):
        allowed = copy.deepcopy(self.deny)
        allowed["disposition"] = "ALLOW"
        with self.assertRaisesRegex(ValueError, "REMEDIATION_REQUIRES_NON_ALLOW"):
            remediation_candidate(self.classification, self.request, allowed)


class GovernedTerminalReentryTests(unittest.TestCase):
    def test_terminal_fail_closed_resubmits_only_on_a_governed_reentry(self):
        manifest = build_exp3_manifest()
        request = derive_execution_request(manifest, BOUNDARY)
        failed = _source_profile_deny(request)
        failed.update({"state": "FAIL_CLOSED", "disposition": "FAIL_CLOSED", "terminal": True,
                       "evaluation_boundary": "SDK_ADMITTED_DIAGNOSTIC_CONSUMER_LOCAL",
                       "retry_condition": "SEPARATELY_GOVERNED_FUTURE_REENTRY_ONLY"})
        classification = _classification(request, failed, "RESUBMIT")
        gov_manifest = _governance_manifest(remediation_candidate(classification, request, failed))
        gov_request = derive_execution_request(gov_manifest, BOUNDARY)
        denied = perform_governed_remediation(manifest, request, failed, gov_manifest,
                                              _governance_result(gov_request, "DENY"), BOUNDARY)
        self.assertIsNone(denied["handoff"])
        allowed = perform_governed_remediation(manifest, request, failed, gov_manifest,
                                               _governance_result(gov_request, "ALLOW"), BOUNDARY,
                                               decision_return_evidence=_evidence())
        self.assertEqual(allowed["action"], "RESUBMIT")
        self.assertEqual(allowed["disposition"], "ALLOW")
        self.assertEqual(allowed["original_disposition"]["disposition"], "FAIL_CLOSED")


class GovernedReManifestTests(unittest.TestCase):
    def test_envelope_deny_is_re_manifested_through_the_builder_to_the_same_destination(self):
        from tests.test_mir_sv_exp3_manifest import MIRSVExp3ManifestTests
        manifest = build_exp3_manifest()
        historical, denial = MIRSVExp3ManifestTests._boundary_resolved_hash_deny(None, manifest, BOUNDARY)
        classification = _classification(historical, denial, "RE_MANIFEST")
        gov_manifest = _governance_manifest(remediation_candidate(classification, historical, denial))
        gov_request = derive_execution_request(gov_manifest, BOUNDARY)
        out = perform_governed_remediation(manifest, historical, denial, gov_manifest,
                                           _governance_result(gov_request, "ALLOW"), BOUNDARY,
                                               decision_return_evidence=_evidence())
        self.assertEqual(out["action"], "RE_MANIFEST")
        self.assertEqual(out["disposition"], "ALLOW")
        repaired = out["remediated_request"]
        self.assertEqual(repaired, derive_execution_request(manifest, BOUNDARY))
        self.assertNotEqual(repaired["request_sha256"], historical["request_sha256"])
        self.assertEqual(repaired["manifest_declared_destination"], historical["manifest_declared_destination"])
        self.assertEqual(manifest, build_exp3_manifest())



class RemediationGovernanceManifestTests(unittest.TestCase):
    """The classification is decided on the existing governance route; nothing it cannot evidence is claimed."""

    def setUp(self):
        from stegverse.governed_remediation import remediation_governance_manifest
        self.build = remediation_governance_manifest
        self.manifest = build_exp3_manifest()
        self.request = derive_execution_request(self.manifest, BOUNDARY)
        self.deny = _source_profile_deny(self.request)
        self.classification = _classification(self.request, self.deny, "RESUBMIT")
        self.preflight = {"schema": "stegverse.organization.remediation-return-preflight/v1",
                          "state": "AWAIT_AUTHENTIC_ORGANIZATION_GOVERNANCE", "disposition": "FAIL_CLOSED",
                          "proposed_action": "RESUBMIT", "original_request_sha256": self.request["request_sha256"],
                          "authority_effect": "NONE_PREFLIGHT_ONLY", "execution_authority_granted": False}

    def _manifest(self, **overrides):
        args = dict(preflight=self.preflight, evidence_refs=["sha256:" + "c" * 64], organization_boundary=BOUNDARY)
        args.update(overrides)
        return self.build(self.classification, self.request, self.deny, **args)

    def test_the_remediation_is_decided_on_the_existing_governance_route(self):
        governance = derive_execution_request(self._manifest(), BOUNDARY)
        self.assertEqual(governance["processing_capability"], "governance")
        self.assertEqual(governance["route_id"], "stegverse.route.canonical-governed.v1")

    def test_no_authority_is_claimed_that_the_evidence_does_not_carry(self):
        request = self._manifest()["extensions"]["stegverse_governance_request"]
        self.assertEqual(request["candidate"], remediation_candidate(self.classification, self.request, self.deny))
        self.assertFalse(request["execution"]["actor_authority_current"])
        self.assertFalse(request["execution"]["delegation_current"])
        self.assertFalse(request["permission_present"])
        self.assertTrue(request["approval"]["required"])
        self.assertIn("authenticated_current_grant", request["signal"]["missing_inputs"])

    def test_one_classification_is_one_governance_request(self):
        self.assertEqual(self._manifest(), self._manifest())

    def test_a_preflight_for_another_action_or_request_is_refused(self):
        for override in ({"proposed_action": "RE_MANIFEST"}, {"original_request_sha256": "f" * 64},
                         {"execution_authority_granted": True}, {"schema": "other"}):
            with self.assertRaisesRegex(ValueError, "REMEDIATION_PREFLIGHT_NOT_BOUND_TO_THIS_CANDIDATE"):
                self._manifest(preflight={**self.preflight, **override})

    def test_lineage_evidence_is_required(self):
        with self.assertRaisesRegex(ValueError, "REMEDIATION_LINEAGE_EVIDENCE_REQUIRED"):
            self._manifest(evidence_refs=[])

    def test_a_preapproved_classification_never_reaches_governance(self):
        forged = dict(self.classification, execution_authority_granted=True)
        with self.assertRaisesRegex(ValueError, "REMEDIATION_CLASSIFICATION_AUTHORITY_ESCALATION"):
            self.build(forged, self.request, self.deny, preflight=self.preflight,
                       evidence_refs=["sha256:" + "c" * 64], organization_boundary=BOUNDARY)
if __name__ == "__main__":
    unittest.main()
