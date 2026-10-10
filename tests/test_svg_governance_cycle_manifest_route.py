import copy
import unittest

from stegverse.manifest_builder import build_manifest
from stegverse.manifest_state_transition_runtime import derive_execution_request
from stegverse.svg_governance_cycle_processor import (
    OWNER_COSV,
    OWNER_TASK_ID,
    REQUEST_SCHEMA,
    ROUTE_ID,
)


def processor_request():
    return {
        "schema": REQUEST_SCHEMA,
        "task_id": OWNER_TASK_ID,
        "correlation_id": OWNER_TASK_ID,
        "cosv_task_vector": OWNER_COSV,
        "benchmark_profile": "SVG-GOVERNANCE-CYCLE-V0.1",
        "transition_subject": "native-governance-cycle",
        "native_evaluator": "stegcore.three_layer.evaluate_three_layer",
        "governance_schema_ref": "StegVerse-Labs/Governance/schemas/admissibility_stage_vector.schema.json",
        "expected_evidence": [
            "ORIGINAL_INTR_DISPOSITION",
            "ORGANIZATION_LEDGER_RECEIPT_AND_PREDECESSOR",
        ],
        "authority_effect": "NONE_MANIFEST_REQUEST_ONLY",
    }


def manifest():
    return build_manifest(
        data={"benchmark_input": "source-bound-only"},
        source_framework="svg_governance_cycle",
        source_output_id="svg-governance-cycle-test",
        processor_request=processor_request(),
        process="svg_governance_cycle",
        return_depth="full-trace",
        created_at="2026-09-28T00:00:00Z",
    )


class SVGGovernanceCycleManifestRouteTests(unittest.TestCase):
    def test_route_binds_existing_owner_without_minting_authority(self):
        value = manifest()
        self.assertEqual(value["processing"]["capability"], "svg_governance_cycle")
        self.assertEqual(value["processing"]["route_id"], ROUTE_ID)
        request = derive_execution_request(value)
        self.assertEqual(request["canonical_task_id"], OWNER_TASK_ID)
        self.assertEqual(request["processing_capability"], "svg_governance_cycle")
        self.assertEqual(request["route_id"], ROUTE_ID)
        self.assertTrue(request["requires_workercoordinator_claim_fence"])
        self.assertFalse(request["request_grants_authority"])
        self.assertFalse(request["sdk_executes_lifecycle"])
        self.assertFalse(request["state_graph"]["adapter_executes_lifecycle"])
        bound = request["state_graph"]["request"]
        self.assertEqual(bound["cosv_task_vector"], OWNER_COSV)
        self.assertEqual(bound["task_id"], OWNER_TASK_ID)

    def test_owner_or_cosv_drift_fails_before_runtime_request(self):
        for field, value in (
            ("task_id", "SVG-GOVERNANCE-CAPABILITY-VERSIONING-001"),
            ("correlation_id", "SVG-GOVERNANCE-CAPABILITY-VERSIONING-001"),
            ("cosv_task_vector", "99999999999999"),
        ):
            bad = processor_request()
            bad[field] = value
            with self.assertRaises(ValueError, msg=field):
                build_manifest(
                    data={"benchmark_input": "source-bound-only"},
                    source_framework="svg_governance_cycle",
                    source_output_id="svg-governance-cycle-negative",
                    processor_request=bad,
                    process="svg_governance_cycle",
                    created_at="2026-09-28T00:00:00Z",
                )

    def test_route_substitution_fails_closed(self):
        value = manifest()
        bad = copy.deepcopy(value)
        bad["processing"]["route_id"] = "stegverse.route.canonical-governed.v1"
        with self.assertRaises(ValueError):
            derive_execution_request(bad)


if __name__ == "__main__":
    unittest.main()
