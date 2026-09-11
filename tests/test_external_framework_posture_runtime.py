from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from stegverse.external_framework_runner import main, run_external_framework
from tests.test_intr_posture_runtime_bridge import governance_request, fake_intr_resolver


class ExternalFrameworkPostureRuntimeTests(unittest.TestCase):
    def test_prepare_only_cli_retains_posture_request_without_resolving_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/"input.json").write_text(json.dumps({"observation":"x"}))
            (root/"gov.json").write_text(json.dumps(governance_request()))
            (root/"posture.json").write_text(json.dumps({
                "schema":"stegverse.sdk.security-posture-request.v1",
                "task_id":"EVAL-CLI-1",
                "selected_tier":None,
                "selection_present":False,
                "organization_minimum_tier":"SECURE",
                "data_class":None,
                "channel":None,
                "authority_effect":"NONE_REQUEST_INPUT_ONLY",
            }))
            out=root/"out.json"
            rc=main([
                "--input",str(root/"input.json"),"--governance-request",str(root/"gov.json"),
                "--security-posture-request",str(root/"posture.json"),
                "--source-framework","fixture","--source-output-id","out-1",
                "--created-at","2026-09-10T19:00:00Z","--prepare-only","--output",str(out),
            ])
            self.assertEqual(rc,0)
            result=json.loads(out.read_text())
            self.assertFalse(result["execution_performed"])
            self.assertFalse(result["posture_resolution_performed"])
            self.assertIn("security_posture_request",result["manifest"]["extensions"])
            self.assertNotIn("effective_posture",result["manifest"]["extensions"])

    def test_runtime_calls_injected_intr_before_exact_governance_request_executes(self):
        captured={}
        def run_governance(request, *, custody_db, host_identity):
            captured["request"]=request
            return {"manifest_receipt_id":"MR-1","governance_state":"ADMITTED"}
        with patch("stegverse.sovereign_validation_runtime.run_sovereign_validation",side_effect=run_governance), \
             patch("stegverse.sovereign_validation_runtime.replay_sovereign",return_value={"status":"REPLAYED"}), \
             patch("stegverse.sovereign_validation_runtime.reconstruct_sovereign",return_value={"status":"RECONSTRUCTED"}):
            result=run_external_framework(
                data={"observation":"x"},source_framework="fixture",source_output_id="runtime-1",
                processor_request=governance_request(),
                security_posture_request={
                    "schema":"stegverse.sdk.security-posture-request.v1","task_id":"EVAL-RUNTIME-1",
                    "selected_tier":"HIGHEST","selection_present":True,
                    "organization_minimum_tier":"SECURE","data_class":None,"channel":None,
                    "authority_effect":"NONE_REQUEST_INPUT_ONLY",
                },
                created_at="2026-09-10T19:00:00Z",posture_observed_at="2026-09-10T19:00:00Z",
                intr_posture_resolver=fake_intr_resolver,
            )
        binding=result["intr_security_posture_binding"]
        self.assertTrue(result["posture_bound_execution"])
        self.assertEqual(binding["task_id"],"EVAL-RUNTIME-1")
        self.assertFalse(binding["sdk_resolved_posture"])
        self.assertTrue(binding["transition_request_sha256"].startswith("sha256:"))
        self.assertEqual(result["manifest_receipt_id"],"MR-1")
        self.assertIn("request_id",captured["request"])


if __name__=="__main__": unittest.main()
