"""Every non-ALLOW carries its remediation fork (NODE_INGRESS_SETTLED_SPECIFICATION §8).

The Manifest Builder builds a remediation manifest bound to the exact request and
non-ALLOW; it declares its own path (stegverse.route.governed-remediation.v1 /
remediation) and is handed off, never transported, classified or decided here.
The original disposition stands unchanged. Owner contract: StegVerse-org/.github#98
comment 6134521366; SDK#493.
"""
from __future__ import annotations

import copy
import unittest

from scripts.build_mir_sv_exp3_manifest import build_exp3_manifest
from stegverse.manifest_state_transition_runtime import admit_runtime_result, derive_execution_request
from stegverse.remediation_fork import (
    REMEDIATION_CAPABILITY, REQUEST_EXTENSION, STEGHEALER, build_remediation_fork, fork_request,
    remediation_route, validate_remediation_fork_request,
)
from stegverse.route_resolution import GOVERNED_REMEDIATION_ROUTE_ID, canonical_sha256
from tests.test_governed_remediation import BOUNDARY, _source_profile_deny

SIX_FIELDS = ("failure_code", "failed_predicate", "required_evidence_or_repair",
              "retry_entrypoint", "owning_existing_goal", "next_attempt")


class RemediationForkTests(unittest.TestCase):
    def setUp(self):
        self.manifest = build_exp3_manifest()
        self.request = derive_execution_request(self.manifest, BOUNDARY)
        self.deny = _source_profile_deny(self.request)

    def _admit(self, result):
        return admit_runtime_result(self.manifest, self.request, result, BOUNDARY)

    def test_a_deny_keeps_every_field_and_carries_its_fork(self):
        out = self._admit(self.deny)
        self.assertEqual({k: v for k, v in out.items() if k != "remediation_fork"}, self.deny)
        fork = out["remediation_fork"]
        self.assertEqual(fork["route_id"], GOVERNED_REMEDIATION_ROUTE_ID)
        self.assertEqual(fork["original_request_sha256"], self.request["request_sha256"])
        self.assertEqual(fork["non_allow_sha256"], canonical_sha256(self.deny))
        self.assertTrue(fork["original_disposition_unchanged"])
        self.assertEqual(fork["authority_effect"], "NONE_MANIFEST_HANDOFF_ONLY")

    def test_the_fork_declares_its_own_path_and_binds_the_original(self):
        fork = self._admit(self.deny)["remediation_fork"]
        manifest = fork["remediation_manifest"]
        self.assertEqual(manifest["processing"], {"capability": REMEDIATION_CAPABILITY,
                                                  "route_id": GOVERNED_REMEDIATION_ROUTE_ID})
        request = manifest["extensions"][REQUEST_EXTENSION]
        for key in ("request_sha256", "wire_manifest_sha256", "canonical_manifest_sha256"):
            self.assertEqual(request["original_" + key], self.request[key])
        self.assertEqual(request["original_destination"], self.request["manifest_declared_destination"])
        self.assertEqual(request["non_allow"], self.deny)

    def test_the_fork_is_handed_off_to_the_same_destination_and_never_transported(self):
        fork = self._admit(self.deny)["remediation_fork"]
        remediation = derive_execution_request(fork["remediation_manifest"], BOUNDARY)
        self.assertEqual(remediation["manifest_declared_destination"], self.request["manifest_declared_destination"])
        self.assertEqual(remediation["processing_capability"], REMEDIATION_CAPABILITY)
        self.assertFalse(remediation["state_graph"]["classification_grants_authority"])
        self.assertFalse(fork["handoff"]["receiver_contacted"])
        self.assertFalse(fork["handoff"]["intr_admission_observed"])

    def test_a_terminal_fail_closed_forks_too(self):
        failed = copy.deepcopy(self.deny)
        failed.update({"state": "FAIL_CLOSED", "disposition": "FAIL_CLOSED", "terminal": True,
                       "evaluation_boundary": "SDK_ADMITTED_DIAGNOSTIC_CONSUMER_LOCAL",
                       "retry_condition": "SEPARATELY_GOVERNED_FUTURE_REENTRY_ONLY"})
        out = self._admit(failed)
        self.assertEqual(out["disposition"], "FAIL_CLOSED")
        self.assertEqual(out["remediation_fork"]["remediation_manifest"]["extensions"][REQUEST_EXTENSION]
                         ["non_allow"]["disposition"], "FAIL_CLOSED")

    def test_an_allow_carries_no_fork(self):
        allowed = copy.deepcopy(self.deny)
        allowed.update({"state": "COMPLETE", "disposition": "ALLOW"})
        self.assertIsNone(build_remediation_fork(self.request, allowed, BOUNDARY))

    def test_one_non_allow_is_one_fork(self):
        first = self._admit(self.deny)["remediation_fork"]
        second = self._admit(copy.deepcopy(self.deny))["remediation_fork"]
        self.assertEqual(first["remediation_request_sha256"], second["remediation_request_sha256"])
        other = copy.deepcopy(self.deny)
        other["source_disposition_ref"] = "runtime-state/other.json"
        third = self._admit(other)["remediation_fork"]
        self.assertNotEqual(first["remediation_request_sha256"], third["remediation_request_sha256"])

    def test_a_remediation_non_allow_does_not_fork_again(self):
        fork = self._admit(self.deny)["remediation_fork"]
        remediation = derive_execution_request(fork["remediation_manifest"], BOUNDARY)
        denied = copy.deepcopy(self.deny)
        denied.update({k: remediation[k] for k in ("request_sha256", "wire_manifest_sha256",
                                                   "canonical_manifest_sha256", "graph_id", "processing_capability")})
        self.assertIsNone(build_remediation_fork(remediation, denied, BOUNDARY))

    def test_a_forged_or_misbound_fork_request_is_refused(self):
        request = fork_request(self.request, self.deny)
        forged = copy.deepcopy(request)
        forged["non_allow"]["failed_predicate"] = "SOMETHING_ELSE"
        with self.assertRaisesRegex(ValueError, "REMEDIATION_FORK_NON_ALLOW_DIGEST_MISMATCH"):
            validate_remediation_fork_request(forged)
        other = copy.deepcopy(self.deny)
        other["request_sha256"] = "f" * 64
        with self.assertRaisesRegex(ValueError, "REMEDIATION_FORK_NON_ALLOW_IS_FOR_ANOTHER_REQUEST"):
            fork_request(self.request, other)
        allowed = copy.deepcopy(request)
        allowed["non_allow"]["disposition"] = "ALLOW"
        allowed["non_allow_sha256"] = canonical_sha256(allowed["non_allow"])
        with self.assertRaisesRegex(ValueError, "REMEDIATION_FORK_REQUIRES_NON_ALLOW"):
            validate_remediation_fork_request(allowed)
        extra = dict(request, healer_classification={"suggested_action": "RESUBMIT"})
        with self.assertRaisesRegex(ValueError, "unknown remediation request fields"):
            validate_remediation_fork_request(extra)

    def test_a_pre_323_request_forks_on_the_digest_of_its_canonical_manifest(self):
        # Requests derived before SDK #323 carry no wire_manifest_sha256 field.
        legacy = {k: v for k, v in self.request.items() if k != "wire_manifest_sha256"}
        deny = dict(self.deny, request_sha256=legacy["request_sha256"])
        request = fork_request(legacy, deny)
        self.assertEqual(request["original_wire_manifest_sha256"], canonical_sha256(legacy["canonical_manifest"]))
        self.assertEqual(validate_remediation_fork_request(request), request)
        forged = copy.deepcopy(request)
        forged["original_wire_manifest_sha256"] = "f" * 64
        with self.assertRaisesRegex(ValueError, "REMEDIATION_FORK_ORIGINAL_REQUEST_MISMATCH:wire_manifest_sha256"):
            validate_remediation_fork_request(forged)
        bare = {k: v for k, v in legacy.items() if k != "canonical_manifest"}
        with self.assertRaisesRegex(ValueError, "REMEDIATION_REQUEST_WIRE_IDENTITY_REQUIRED"):
            fork_request(bare, deny)

    def test_a_fork_that_cannot_be_built_is_a_six_field_refusal_and_the_deny_stands(self):
        from unittest.mock import patch
        with patch("stegverse.manifest_state_transition_runtime.validate_runtime_result", return_value=self.deny):
            out = admit_runtime_result(self.manifest, {"processing_capability": "governance"}, self.deny, BOUNDARY)
        self.assertEqual({k: v for k, v in out.items() if k != "remediation_fork"}, self.deny)
        refusal = out["remediation_fork"]
        self.assertEqual(refusal["disposition"], "FAIL_CLOSED")
        for field in SIX_FIELDS:
            self.assertTrue(refusal[field], field)
        self.assertIsNone(refusal["handoff"])

class RemediationRouteTests(unittest.TestCase):
    """The route: where remediation was recognized, the manifested path, the direct leg to StegHealer."""

    def setUp(self):
        self.manifest = build_exp3_manifest()
        self.request = derive_execution_request(self.manifest, BOUNDARY)
        self.deny = _source_profile_deny(self.request)
        self.destination = self.request["manifest_declared_destination"]

    def _route(self, non_allow, destination=None):
        return remediation_route(non_allow, original_route_id=self.request["route_id"],
                                 original_processing_capability=self.request["processing_capability"],
                                 original_destination=destination or self.destination)

    def test_recognized_in_the_sdk_enters_at_the_manifested_destination_then_goes_direct(self):
        route = self._route(self.deny)
        self.assertEqual(route["recognized_at"]["node"], "SDK")
        self.assertEqual(route["manifested_path"]["route_id"], self.request["route_id"])
        self.assertEqual(route["entry_organization"], self.destination["organization"])
        self.assertEqual(route["direct_route_to_steghealer"][-1]["to"], STEGHEALER["service_id"])
        self.assertEqual(route["direct_route_to_steghealer"][0],
                         {"from": "SDK", "to": self.destination["organization"], "crossing": "INTERLOCK_INTR_INGRESS"})
        self.assertFalse(route["follows_remaining_manifested_path"])

    def test_recognized_by_an_organization_enters_there(self):
        other = dict(self.deny, evaluation_boundary="ORGANIZATION_INGRESS", organization="StegVerse-org")
        route = self._route(other)
        self.assertEqual(route["recognized_at"], {"node": "ORGANIZATION", "organization": "StegVerse-org",
                                                  "evaluation_boundary": "ORGANIZATION_INGRESS"})
        self.assertEqual(route["entry_organization"], "StegVerse-org")
        self.assertEqual([h["crossing"] for h in route["direct_route_to_steghealer"]],
                         ["INTERLOCK_INTR_EGRESS", "INTERLOCK_INTR_INGRESS", "INTERNAL_ENDPOINT"])

    def test_recognized_inside_steghealers_organization_is_one_internal_leg(self):
        labs = dict(self.deny, evaluation_boundary="ORGANIZATION_INGRESS", organization=STEGHEALER["organization"])
        route = self._route(labs)
        self.assertEqual(route["direct_route_to_steghealer"],
                         [{"from": STEGHEALER["organization"], "to": STEGHEALER["service_id"],
                           "crossing": "INTERNAL_ENDPOINT"}])

    def test_no_organization_crossing_bypasses_intr(self):
        from stegverse.remediation_fork import _assert_intr_on_every_crossing
        crossings = [h["crossing"] for h in self._route(self.deny)["direct_route_to_steghealer"]]
        if self.destination["organization"] != STEGHEALER["organization"]:
            self.assertIn("INTERLOCK_INTR_EGRESS", crossings)
        for bad in ([{"from": "A", "to": "B", "crossing": "DIRECT"}],
                    [{"from": "A", "to": "B", "crossing": "INTERLOCK_INTR_EGRESS"}],
                    [{"from": "A", "to": "B", "crossing": "INTERLOCK_INTR_INGRESS"}]):
            with self.assertRaisesRegex(ValueError, "REMEDIATION_ROUTE_"):
                _assert_intr_on_every_crossing(bad)

    def test_the_lane_carries_the_whole_original_request_and_it_must_be_the_bound_one(self):
        request = fork_request(self.request, self.deny)
        self.assertEqual(request["original_request"], self.request)
        swapped = copy.deepcopy(request)
        swapped["original_request"]["request_sha256"] = "f" * 64
        with self.assertRaisesRegex(ValueError, "REMEDIATION_FORK_ORIGINAL_REQUEST_MISMATCH:request_sha256"):
            validate_remediation_fork_request(swapped)
        moved = copy.deepcopy(request)
        moved["original_request"]["manifest_declared_destination"] = {"organization": "Elsewhere"}
        with self.assertRaisesRegex(ValueError, "REMEDIATION_FORK_ORIGINAL_REQUEST_MISMATCH:manifest_declared_destination"):
            validate_remediation_fork_request(moved)

    def test_a_redirected_route_is_refused(self):
        request = fork_request(self.request, self.deny)
        redirected = copy.deepcopy(request)
        redirected["remediation_route"]["direct_route_to_steghealer"][-1]["to"] = "somewhere-else"
        with self.assertRaisesRegex(ValueError, "REMEDIATION_ROUTE_IS_NOT_THE_CALCULATED_ROUTE"):
            validate_remediation_fork_request(redirected)
        missing = {k: v for k, v in request.items() if k != "remediation_route"}
        with self.assertRaisesRegex(ValueError, "REMEDIATION_ROUTE_IS_NOT_THE_CALCULATED_ROUTE"):
            validate_remediation_fork_request(missing)

    def test_the_handoff_is_at_the_calculated_entry_or_not_at_all(self):
        elsewhere = dict(self.deny, evaluation_boundary="ORGANIZATION_INGRESS", organization="SomeOtherOrg")
        with self.assertRaisesRegex(ValueError, "REMEDIATION_HANDOFF_IS_NOT_AT_THE_CALCULATED_ENTRY"):
            build_remediation_fork(self.request, elsewhere, BOUNDARY)
        fork = build_remediation_fork(self.request, self.deny, BOUNDARY)
        self.assertEqual(fork["remediation_route"]["entry_organization"], self.destination["organization"])


if __name__ == "__main__":
    unittest.main()
