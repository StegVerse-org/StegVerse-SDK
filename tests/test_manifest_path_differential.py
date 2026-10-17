"""Source-only MPDV regressions; not authentic runtime or ledger proof."""
import copy
import json
import unittest
from pathlib import Path

from stegverse.manifest_path_differential import (
    FINDING_OBSERVATIONS,
    OWNING_EXISTING_GOAL,
    REFUSAL_DISPOSITIONS,
    ManifestPathDifferentialRefusal,
    compare_manifest_paths,
    declared_refusal,
)

SIX_FIELDS = (
    "failure_code", "failed_predicate", "required_evidence_or_repair",
    "retry_entrypoint", "owning_existing_goal", "next_attempt",
)
FIXTURE = Path(__file__).parent / "fixtures" / "ecosystem-diagnostic" / "steghealth-51-governed-deny-negative-control.json"


def snapshot(**overrides):
    row = {
        "manifest_digest": "sha256:original",
        "route_id": "route-a",
        "component_id": "sdk",
        "predicate_id": "P1",
        "policy_version": "v1",
        "authority_binding": "owner",
        "disposition": "DENY",
        "evidence_refs": ["receipt:original"],
    }
    row.update(overrides)
    return row


class ManifestPathDifferentialTests(unittest.TestCase):
    def test_correct_deny_retains_disposition_and_no_authority(self):
        result = compare_manifest_paths(snapshot(), snapshot(), finding="EXPECTED_GOVERNED_DENY")
        self.assertEqual(result["path_deltas"], [])
        self.assertEqual(result["original_disposition"], "DENY")
        self.assertFalse(result["remediation_authorized"])
        self.assertFalse(result["experiment_result_established"])
        self.assertFalse(result["authentic_readback_verified"])

    def test_route_delta_is_evidence_bound_candidate_only(self):
        result = compare_manifest_paths(
            snapshot(),
            snapshot(route_id="route-b", disposition="FAIL_CLOSED", evidence_refs=["receipt:diagnostic"]),
            finding="CAPABILITY_GAP_IDENTIFIED",
        )
        self.assertEqual(result["path_deltas"][0]["field"], "route_id")
        self.assertEqual(result["evidence_refs"], ["receipt:original", "receipt:diagnostic"])
        self.assertEqual(result["authority_effect"], "NONE_DIAGNOSTIC_ONLY")

    def test_missing_evidence_does_not_claim_authentication(self):
        result = compare_manifest_paths(
            snapshot(evidence_refs=[]), snapshot(evidence_refs=[]),
        )
        self.assertEqual(result["finding_candidate"], "INSUFFICIENT_AUTHENTIC_EVIDENCE")
        self.assertFalse(result["authentic_readback_verified"])

    def test_refuses_non_nonallow_and_unsupported_findings(self):
        with self.assertRaises(ValueError):
            compare_manifest_paths(snapshot(disposition="ALLOW"), snapshot())
        with self.assertRaises(ValueError):
            compare_manifest_paths(snapshot(), snapshot(), finding="EXPERIMENT_FAILED")


class SixFieldRefusalTests(unittest.TestCase):
    def refusal(self, *args, **kwargs):
        with self.assertRaises(ManifestPathDifferentialRefusal) as ctx:
            compare_manifest_paths(*args, **kwargs)
        refusal = ctx.exception.refusal
        self.assertEqual(
            refusal["disposition"],
            REFUSAL_DISPOSITIONS[(refusal["failure_code"], refusal["failed_predicate"])],
        )
        for field in SIX_FIELDS:
            self.assertIsInstance(refusal[field], str)
            self.assertTrue(refusal[field].strip(), field)
        self.assertEqual(refusal["owning_existing_goal"], OWNING_EXISTING_GOAL)
        self.assertIsInstance(ctx.exception, ValueError)
        return refusal

    def test_every_refusal_carries_six_fields(self):
        cases = {
            "MPDV_FINDING_UNSUPPORTED": ((snapshot(), snapshot()), {"finding": "EXPERIMENT_FAILED"}, "DENY"),
            "MPDV_SNAPSHOT_NOT_A_MAPPING": ((["x"], snapshot()), {}, "DENY"),
            "MPDV_SNAPSHOT_FIELD_ABSENT": ((snapshot(route_id="  "), snapshot()), {}, "FAIL_CLOSED"),
            "MPDV_EVIDENCE_REFS_MALFORMED": ((snapshot(evidence_refs="receipt"), snapshot()), {}, "DENY"),
            "MPDV_ORIGINAL_IS_ALLOW": ((snapshot(disposition="ALLOW"), snapshot()), {}, "DENY"),
            "MPDV_DIAGNOSTIC_DISPOSITION_UNDECLARED": (
                (snapshot(), snapshot(disposition="PENDING")), {}, "DENY"),
            "MPDV_FINDING_NOT_DECLARED_FOR_OBSERVED_DIAGNOSTIC": (
                (snapshot(), snapshot(disposition="ALLOW")), {"finding": "EXPECTED_GOVERNED_DENY"}, "FAIL_CLOSED"),
        }
        for code, (args, kwargs, disposition) in cases.items():
            with self.subTest(code=code):
                refusal = self.refusal(*args, **kwargs)
                self.assertEqual(refusal["failure_code"], code)
                self.assertEqual(refusal["disposition"], disposition)

    def test_absent_original_disposition_is_refused_not_compared(self):
        row = snapshot()
        del row["disposition"]
        refusal = self.refusal(row, snapshot())
        self.assertEqual(refusal["failure_code"], "MPDV_ORIGINAL_DISPOSITION_ABSENT")
        self.assertEqual(refusal["disposition"], "FAIL_CLOSED")

    def test_blank_evidence_locator_is_refused(self):
        refusal = self.refusal(snapshot(evidence_refs=["   "]), snapshot())
        self.assertEqual(refusal["failure_code"], "MPDV_EVIDENCE_REFS_MALFORMED")

    def test_empty_evidence_cannot_carry_a_substantive_finding(self):
        # Empty evidence on both sides must not yield an evidenced-looking result.
        result = compare_manifest_paths(
            snapshot(evidence_refs=[]), snapshot(evidence_refs=[]), finding="EXPECTED_GOVERNED_DENY",
        )
        self.assertEqual(result["finding_candidate"], "INSUFFICIENT_AUTHENTIC_EVIDENCE")
        self.assertEqual(result["requested_finding"], "EXPECTED_GOVERNED_DENY")

    def test_undeclared_refusal_pair_fails_closed_not_declared(self):
        refusal = declared_refusal({
            "failure_code": "MPDV_SOMETHING_NEW", "failed_predicate": "SOME_PREDICATE",
            "required_evidence_or_repair": "x", "retry_entrypoint": "y",
            "owning_existing_goal": OWNING_EXISTING_GOAL, "next_attempt": "z",
        })
        self.assertEqual(refusal["disposition"], "FAIL_CLOSED")
        self.assertEqual(refusal["failure_code"], "MPDV_REFUSAL_DISPOSITION_NOT_DECLARED")
        self.assertEqual(refusal["undeclared_refusal_failure_code"], "MPDV_SOMETHING_NEW")
        self.assertEqual(refusal["undeclared_refusal_failed_predicate"], "SOME_PREDICATE")

    def test_every_declared_refusal_is_deny_or_fail_closed(self):
        self.assertTrue(set(REFUSAL_DISPOSITIONS.values()) <= {"DENY", "FAIL_CLOSED"})


class FindingConsistencyTests(unittest.TestCase):
    """R3: the caller's finding must be declared for what the comparison observed."""

    def test_expected_deny_refused_for_diagnostic_allow_with_route_change(self):
        with self.assertRaises(ManifestPathDifferentialRefusal) as ctx:
            compare_manifest_paths(snapshot(), snapshot(route_id="route-b", disposition="ALLOW"),
                                   finding="EXPECTED_GOVERNED_DENY")
        refusal = ctx.exception.refusal
        self.assertEqual(refusal["failure_code"], "MPDV_FINDING_NOT_DECLARED_FOR_OBSERVED_DIAGNOSTIC")
        self.assertEqual(refusal["disposition"], "FAIL_CLOSED")

    def test_expected_deny_requires_unchanged_path(self):
        with self.assertRaises(ManifestPathDifferentialRefusal):
            compare_manifest_paths(snapshot(), snapshot(route_id="route-b"), finding="EXPECTED_GOVERNED_DENY")

    def test_absent_diagnostic_disposition_only_supports_insufficient_evidence(self):
        replay = snapshot()
        del replay["disposition"]
        for finding in FINDING_OBSERVATIONS:
            with self.subTest(finding=finding):
                if finding == "INSUFFICIENT_AUTHENTIC_EVIDENCE":
                    self.assertEqual(compare_manifest_paths(snapshot(), replay, finding=finding)["finding_candidate"],
                                     finding)
                else:
                    with self.assertRaises(ManifestPathDifferentialRefusal):
                        compare_manifest_paths(snapshot(), replay, finding=finding)

    def test_table_is_exhaustive_over_the_vocabulary(self):
        # Every pair the table lists is accepted, and every unlisted pair is refused.
        for finding, observations in FINDING_OBSERVATIONS.items():
            for disposition in ("ALLOW", "DENY", "FAIL_CLOSED"):
                for changed in (False, True):
                    replay = snapshot(disposition=disposition, evidence_refs=["receipt:diagnostic"],
                                      **({"route_id": "route-b"} if changed else {}))
                    with self.subTest(finding=finding, disposition=disposition, changed=changed):
                        if (disposition, changed) in observations:
                            self.assertEqual(
                                compare_manifest_paths(snapshot(), replay, finding=finding)["finding_candidate"],
                                finding)
                        else:
                            with self.assertRaises(ManifestPathDifferentialRefusal):
                                compare_manifest_paths(snapshot(), replay, finding=finding)


class EvidenceBothSidesTests(unittest.TestCase):
    """R5: a substantive finding needs evidence from both snapshots."""

    def test_original_side_evidence_alone_downgrades(self):
        result = compare_manifest_paths(snapshot(), snapshot(evidence_refs=[]), finding="EXPECTED_GOVERNED_DENY")
        self.assertEqual(result["finding_candidate"], "INSUFFICIENT_AUTHENTIC_EVIDENCE")
        self.assertEqual(result["finding_downgrade_reason"], "EVIDENCE_REFS_ABSENT_ON_ONE_OR_BOTH_SIDES")

    def test_diagnostic_side_evidence_alone_downgrades(self):
        result = compare_manifest_paths(snapshot(evidence_refs=[]), snapshot(evidence_refs=["receipt:d"]),
                                        finding="EXPECTED_GOVERNED_DENY")
        self.assertEqual(result["finding_candidate"], "INSUFFICIENT_AUTHENTIC_EVIDENCE")

    def test_both_sides_keep_the_finding(self):
        result = compare_manifest_paths(snapshot(), snapshot(evidence_refs=["receipt:d"]),
                                        finding="EXPECTED_GOVERNED_DENY")
        self.assertEqual(result["finding_candidate"], "EXPECTED_GOVERNED_DENY")
        self.assertIsNone(result["finding_downgrade_reason"])
        self.assertEqual(result["finding_source"], "CALLER_SUPPLIED_CHECKED_AGAINST_DECLARED_OBSERVATIONS")

    def test_inconsistent_finding_is_refused_even_without_evidence(self):
        # The input check (consistency) runs before the evidence downgrade.
        with self.assertRaises(ManifestPathDifferentialRefusal):
            compare_manifest_paths(snapshot(evidence_refs=[]), snapshot(evidence_refs=[], disposition="ALLOW"),
                                   finding="EXPECTED_GOVERNED_DENY")

    def test_success_is_comparison_allow_with_no_authority(self):
        result = compare_manifest_paths(snapshot(), snapshot(), finding="EXPECTED_GOVERNED_DENY")
        self.assertEqual(result["comparison_disposition"], "ALLOW")
        self.assertEqual(result["owning_existing_goal"], OWNING_EXISTING_GOAL)
        self.assertEqual(result["authority_effect"], "NONE_DIAGNOSTIC_ONLY")
        self.assertFalse(result["mutation_performed"])


class StegHealth51NegativeControlFixtureTests(unittest.TestCase):
    """StegHealth#51 governed-DENY negative control, reused as an SDK diagnostic fixture."""

    @classmethod
    def setUpClass(cls):
        cls.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_fixture_claims_nothing_authentic(self):
        claims = self.fixture["claims"]
        self.assertEqual(self.fixture["fixture_class"], "SYNTHETIC_SOURCE_FIXTURE")
        self.assertFalse(claims["authentic_receipts"])
        self.assertFalse(claims["trial_executed"])
        self.assertFalse(self.fixture["provenance"]["steghealth_obligation_created"])
        for key in ("organization_ledger_readback", "repository_ledger_readback", "sdk_authenticated_return"):
            self.assertEqual(claims[key], "NOT_OBSERVED")
        self.assertEqual(self.fixture["provenance"]["origin_cosv"], "10100000100000")

    def test_correct_deny_replays_as_expected_governed_deny(self):
        original = copy.deepcopy(self.fixture["original_deny"])
        result = compare_manifest_paths(
            original, self.fixture["diagnostic_replay"], finding="EXPECTED_GOVERNED_DENY",
        )
        self.assertEqual(result["path_deltas"], [])
        self.assertEqual(result["original_disposition"], "DENY")
        self.assertEqual(result["finding_candidate"], "EXPECTED_GOVERNED_DENY")
        self.assertFalse(result["experiment_result_established"])
        self.assertFalse(result["authentic_readback_verified"])
        self.assertFalse(result["remediation_authorized"])
        # The original manifest and route hashes are immutable through the comparison.
        self.assertEqual(original, self.fixture["original_deny"])
        self.assertEqual(result["original_manifest_digest"], self.fixture["original_deny"]["manifest_digest"])

    def test_deny_and_fail_closed_originals_stay_distinct(self):
        deny = compare_manifest_paths(self.fixture["original_deny"], self.fixture["diagnostic_replay"],
                                      finding="EXPECTED_GOVERNED_DENY")
        fail_closed = compare_manifest_paths(self.fixture["original_fail_closed"], self.fixture["diagnostic_replay"],
                                             finding="REQUIREMENTS_AMBIGUOUS")
        self.assertEqual(deny["original_disposition"], "DENY")
        self.assertEqual(fail_closed["original_disposition"], "FAIL_CLOSED")
        self.assertEqual([d["field"] for d in fail_closed["path_deltas"]], ["predicate_id"])

    def test_unadmitted_capability_never_becomes_allow(self):
        allowed = dict(self.fixture["original_deny"], disposition="ALLOW")
        with self.assertRaises(ManifestPathDifferentialRefusal) as ctx:
            compare_manifest_paths(allowed, self.fixture["diagnostic_replay"])
        self.assertEqual(ctx.exception.refusal["failure_code"], "MPDV_ORIGINAL_IS_ALLOW")
        self.assertEqual(ctx.exception.refusal["disposition"], "DENY")


if __name__ == "__main__":
    unittest.main()
