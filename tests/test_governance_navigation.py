import unittest

from stegverse.governance_navigation import (
    DEMO_OUTPUT_PROFILE,
    INGRESS_PROFILE,
    canonical_sha256,
    demo_output_manifest_shape,
    guidance_for,
    manifest_shape_guidance,
    navigation_text,
    normalize_return_projection,
    validate_external_manifest,
    validate_manifest_receipt_id,
)


class GovernanceNavigationTests(unittest.TestCase):
    def test_navigation_exposes_demo_parameter_and_three_canonical_operations(self):
        text = navigation_text()
        self.assertIn("[000] Demo test sequence without user-supplied manifest", text)
        self.assertIn("[00] User-defined run parameters", text)
        self.assertIn("[0] Submit data for governance", text)
        self.assertIn("[1] Replay previously run set", text)
        self.assertIn("[2] Reconstruct previously run set", text)

    def test_guidance_is_explicit_before_input(self):
        self.assertIn("no user-supplied manifest", guidance_for("000"))
        self.assertIn("Master Records", guidance_for("00"))
        self.assertIn("preformatted machine manifest", guidance_for("0"))
        self.assertIn("manifest_receipt_id", guidance_for("1"))
        self.assertIn("consequential side effects", guidance_for("2"))

    def test_every_choice_explains_manifest_shape_and_projection(self):
        for selection in ("000", "00", "0", "1", "2"):
            text = guidance_for(selection)
            self.assertIn("MANIFEST SHAPE", text)
            self.assertIn("manifest_profile", text)
            self.assertIn("return_projection.mode", text)
            self.assertIn("SELECTED", text)
            self.assertIn("NONE", text)
            self.assertIn("Master Records custody is independent", text)

    def test_manifest_shape_labels_transition_and_receipt_classes(self):
        text = manifest_shape_guidance()
        self.assertIn("transition classes", text)
        self.assertIn("receipt classes", text)
        self.assertIn("Governance and consequence trajectory", text)
        self.assertIn("MANIFEST_ADMITTED", text)
        self.assertIn("RESULT_INGESTED", text)

    def test_demo_output_is_self_describing_for_human_or_llm_reconstruction(self):
        demo = demo_output_manifest_shape()
        self.assertEqual(demo["schema"], DEMO_OUTPUT_PROFILE)
        self.assertEqual(demo["canonical_input_profile"], INGRESS_PROFILE)
        self.assertEqual(demo["canonical_manifest_example"]["manifest_profile"], INGRESS_PROFILE)
        self.assertGreaterEqual(len(demo["sections"]), 6)
        self.assertGreaterEqual(len(demo["process_sequence"]), 7)
        for section in demo["sections"]:
            self.assertIn("label", section)
            self.assertIn("transition_classes", section)
            self.assertIn("receipt_classes", section)
        self.assertIn("human", demo["reconstruction_notes"])
        self.assertIn("llm", demo["reconstruction_notes"])
        self.assertFalse(demo["demo_grants_authority"])

    def test_manifest_shape_explains_required_fields_cannot_be_hidden(self):
        text = manifest_shape_guidance()
        self.assertIn("cannot be set", text)
        self.assertIn("Required identity, integrity, governed-subject, and routing fields", text)
        self.assertIn("manifest_receipt_id", text)

    def test_return_projection_none_never_suppresses_master_records(self):
        projection = normalize_return_projection({"mode": "NONE"})
        self.assertEqual(projection["mode"], "NONE")
        self.assertTrue(projection["controls_user_return_only"])
        self.assertFalse(projection["suppresses_master_records_custody"])
        self.assertFalse(projection["erases_ecosystem_transitions"])
        self.assertFalse(projection["grants_authority"])

    def test_selected_return_projection_requires_explicit_classes(self):
        projection = normalize_return_projection({
            "mode": "SELECTED",
            "transition_classes": ["steggate", "return_ingestion"],
        })
        self.assertEqual(projection["transition_classes"], ["steggate", "return_ingestion"])
        with self.assertRaises(ValueError):
            normalize_return_projection({"mode": "SELECTED"})

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
            "return_projection": {"mode": "NONE"},
            "hashes": {
                "payload_sha256": canonical_sha256(payload),
                "candidate_sha256": canonical_sha256(candidate),
            },
        }
        result = validate_external_manifest(manifest)
        self.assertTrue(result["external_manifest_valid"])
        self.assertFalse(result["external_manifest_grants_authority"])
        self.assertEqual(result["ingress_mode"], "external_manifest")
        self.assertEqual(result["return_projection"]["mode"], "NONE")
        self.assertTrue(result["master_records_transition_custody_independent_of_return_projection"])

    def test_unknown_manifest_fields_fail_closed(self):
        with self.assertRaises(ValueError):
            validate_external_manifest({"manifest_profile": INGRESS_PROFILE, "surprise": True})

    def test_receipt_id_is_canonical_user_handle(self):
        self.assertEqual(validate_manifest_receipt_id("mr-0123456789abcdef"), "MR-0123456789ABCDEF")
        with self.assertRaises(ValueError):
            validate_manifest_receipt_id("transaction-123")


if __name__ == "__main__":
    unittest.main()
