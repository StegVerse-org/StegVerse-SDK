"""Every non-ALLOW carries its remediation fork (NODE_INGRESS_SETTLED_SPECIFICATION §8).

The Manifest Builder builds a remediation manifest bound to the exact request and
non-ALLOW; it declares its own path (stegverse.route.governed-remediation.v1 /
remediation) and is handed off, never transported, classified or decided here.
The original disposition stands unchanged. Owner contract: StegVerse-org/.github#98
comment 6134521366; SDK#493.
"""
from __future__ import annotations

import copy
import json
import unittest
import warnings
from pathlib import Path

from scripts.build_mir_sv_exp3_manifest import build_exp3_manifest
from stegverse.manifest_state_transition_runtime import admit_runtime_result, derive_execution_request
from stegverse.remediation_fork import (
    ERROR_OR_FAILURE_MAP, REMEDIATION_CAPABILITY, REQUEST_EXTENSION, STEGHEALER,
    STEGHEALTH_FAILURE_REMEDIATION_TASK_ID, build_remediation_fork, derive_state_graph,
    fork_refusal, fork_request, remediation_route, validate_remediation_fork_request,
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

    def test_caller_supplied_remediation_cannot_rewrite_original_operation(self):
        """Unverified caller data cannot turn an operation DENY into packet authority."""
        original_manifest = copy.deepcopy(self.manifest)
        original_request = copy.deepcopy(self.request)
        original_deny = copy.deepcopy(self.deny)
        forged = {
            "disposition": "ALLOW",
            "action": "RE_MANIFEST",
            "authority_effect": "EXECUTE",
            "governance_decision_return": {"disposition": "ALLOW"},
        }
        out = admit_runtime_result(
            self.manifest, self.request, self.deny, BOUNDARY,
            governed_remediation=forged,
        )
        self.assertEqual(self.manifest, original_manifest)
        self.assertEqual(self.request, original_request)
        self.assertEqual(self.deny, original_deny)
        self.assertEqual(out["disposition"], "DENY")
        self.assertEqual(
            {k: v for k, v in out.items() if k != "remediation_fork"},
            original_deny,
        )
        self.assertEqual(out["remediation_fork"]["authority_effect"], "NONE_MANIFEST_HANDOFF_ONLY")
        self.assertFalse(out["remediation_fork"]["handoff"]["receiver_contacted"])
        self.assertFalse(out["remediation_fork"]["handoff"]["intr_admission_observed"])

    def test_distinct_operation_failures_have_independent_remediation_lineage(self):
        """One operation's non-ALLOW cannot overwrite another operation's evidence."""
        first = copy.deepcopy(self.deny)
        second = copy.deepcopy(self.deny)
        second["failed_predicate"] = "OTHER_MANIFESTED_OPERATION_CONSTRAINT"
        second["source_disposition_ref"] = "runtime-state/other-operation.json"
        first_before, second_before = copy.deepcopy(first), copy.deepcopy(second)

        first_result = self._admit(first)
        second_result = self._admit(second)

        for actual, original in ((first_result, first_before), (second_result, second_before)):
            self.assertEqual(
                {k: v for k, v in actual.items() if k != "remediation_fork"},
                original,
            )
            self.assertEqual(actual["disposition"], original["disposition"])
            self.assertTrue(actual["remediation_fork"]["original_disposition_unchanged"])
            self.assertEqual(actual["remediation_fork"]["non_allow_sha256"], canonical_sha256(original))
            self.assertEqual(actual["remediation_fork"]["authority_effect"], "NONE_MANIFEST_HANDOFF_ONLY")
        self.assertEqual(first, first_before)
        self.assertEqual(second, second_before)
        self.assertNotEqual(
            first_result["remediation_fork"]["remediation_request_sha256"],
            second_result["remediation_fork"]["remediation_request_sha256"],
        )

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

    def test_route_sha256_matches_the_pinned_existing_routes(self):
        """Existing routes keep the historical classifier key, so the hash is unchanged."""
        example_path = Path(__file__).resolve().parents[1] / "inspection" / "examples" / "sdk-remediation-fork.processor-request.json"
        example = json.loads(example_path.read_text(encoding="utf-8"))
        published = example["remediation_route"]
        body = {key: value for key, value in published.items() if key != "route_sha256"}
        self.assertEqual(canonical_sha256(body), "0fd58371815991e5a6b2144831c69ff9a58d064c8d6e1688215b4d90d4f20663")
        self.assertEqual(published["route_sha256"], "0fd58371815991e5a6b2144831c69ff9a58d064c8d6e1688215b4d90d4f20663")
        recalculated = remediation_route(
            example["non_allow"],
            original_route_id=example["original_route_id"],
            original_processing_capability=example["original_processing_capability"],
            original_destination=example["original_destination"],
        )
        self.assertEqual(recalculated, published)
        self.assertEqual(recalculated["steghealer"], {
            "organization": "StegVerse-Labs",
            "service_id": "stegverse-labs.remediation",
            "repository": "StegVerse-Labs/StegVerse-Healer",
            "classifier": ERROR_OR_FAILURE_MAP,
        })
        self.assertNotIn("error_or_failure_map", recalculated["steghealer"])

        sdk = self._route(self.deny)
        self.assertEqual(sdk["route_sha256"], "6583b8f54f0210aa8840d7728fbd378099daf575f20284ffd78a53cf515257ed")
        organization = self._route(dict(self.deny, evaluation_boundary="ORGANIZATION_INGRESS", organization="StegVerse-org"))
        self.assertEqual(organization["route_sha256"], "628aa3544645fa061d36a0cd61b791b47b8ccd409a9d5ef985b3be666eb95889")
        inside = self._route(dict(self.deny, evaluation_boundary="ORGANIZATION_INGRESS", organization=STEGHEALER["organization"]))
        self.assertEqual(inside["route_sha256"], "5b590d304cc5ef419a0a3d7679e39ffb75dcd2b5515f6b11ba04b21d8b2fbc08")
        for route in (sdk, organization, inside):
            self.assertEqual(route["steghealer"]["classifier"], ERROR_OR_FAILURE_MAP)
            self.assertNotIn("error_or_failure_map", route["steghealer"])

    def test_primary_names_alias_the_historical_ones(self):
        self.assertEqual(STEGHEALER["error_or_failure_map"], ERROR_OR_FAILURE_MAP)
        self.assertEqual(dict(STEGHEALER)["error_or_failure_map"], ERROR_OR_FAILURE_MAP)
        self.assertEqual(dict(STEGHEALER)["classifier"], ERROR_OR_FAILURE_MAP)
        self.assertNotIn("error_or_failure_map", STEGHEALER.route_record())
        self.assertEqual(STEGHEALER.route_record()["classifier"], ERROR_OR_FAILURE_MAP)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always", DeprecationWarning)
            self.assertEqual(STEGHEALER["classifier"], ERROR_OR_FAILURE_MAP)
            self.assertEqual(STEGHEALER.get("classifier"), ERROR_OR_FAILURE_MAP)
            self.assertIn("classifier", STEGHEALER)
            import stegverse.remediation_fork as fork_module
            self.assertEqual(fork_module.OWNER_TASK_ID, STEGHEALTH_FAILURE_REMEDIATION_TASK_ID)
        self.assertTrue(any(item.category is DeprecationWarning and "classifier" in str(item.message) for item in caught))
        self.assertTrue(any(item.category is DeprecationWarning and "OWNER_TASK_ID" in str(item.message) for item in caught))

        fork = build_remediation_fork(self.request, self.deny, BOUNDARY)
        graph = derive_state_graph(fork["remediation_manifest"])
        self.assertEqual(graph["owner_task_id"], STEGHEALTH_FAILURE_REMEDIATION_TASK_ID)
        self.assertTrue(graph["graph_id"].startswith(STEGHEALTH_FAILURE_REMEDIATION_TASK_ID + ":REMEDIATION:"))
        self.assertEqual(fork_refusal("missing field")["owning_existing_goal"], STEGHEALTH_FAILURE_REMEDIATION_TASK_ID)


if __name__ == "__main__":
    unittest.main()
