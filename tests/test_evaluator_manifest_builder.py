from __future__ import annotations

import unittest

from stegverse.evaluator_manifest_builder import build_evaluator_governance_manifest
from stegverse.governance_navigation import canonical_sha256
from stegverse.security_posture_request import build_security_posture_request


def governance_request():
    return {
        "candidate": {"actor_class":"external_framework","action":"evaluate","target":"native","scope":"test","parameters":{"external_side_effect":False}},
        "judgment": {"refusal_available":True,"operator_recoverability":"available","workload_state":"supported","time_pressure":"normal","isolation_state":"supported","evidence_refs":["external:test:1"]},
        "signal": {"admitted_signal_refs":["external:test:1"],"excluded_signal_refs":[],"transformations":[],"missing_inputs":[],"uncertainty_state":"bounded","reference_state_hash":"a"*64,"expected_reference_state_hash":"a"*64,"reconstruction_available":True,"transformation_provenance_complete":True},
        "execution": {"actor_authority_current":True,"policy_current":True,"delegation_current":True,"evidence_current":True,"affected_entity_conditions_represented":True,"recoverability_profile":"recoverable","validity_window_open":True,"policy_ref":"external:test-policy","delegation_ref":"external:test-delegation","evidence_refs":["external:test:1"]},
        "capability": {"allowed":True},
        "continuity": {"required":False},
        "approval": {"required":False},
        "permission_present": True,
    }


class EvaluatorManifestBuilderTests(unittest.TestCase):
    def test_composes_four_independent_inputs_without_posture_resolution(self):
        payload={"class":"elan.relational-state.v1","observed":{"silence":True}}
        declaration={"schema":"elan.evaluator-preregistration.v1","protocol_ref":"elan-test-1"}
        posture=build_security_posture_request(
            task_id="ELAN-EVALUATOR-TEST-001",
            selection_present=False,
            organization_minimum_tier="SECURE",
            data_class="elan.relational-state.v1",
        )
        request=governance_request()
        manifest=build_evaluator_governance_manifest(
            data=payload,
            source_framework="ELAN",
            source_output_id="elan-output-001",
            governance_request=request,
            evaluation_declaration=declaration,
            security_posture_request=posture,
            data_class="elan.relational-state.v1",
            created_at="2026-09-10T18:40:00Z",
        )
        self.assertEqual(manifest["payload"],payload)
        self.assertEqual(manifest["candidate"],request["candidate"])
        self.assertEqual(manifest["processing"]["capability"],"governance")
        self.assertEqual(manifest["extensions"]["stegverse_governance_request"],request)
        self.assertEqual(manifest["extensions"]["evaluation_declaration"],declaration)
        self.assertEqual(manifest["extensions"]["security_posture_request"],posture)
        self.assertNotIn("evaluation_declaration",manifest["extensions"]["stegverse_governance_request"])
        self.assertNotIn("security_posture_request",manifest["extensions"]["stegverse_governance_request"])
        self.assertNotIn("automatic_posture",manifest["extensions"])
        self.assertNotIn("effective_posture",manifest["extensions"])
        self.assertNotIn("posture_instance",manifest["extensions"])
        self.assertEqual(manifest["hashes"]["payload_sha256"],canonical_sha256(payload))
        self.assertEqual(manifest["hashes"]["candidate_sha256"],canonical_sha256(request["candidate"]))

    def test_explicit_higher_tier_remains_request_input_only(self):
        posture=build_security_posture_request(
            task_id="EVAL-2",selected_tier="HIGHEST",selection_present=True,
            organization_minimum_tier="SECURE",data_class="PII",
        )
        manifest=build_evaluator_governance_manifest(
            data={"value":1},source_framework="fixture",source_output_id="2",
            governance_request=governance_request(),security_posture_request=posture,
            data_class="PII",created_at="2026-09-10T18:40:00Z",
        )
        self.assertEqual(manifest["extensions"]["security_posture_request"]["selected_tier"],"HIGHEST")
        self.assertEqual(manifest["extensions"]["security_posture_request"]["authority_effect"],"NONE_REQUEST_INPUT_ONLY")
        self.assertNotIn("effective_tier",manifest["extensions"]["security_posture_request"])

    def test_no_selection_cannot_smuggle_selected_tier(self):
        with self.assertRaisesRegex(ValueError,"selected_tier must be null/absent"):
            build_security_posture_request(task_id="EVAL-3",selected_tier="SECURE",selection_present=False)

    def test_authorizing_posture_request_is_rejected(self):
        bad={"schema":"stegverse.sdk.security-posture-request.v1","task_id":"EVAL-4","selected_tier":None,"selection_present":False,"organization_minimum_tier":"SECURE","data_class":None,"channel":None,"authority_effect":"GRANT"}
        with self.assertRaisesRegex(ValueError,"sdk_posture_request_must_be_non_authorizing"):
            build_evaluator_governance_manifest(
                data={"value":1},source_framework="fixture",source_output_id="4",
                governance_request=governance_request(),security_posture_request=bad,
                created_at="2026-09-10T18:40:00Z",
            )

    def test_manifest_and_posture_data_class_mismatch_fails_closed(self):
        posture=build_security_posture_request(task_id="EVAL-5",data_class="PII")
        with self.assertRaisesRegex(ValueError,"must match manifest data_class"):
            build_evaluator_governance_manifest(
                data={"value":1},source_framework="fixture",source_output_id="5",
                governance_request=governance_request(),security_posture_request=posture,
                data_class="general",created_at="2026-09-10T18:40:00Z",
            )


if __name__=="__main__":
    unittest.main()
