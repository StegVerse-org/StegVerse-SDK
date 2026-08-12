import unittest

from stegverse.governance_navigation import (
    DEMO_OUTPUT_PROFILE,
    INGRESS_PROFILE,
    MANIFEST_LABEL_PROFILE,
    canonical_sha256,
    demo_output_manifest_shape,
    guidance_for,
    manifest_shape_guidance,
    navigation_text,
    normalize_manifest_labels,
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

    def test_every_choice_explains_manifest_shape_and_labels(self):
        for selection in ("000", "00", "0", "1", "2"):
            text = guidance_for(selection)
            self.assertIn("MANIFEST SHAPE", text)
            self.assertIn("manifest_profile", text)
            self.assertIn("return_projection", text)
            self.assertIn("manifest_labels", text)
            self.assertIn("Master Records custody is independent", text)

    def test_manifest_shape_labels_transition_and_receipt_classes(self):
        text = manifest_shape_guidance()
        self.assertIn("transition classes", text)
        self.assertIn("receipt classes", text)
        self.assertIn("Governance and consequence trajectory", text)
        self.assertIn("MANIFEST_ADMITTED", text)
        self.assertIn("RESULT_INGESTED", text)
        self.assertIn("manifest-label-projection", text)

    def test_manifest_labels_are_return_explanation_only(self):
        labels = normalize_manifest_labels({"mode": "ALL"})
        self.assertEqual(labels["profile"], MANIFEST_LABEL_PROFILE)
        self.assertEqual(labels["mode"], "ALL")
        self.assertTrue(labels["include_field_descriptions"])
        self.assertTrue(labels["include_transition_class_labels"])
        self.assertTrue(labels["include_receipt_class_labels"])
        self.assertTrue(labels["controls_return_explanation_only"])
        self.assertFalse(labels["changes_governance_decision"])
        self.assertFalse(labels["suppresses_master_records_custody"])
        self.assertFalse(labels["grants_authority"])

    def test_selected_manifest_labels_require_sections(self):
        labels = normalize_manifest_labels({
            "mode": "SELECTED",
            "sections": ["governed_trajectory", "exact_run_locator"],
        })
        self.assertEqual(labels["sections"], ["governed_trajectory", "exact_run_locator"])
        with self.assertRaises(ValueError):
            normalize_manifest_labels({"mode": "SELECTED"})

    def test_demo_output_embeds_exact_dataset_as_submitted_payload(self):
        demo = demo_output_manifest_shape()
        dataset = demo["000_governance_outcome_dataset"]
        manifest = demo["canonical_manifest_example"]
        processing = demo["demo_dataset_processing"]
        self.assertEqual(manifest["payload"], dataset)
        self.assertEqual(manifest["hashes"]["payload_sha256"], canonical_sha256(dataset))
        self.assertEqual(processing["dataset_sha256"], canonical_sha256(dataset))
        self.assertEqual(processing["submitted_as"], "canonical_manifest_example.payload")
        self.assertTrue(processing["dataset_loaded_into_demo_manifest"])
        self.assertEqual(processing["canonical_processing_status"], "PENDING_RUNTIME_BINDING")
        self.assertTrue(processing["do_not_claim_processed_until_receipts_exist"])
        self.assertIn("MANIFEST_ADMITTED", processing["required_processing_receipt_classes"])
        self.assertIn("governance-decision", processing["required_processing_receipt_classes"])
        self.assertIn("RESULT_INGESTED", processing["required_processing_receipt_classes"])
        self.assertIn("manifest-receipt", processing["required_processing_receipt_classes"])

    def test_demo_output_is_self_describing_for_human_or_llm_reconstruction(self):
        demo = demo_output_manifest_shape()
        self.assertEqual(demo["schema"], DEMO_OUTPUT_PROFILE)
        self.assertEqual(demo["canonical_input_profile"], INGRESS_PROFILE)
        manifest = demo["canonical_manifest_example"]
        self.assertEqual(manifest["manifest_profile"], INGRESS_PROFILE)
        self.assertEqual(manifest["manifest_labels"]["mode"], "ALL")
        self.assertGreaterEqual(len(demo["sections"]), 7)
        self.assertGreaterEqual(len(demo["process_sequence"]), 8)
        for section in demo["sections"]:
            self.assertIn("manifest_label", section)
            label = section["manifest_label"]
            self.assertIn("title", label)
            self.assertIn("description", label)
            self.assertIn("transition_classes", label)
            self.assertIn("receipt_classes", label)
            self.assertIn("editable", label)
            self.assertIn("authority_effect", label)
        self.assertIn("human", demo["reconstruction_notes"])
        self.assertIn("llm", demo["reconstruction_notes"])
        self.assertFalse(demo["demo_grants_authority"])

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

    def test_option_zero_machine_manifest_may_request_explanatory_return_labels(self):
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
            "manifest_labels": {"mode": "ALL"},
            "hashes": {
                "payload_sha256": canonical_sha256(payload),
                "candidate_sha256": canonical_sha256(candidate),
            },
        }
        result = validate_external_manifest(manifest)
        self.assertTrue(result["external_manifest_valid"])
        self.assertFalse(result["external_manifest_grants_authority"])
        self.assertEqual(result["return_projection"]["mode"], "NONE")
        self.assertEqual(result["manifest_labels"]["mode"], "ALL")
        self.assertTrue(result["manifest_labels"]["controls_return_explanation_only"])
        self.assertFalse(result["manifest_labels_change_governance"])
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
