import unittest

from stegverse.governance_navigation import (
    INGRESS_PROFILE,
    guidance_for,
    navigation_text,
    validate_external_manifest,
    validate_manifest_receipt_id,
    canonical_sha256,
)


class GovernanceNavigationTests(unittest.TestCase):
    def test_navigation_exposes_three_canonical_options(self):
        text = navigation_text()
        self.assertIn("[0] Submit data for governance", text)
        self.assertIn("[1] Replay previously run set", text)
        self.assertIn("[2] Reconstruct previously run set", text)

    def test_guidance_is_explicit_before_input(self):
        self.assertIn("preformatted machine manifest", guidance_for("0"))
        self.assertIn("manifest_receipt_id", guidance_for("1"))
        self.assertIn("Consequential side effects", guidance_for("2").replace("consequential", "Consequential"))

    def test_external_manifest_is_structural_not_authority(self):
        payload = {"reading": 42}
        candidate = {"action": "evaluate"}
        manifest = {
            "manifest_profile": INGRESS_PROFILE,
            "manifest_profile_version": "1",
            "source_framework": "example.framework",
            "source_output_id": "evt-1",
            "created_at": "2026-08-12T19:00:00Z",
            "payload": payload,
            "candidate": candidate,
            "declared_intent": "evaluation",
            "requested_consequence": "none",
            "hashes": {
                "payload_sha256": canonical_sha256(payload),
                "candidate_sha256": canonical_sha256(candidate),
            },
        }
        result = validate_external_manifest(manifest)
        self.assertTrue(result["external_manifest_valid"])
        self.assertFalse(result["external_manifest_grants_authority"])
        self.assertEqual(result["ingress_mode"], "external_manifest")

    def test_unknown_manifest_fields_fail_closed(self):
        with self.assertRaises(ValueError):
            validate_external_manifest({"manifest_profile": INGRESS_PROFILE, "surprise": True})

    def test_receipt_id_is_canonical_user_handle(self):
        self.assertEqual(validate_manifest_receipt_id("mr-0123456789abcdef"), "MR-0123456789ABCDEF")
        with self.assertRaises(ValueError):
            validate_manifest_receipt_id("transaction-123")


if __name__ == "__main__":
    unittest.main()
