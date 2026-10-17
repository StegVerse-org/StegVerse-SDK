"""Source-only MPDV regressions; not authentic runtime or ledger proof."""
import unittest

from stegverse.manifest_path_differential import compare_manifest_paths


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
            snapshot(), snapshot(route_id="route-b", evidence_refs=["receipt:diagnostic"]),
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


if __name__ == "__main__":
    unittest.main()
