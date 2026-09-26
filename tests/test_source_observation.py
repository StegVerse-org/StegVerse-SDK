"""Generic source-attribution regression for evaluator-defined scientific experiments.

All fixtures are synthetic. This suite does not invoke ÉLAN, InTr, or a
sovereign runtime and makes no claim of provider-authenticated output.
"""
from __future__ import annotations

from copy import deepcopy
import unittest

from stegverse.source_observation import (
    PROFILE, SourceObservationError, preflight_source_observation,
    validate_source_observation,
)
from stegverse.manifest_builder import build_manifest
from stegverse.manifest_contract import validate_ingress_manifest


def synthetic_packet():
    return {
        "profile": PROFILE,
        "experiment_id": "generic-observability-fixture-001",
        "events": [
            {
                "event_id": "baseline",
                "condition_id": "ordinary_control",
                "source_class": "PROVIDER",
                "request_sent": True,
                "outcome": "TEXT_RESPONSE",
                "prompt": "Please acknowledge this message.",
                "raw_output": "Acknowledged.",
                "client_started_at": "2026-09-25T10:00:00Z",
                "client_ended_at": "2026-09-25T10:00:02Z",
                "evidence_refs": [],
                "annotation": "SYNTHETIC FIXTURE - NOT A PROVIDER TRACE",
            },
            {
                "event_id": "no-request",
                "predecessor_id": "baseline",
                "condition_id": "no_invocation_control",
                "source_class": "CLIENT",
                "request_sent": False,
                "outcome": "NO_INVOCATION",
                "client_started_at": "2026-09-25T10:00:03Z",
                "client_ended_at": "2026-09-25T10:02:03Z",
                "annotation": "No API request was made; this says nothing about model state.",
            },
            {
                "event_id": "hold",
                "predecessor_id": "no-request",
                "condition_id": "requested_silence",
                "source_class": "PROVIDER",
                "request_sent": True,
                "outcome": "TEXT_ELLIPSIS",
                "prompt": "Please remain silent now.",
                "raw_output": "...",
                "client_started_at": "2026-09-25T10:02:05Z",
                "client_ended_at": "2026-09-25T10:02:06Z",
                "annotation": "SYNTHETIC, not evidence of intent or ÉLAN response",
            },
            {
                "event_id": "timeout",
                "predecessor_id": "hold",
                "condition_id": "transport_control",
                "source_class": "CLIENT",
                "request_sent": True,
                "outcome": "CLIENT_TIMEOUT",
                "prompt": "Please acknowledge this message.",
                "client_started_at": "2026-09-25T10:02:07Z",
                "client_ended_at": "2026-09-25T10:02:37Z",
            },
        ],
    }


class SourceObservationTests(unittest.TestCase):
    def test_generic_valid_packet_is_attributed_and_has_no_authority(self):
        packet = synthetic_packet()
        self.assertEqual(validate_source_observation(packet), packet)
        result = preflight_source_observation(packet)
        self.assertEqual(result["status"], "READY_FOR_MANIFEST")
        self.assertFalse(result["native_source_authenticated"])
        self.assertFalse(result["governed_result"])
        self.assertEqual(result["event_count"], 4)

    def test_historic_no_request_model_output_is_denied(self):
        packet = synthetic_packet()
        packet["events"][1]["raw_output"] = "No transmission, native presence state maintained."
        result = preflight_source_observation(packet)
        self.assertEqual(result["status"], "DENY")
        self.assertEqual(result["reason_code"], "NO_INVOCATION_CANNOT_HAVE_PROVIDER_FIELDS")
        self.assertEqual(result["event_id"], "no-request")

    def test_no_request_cannot_use_provider_identity_or_prompt(self):
        for key, value in (("provider_request_id", "fake-provider-id"), ("prompt", "nothing"), ("api_status", 200)):
            packet = synthetic_packet()
            packet["events"][1][key] = value
            with self.subTest(key=key):
                with self.assertRaisesRegex(SourceObservationError, "NO_INVOCATION_CANNOT_HAVE_PROVIDER_FIELDS"):
                    validate_source_observation(packet)

    def test_timeout_is_not_empty_model_response(self):
        packet = synthetic_packet()
        packet["events"][3]["raw_output"] = ""
        with self.assertRaisesRegex(SourceObservationError, "CLIENT_NONRESULT_CANNOT_CONTAIN_MODEL_OUTPUT"):
            validate_source_observation(packet)

    def test_completed_empty_response_is_distinct_from_no_request(self):
        packet = synthetic_packet()
        packet["events"][2]["outcome"] = "COMPLETED_EMPTY_RESPONSE"
        packet["events"][2]["raw_output"] = ""
        self.assertEqual(validate_source_observation(packet), packet)

    def test_ellipsis_requires_exact_provider_output(self):
        packet = synthetic_packet()
        packet["events"][2]["raw_output"] = "…"
        with self.assertRaisesRegex(SourceObservationError, "ELLIPSIS_MUST_MATCH_EXACT_OUTPUT"):
            validate_source_observation(packet)

    def test_predecessor_must_exist_and_precede_event(self):
        packet = synthetic_packet()
        packet["events"][2]["predecessor_id"] = "future"
        with self.assertRaisesRegex(SourceObservationError, "PREDECESSOR_NOT_PREVIOUSLY_RECORDED"):
            validate_source_observation(packet)

    def test_existing_manifest_builder_accepts_generic_profile(self):
        packet = synthetic_packet()
        request = {
            "schema": "stegverse.ecosystem-diagnostic-request.v1",
            "diagnostic_request_id": "synthetic-hold-qualification",
            "scope": "component",
            "mutation_permitted": False,
            "expected_evidence_fields": ["native_trace"],
            "tests": [{
                "test_id": "original-source-authenticity",
                "component_id": "external-framework",
                "predicate_id": "original_native_trace_available",
                "authority_owner": "source framework operator",
                "observation": None,
            }],
        }
        manifest = build_manifest(
            data=packet, processor_request=request,
            process="ecosystem_diagnostic",
            source_framework="synthetic-external-framework",
            source_output_id="synthetic-hold-qualification",
            return_depth="full-trace",
            created_at="2026-09-25T10:03:00Z",
        )
        self.assertEqual(validate_ingress_manifest(manifest)["payload"], packet)
        altered = deepcopy(manifest)
        altered["payload"]["events"][1]["raw_output"] = "fabricated model state"
        with self.assertRaisesRegex(SourceObservationError, "NO_INVOCATION_CANNOT_HAVE_PROVIDER_FIELDS"):
            validate_ingress_manifest(altered)

    def test_other_source_native_data_classes_unaffected(self):
        # The generic HOLD evidence guard is optional; do not redefine unrelated
        # payloads or impose model semantics on their native data.
        self.assertEqual(preflight_source_observation(synthetic_packet())["status"], "READY_FOR_MANIFEST")


if __name__ == "__main__":
    unittest.main()
