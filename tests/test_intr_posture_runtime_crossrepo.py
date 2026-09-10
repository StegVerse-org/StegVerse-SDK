from __future__ import annotations

import unittest

from stegos.intr_security_posture_resolution import resolve_task_security_posture
from stegverse.evaluator_manifest_builder import build_evaluator_governance_manifest
from stegverse.governance_ingress_runtime import external_manifest_to_public_request
from stegverse.intr_posture_runtime_bridge import resolve_manifest_posture
from stegverse.security_posture_request import build_security_posture_request
from tests.test_intr_posture_runtime_bridge import governance_request


class CrossRepoInTrPostureRuntimeTests(unittest.TestCase):
    def test_sdk_manifest_binds_to_actual_stegos_intr_resolver(self):
        manifest=build_evaluator_governance_manifest(
            data={"class":"evaluator.fixture.v1","observation":"neutral"},
            source_framework="IndependentEvaluator",
            source_output_id="case-001",
            governance_request=governance_request(),
            evaluation_declaration={"schema":"evaluator.preregistration.v1","protocol_ref":"fixed-before-run"},
            security_posture_request=build_security_posture_request(
                task_id="EVAL-CROSSREPO-1",selected_tier="HIGHEST",selection_present=True,
                organization_minimum_tier="SECURE",
            ),
            created_at="2026-09-10T19:00:00Z",
        )
        transition=external_manifest_to_public_request(manifest)
        bound=resolve_manifest_posture(
            manifest=manifest,transition_request=transition,
            resolver=resolve_task_security_posture,observed_at="2026-09-10T19:00:00Z",
        )
        resolution=bound["resolution"]
        self.assertEqual(resolution["resolution_authority"],"INTERLOCK_INTR")
        self.assertEqual(resolution["effective_posture"]["tier"],"HIGHEST")
        self.assertEqual(resolution["posture_instance"]["task_id"],"EVAL-CROSSREPO-1")
        self.assertEqual(resolution["posture_instance"]["payload_sha256"],bound["payload_sha256"])
        self.assertEqual(resolution["posture_instance"]["transition_request_sha256"],bound["transition_request_sha256"])
        self.assertEqual(manifest["extensions"]["evaluation_declaration"]["protocol_ref"],"fixed-before-run")
        self.assertNotIn("evaluation_declaration",manifest["extensions"]["stegverse_governance_request"])
        self.assertNotIn("posture_instance",manifest["extensions"])


if __name__=="__main__": unittest.main()
