"""The canonical connector registry is the fourth map of SDK capability.

A registered capability the SDK does not bind is not invocable, and an SDK
subsystem reaching the registry undeclared is a change to the SDK's own
ingress/egress surface that must be read rather than absorbed.
"""
import json
from pathlib import Path
import unittest

from stegverse.connector_capability_overlay import (
    AUTHORITY_BOUNDARY,
    BOUNDARY_AXIS,
    DECLARED_SUBSYSTEM_ABSENT,
    LEG_SET_CHANGED,
    OVERLAY_BOUND,
    OVERLAY_RECONCILED,
    PROFILE_CONTENT_CHANGED,
    PROFILE_LEGS,
    REGISTERED_NOT_BOUND,
    SDK_SUBSYSTEM_BASELINE,
    STOP_OVERLAY_DRIFT,
    UNDECLARED_SDK_SUBSYSTEM,
    UNKNOWN_BOUNDARY,
    boundary_path,
    canonical_sha256,
    overlay_rows,
    reconcile_overlay,
)
from stegverse.evaluator_review_intr import REQUEST_SCHEMA as EVALUATOR_REVIEW_SCHEMA
from stegverse.publisher_return_binding import PUBLISHER_RETURN_SCHEMA
from stegverse.manifest_contract import INGRESS_PROFILE as MANIFEST_INGRESS_SCHEMA
from stegverse.review_publisher_transfer import TRANSFER_SCHEMA

BASELINE_PATH = (Path(__file__).resolve().parent.parent / "data"
                 / "universal-intr-connector-sdk-profiles.baseline.json")

#: The digest the canonical generator itself published for this profile, read
#: from the generated connector's PROVENANCE.profile_sha256. Matching it proves
#: this module canonicalizes exactly as the generator does.
UPSTREAM_PINNED_EVALUATOR_REVIEW = (
    "sha256:07e22ab23438d9a3d5559c69fa76cdb098b8d81f2e7a14aa72064d0198e8c390")

#: What the installed SDK actually binds, read from the modules themselves so a
#: renamed or removed schema fails this suite rather than passing on a literal.
SDK_BOUND = (MANIFEST_INGRESS_SCHEMA, EVALUATOR_REVIEW_SCHEMA, TRANSFER_SCHEMA, PUBLISHER_RETURN_SCHEMA)


def _baseline_registry():
    payload = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    return {"schema": payload["canonical_registry"]["registry_schema"],
            "state": payload["canonical_registry"]["registry_state"],
            "profiles": payload["profiles"]}


class BaselineFidelityTest(unittest.TestCase):
    def test_pinned_digests_match_the_verbatim_profiles(self):
        """The pin has to correspond to real content, not to a remembered string."""
        by_id = {p["profile_id"]: p for p in _baseline_registry()["profiles"]}
        for subsystem, declared in SDK_SUBSYSTEM_BASELINE.items():
            with self.subTest(subsystem=subsystem):
                profile = by_id[declared["profile_id"]]
                self.assertEqual(canonical_sha256(profile),
                                 declared["profile_canonical_sha256"])

    def test_canonicalization_matches_the_generator(self):
        by_id = {p["profile_id"]: p for p in _baseline_registry()["profiles"]}
        self.assertEqual(canonical_sha256(by_id["evaluator-read-review"]),
                         UPSTREAM_PINNED_EVALUATOR_REVIEW)

    def test_every_declared_subsystem_names_a_schema_the_sdk_binds(self):
        for subsystem, declared in SDK_SUBSYSTEM_BASELINE.items():
            with self.subTest(subsystem=subsystem):
                self.assertIn(declared["payload_schema"], SDK_BOUND)

    def test_return_legs_are_scanned(self):
        """SDK:ReviewerReturn is only reachable through a response leg."""
        self.assertIn("response.destination", PROFILE_LEGS)
        self.assertIn("response.source", PROFILE_LEGS)
        rows = {r["profile_id"]: r for r in overlay_rows(_baseline_registry())}
        self.assertIn("SDK:ReviewerReturn", rows["sdk-publisher-review"]["sdk_subsystems"])


class ReconciliationTest(unittest.TestCase):
    def test_canonical_baseline_reconciles(self):
        result = reconcile_overlay(_baseline_registry(), bound_payload_schemas=SDK_BOUND)
        self.assertEqual(result["state"], OVERLAY_RECONCILED)
        self.assertEqual(result["disposition"], "ALLOW")
        self.assertEqual(result["failures"], [])
        self.assertEqual(len(result["sdk_capabilities"]), len(SDK_SUBSYSTEM_BASELINE))
        for entry in result["sdk_capabilities"]:
            self.assertEqual(entry["state"], OVERLAY_BOUND)

    def test_capability_is_overlaid_on_its_owning_organization(self):
        result = reconcile_overlay(_baseline_registry(), bound_payload_schemas=SDK_BOUND)
        owners = {e["subsystem"]: e["owner_organization"] for e in result["sdk_capabilities"]}
        self.assertEqual(owners["SDK:ManifestIngress"], "StegVerse-org")
        self.assertEqual(owners["SDK:EvaluatorReviewIngress"], "StegVerse-Labs")
        self.assertEqual(owners["SDK:ReviewerEvidenceExport"], "GCAT-BCAT-Engine")
        self.assertIn("StegVerse-Labs", result["overlaid_organizations"])

    def test_unbound_registered_capability_fails_closed(self):
        result = reconcile_overlay(_baseline_registry(),
                                   bound_payload_schemas=[EVALUATOR_REVIEW_SCHEMA])
        self.assertEqual(result["state"], STOP_OVERLAY_DRIFT)
        self.assertEqual(result["disposition"], "FAIL_CLOSED")
        unbound = [f for f in result["failures"]
                   if f.get("failed_predicate") == REGISTERED_NOT_BOUND]
        self.assertTrue(unbound)
        self.assertIn("stegverse.review_publisher_transfer",
                      " ".join(f["required_evidence_or_repair"] for f in unbound))

    def test_a_new_sdk_subsystem_is_reported_not_absorbed(self):
        registry = _baseline_registry()
        registry["profiles"] = registry["profiles"] + [{
            "profile_id": "unreviewed-sdk-capability",
            "schema": "stegverse.universal-intr.connector-profile/v1",
            "payload_schema": "stegverse.something.else/v1",
            "source": {"boundary": "DEVICE_SYSTEM", "subsystem": "Site:Caller"},
            "destination": {"boundary": "STEGOS_ECOSYSTEM", "subsystem": "SDK:NotDeclaredHere"},
            "downstream_owner_ref": "StegVerse-Labs/.github#999",
            "operations": ["READ"],
        }]
        result = reconcile_overlay(registry, bound_payload_schemas=SDK_BOUND)
        self.assertEqual(result["undeclared_sdk_subsystems"], ["SDK:NotDeclaredHere"])
        self.assertEqual(result["disposition"], "FAIL_CLOSED")
        self.assertTrue(any(f.get("failed_predicate") == UNDECLARED_SDK_SUBSYSTEM
                            for f in result["failures"]))

    def test_declared_subsystem_missing_from_registry_fails_closed(self):
        registry = _baseline_registry()
        registry["profiles"] = [p for p in registry["profiles"]
                                if p["profile_id"] != "sdk-publisher-review"]
        result = reconcile_overlay(registry, bound_payload_schemas=SDK_BOUND)
        self.assertEqual(result["disposition"], "FAIL_CLOSED")
        self.assertTrue(any(f.get("failed_predicate") == DECLARED_SUBSYSTEM_ABSENT
                            for f in result["failures"]))

    def test_changed_profile_content_is_never_auto_adopted(self):
        registry = _baseline_registry()
        for profile in registry["profiles"]:
            if profile["profile_id"] == "evaluator-read-review":
                profile["custody_mode"] = "EXACT_BYTES"
        result = reconcile_overlay(registry, bound_payload_schemas=SDK_BOUND)
        changed = [f for f in result["failures"]
                   if f.get("failed_predicate") == PROFILE_CONTENT_CHANGED]
        self.assertTrue(changed)
        self.assertNotEqual(changed[0]["observed_profile_canonical_sha256"],
                            changed[0]["baseline_profile_canonical_sha256"])

    def test_subsystem_moved_to_another_leg_fails_closed(self):
        registry = _baseline_registry()
        for profile in registry["profiles"]:
            if profile["profile_id"] == "sdk-publisher-review":
                profile["source"] = {"boundary": "STEGOS_ECOSYSTEM",
                                     "subsystem": "SDK:ReviewerReturn"}
        result = reconcile_overlay(registry, bound_payload_schemas=SDK_BOUND)
        self.assertEqual(result["disposition"], "FAIL_CLOSED")
        self.assertTrue(any(f.get("failed_predicate") in {LEG_SET_CHANGED,
                                                          PROFILE_CONTENT_CHANGED}
                            for f in result["failures"]))

    def test_every_non_allow_names_its_repair(self):
        """ECOSYSTEM_STATE_TRANSITION_DISPOSITION_INVARIANT: no bare blocker."""
        result = reconcile_overlay(_baseline_registry(), bound_payload_schemas=[])
        self.assertTrue(result["failures"])
        for failure in result["failures"]:
            with self.subTest(failure=failure.get("failed_predicate")):
                for field in ("failed_predicate", "required_evidence_or_repair",
                              "retry_entrypoint", "owning_existing_goal"):
                    self.assertTrue(failure.get(field), field)


class BoundaryAxisTest(unittest.TestCase):
    def test_path_is_a_slice_of_the_axis(self):
        self.assertEqual(boundary_path("DEVICE_SYSTEM", "STEGOS_ECOSYSTEM"),
                         ["DEVICE_SYSTEM", "STEGOS_ECOSYSTEM"])
        self.assertEqual(boundary_path("KV", "KV"), ["KV"])

    def test_reverse_direction_reverses_the_slice(self):
        self.assertEqual(boundary_path("EXTERNAL_SYSTEM", "KV"),
                         list(reversed(BOUNDARY_AXIS[1:])))

    def test_unknown_boundary_fails_closed_rather_than_extending_the_axis(self):
        with self.assertRaises(ValueError):
            boundary_path("SOMEWHERE_ELSE", "KV")
        registry = _baseline_registry()
        registry["profiles"] = registry["profiles"] + [{
            "profile_id": "off-axis",
            "source": {"boundary": "SOMEWHERE_ELSE", "subsystem": "X:Y"},
            "destination": {"boundary": "KV", "subsystem": "A:B"},
            "downstream_owner_ref": "StegVerse-Labs/.github#1",
        }]
        result = reconcile_overlay(registry, bound_payload_schemas=SDK_BOUND)
        self.assertTrue(any(f.get("failed_predicate") == UNKNOWN_BOUNDARY
                            for f in result["failures"]))


class ProjectionCoverageTest(unittest.TestCase):
    def test_a_stale_projection_is_machine_visible(self):
        result = reconcile_overlay(
            _baseline_registry(), bound_payload_schemas=SDK_BOUND,
            projected_profile_ids=["evaluator-read-review"])
        coverage = result["projection_coverage"]
        self.assertFalse(coverage["projection_is_current"])
        self.assertEqual(coverage["unprojected_profile_ids"], ["sdk-manifest-ingress", "sdk-publisher-review"])
        self.assertFalse(coverage["sdk_may_regenerate_projection"])

    def test_coverage_is_absent_unless_a_projection_is_supplied(self):
        result = reconcile_overlay(_baseline_registry(), bound_payload_schemas=SDK_BOUND)
        self.assertNotIn("projection_coverage", result)


class AuthorityBoundaryTest(unittest.TestCase):
    def test_reconciliation_claims_nothing(self):
        result = reconcile_overlay(_baseline_registry(), bound_payload_schemas=SDK_BOUND)
        self.assertEqual(result["authority_boundary"], AUTHORITY_BOUNDARY)
        self.assertEqual(result["authority_effect"], "NONE_SOURCE_RECONCILIATION_ONLY")
        for claim, value in AUTHORITY_BOUNDARY.items():
            with self.subTest(claim=claim):
                self.assertFalse(value)

    def test_registry_dict_form_is_accepted(self):
        registry = _baseline_registry()
        registry["profiles"] = {p["profile_id"]: {k: v for k, v in p.items()
                                                  if k != "profile_id"}
                                for p in registry["profiles"]}
        result = reconcile_overlay(registry, bound_payload_schemas=SDK_BOUND)
        self.assertEqual(result["disposition"], "ALLOW")


if __name__ == "__main__":
    unittest.main()
