from __future__ import annotations

import unittest

from stegverse.evaluator_manifest_builder import build_evaluator_governance_manifest
from stegverse.intr_posture_runtime_bridge import InTrPostureBridgeError, resolve_manifest_posture
from stegverse.security_posture_request import build_security_posture_request


def governance_request():
    return {
        "candidate":{"actor_class":"external_framework","action":"evaluate","target":"native","scope":"test","parameters":{"external_side_effect":False}},
        "judgment":{"refusal_available":True,"operator_recoverability":"available","workload_state":"supported","time_pressure":"normal","isolation_state":"supported","evidence_refs":["e:1"]},
        "signal":{"admitted_signal_refs":["e:1"],"excluded_signal_refs":[],"transformations":[],"missing_inputs":[],"uncertainty_state":"bounded","reference_state_hash":"a"*64,"expected_reference_state_hash":"a"*64,"reconstruction_available":True,"transformation_provenance_complete":True},
        "execution":{"actor_authority_current":True,"policy_current":True,"delegation_current":True,"evidence_current":True,"affected_entity_conditions_represented":True,"recoverability_profile":"recoverable","validity_window_open":True,"policy_ref":"p","delegation_ref":"d","evidence_refs":["e:1"]},
        "capability":{"allowed":True},"continuity":{"required":False},"approval":{"required":False},"permission_present":True,
    }


def fake_intr_resolver(*, request, task_id, payload_sha256, transition_request_sha256, observed_at):
    tier = "HIGHEST" if request.get("selected_tier") == "HIGHEST" else "SECURE"
    instance = {
        "schema":"stegverse.intr.security-posture-instance.v1",
        "instance_id":"INTR-SP-test",
        "task_id":task_id,
        "payload_sha256":payload_sha256,
        "transition_request_sha256":transition_request_sha256,
        "automatic_tier":"SECURE",
        "selected_tier":tier,
        "selection_present":request.get("selection_present") is True,
        "effective_tier":tier,
        "channel":request.get("channel"),
        "data_class":request.get("data_class"),
        "issued_at":observed_at,
        "expires_at":"2026-09-10T21:00:00Z",
        "automatic_posture_id":"stegverse.security.secure.v1",
        "selected_posture_id":"stegverse.security.health-pii-high.v1" if tier=="HIGHEST" else "stegverse.security.secure.v1",
        "effective_posture_id":"stegverse.security.health-pii-high.v1" if tier=="HIGHEST" else "stegverse.security.secure.v1",
        "resolution_authority":"INTERLOCK_INTR",
        "credential_authority":"TV/TVC",
        "transferable":False,"reusable_across_tasks":False,
        "authority_effect":"NONE_POSTURE_ADMISSION_EVIDENCE_ONLY",
        "instance_sha256":"fixture",
    }
    return {
        "schema":"stegos.intr-security-posture-resolution.v1",
        "task_id":task_id,
        "automatic_posture":{"tier":"SECURE","posture_id":"stegverse.security.secure.v1"},
        "selected_posture":{"tier":tier,"posture_id":instance["selected_posture_id"],"selection_present":request.get("selection_present") is True},
        "effective_posture":{"tier":tier,"posture_id":instance["effective_posture_id"]},
        "posture_instance":instance,
        "resolution_authority":"INTERLOCK_INTR","credential_authority":"TV/TVC",
        "sdk_authoritative_final_tier":False,"authority_effect":"NONE_POSTURE_ADMISSION_EVIDENCE_ONLY",
    }


class RuntimeBridgeTests(unittest.TestCase):
    def manifest(self):
        return build_evaluator_governance_manifest(
            data={"observation":"x"},source_framework="fixture",source_output_id="1",
            governance_request=governance_request(),
            security_posture_request=build_security_posture_request(task_id="EVAL-1",selected_tier="HIGHEST",selection_present=True),
            created_at="2026-09-10T19:00:00Z",
        )

    def test_exact_task_payload_transition_binding(self):
        manifest=self.manifest(); transition={"request":"govern"}
        bound=resolve_manifest_posture(manifest=manifest,transition_request=transition,resolver=fake_intr_resolver,observed_at="2026-09-10T19:00:00Z")
        self.assertEqual(bound["task_id"],"EVAL-1")
        self.assertTrue(bound["payload_sha256"].startswith("sha256:"))
        self.assertTrue(bound["transition_request_sha256"].startswith("sha256:"))
        self.assertFalse(bound["sdk_resolved_posture"])
        self.assertEqual(bound["projection"]["effective_posture"]["tier"],"HIGHEST")

    def test_missing_posture_request_fails_closed(self):
        m=build_evaluator_governance_manifest(data={"x":1},source_framework="f",source_output_id="2",governance_request=governance_request(),created_at="2026-09-10T19:00:00Z")
        with self.assertRaisesRegex(InTrPostureBridgeError,"security_posture_request_required"):
            resolve_manifest_posture(manifest=m,transition_request={"x":1},resolver=fake_intr_resolver,observed_at="2026-09-10T19:00:00Z")

    def test_detached_payload_resolution_rejected(self):
        def bad(**kwargs):
            r=fake_intr_resolver(**kwargs)
            r["posture_instance"]["payload_sha256"]="sha256:"+"0"*64
            return r
        with self.assertRaisesRegex(InTrPostureBridgeError,"payload_mismatch"):
            resolve_manifest_posture(manifest=self.manifest(),transition_request={"x":1},resolver=bad,observed_at="2026-09-10T19:00:00Z")


if __name__=="__main__": unittest.main()
