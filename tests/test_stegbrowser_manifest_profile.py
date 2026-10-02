from stegverse.manifest_builder import build_manifest
from stegverse.manifest_execution import execute_manifest
from stegverse.manifest_state_transition_runtime import derive_execution_request
from stegverse.route_resolution import STEGBROWSER_ROUTE_ID


def _request(worker):
    outbound = ("a" if worker == "A" else "b") * 64
    returned = ("c" if worker == "A" else "d") * 64
    return {
        "schema": "stegbrowser.llm-profile-request.v1",
        "profile": "llm.v1",
        "prompt": f"Return the exact marker TEST5_{worker} and identify this session.",
        "response_marker": f"TEST5_{worker}",
        "provider": "openai",
        "journey": {
            "schema": "stegverse.packet-carried-endpoint-receipt-journey/v1",
            "journey_id": f"test5-{worker.lower()}",
            "origin_endpoint": "stegverse:test5-origin",
            "ephemeral_endpoint": f"stegbrowser:ephemeral:{worker.lower()}",
            "outbound_manifest_sha256": f"sha256:{outbound}",
            "return_manifest_sha256": f"sha256:{returned}",
            "return_predecessor_manifest_sha256": f"sha256:{outbound}",
        },
    }


def _manifest(worker):
    return build_manifest(
        data={"test": 5, "worker": worker},
        data_class="stegverse.sdk-test.v1",
        source_framework="StegVerse-SDK-Evaluator",
        source_output_id=f"test5-{worker.lower()}",
        processor_request=_request(worker),
        process="stegbrowser",
        return_depth="full-trace",
        publisher_required=False,
    )


def test_test5_two_workers_use_same_generic_run_manifest_route():
    a, b = _manifest("A"), _manifest("B")
    for manifest in (a, b):
        assert manifest["processing"] == {"capability": "stegbrowser", "route_id": STEGBROWSER_ROUTE_ID}
        req = derive_execution_request(manifest)
        assert req["processing_capability"] == "stegbrowser"
        assert req["state_graph"]["capability"] == "StegBrowser"
        assert req["state_graph"]["profile"] == "llm.v1"
        assert req["state_graph"]["endpoint_receipt_journey"]["custody_order"] == [
            "ORGANIZATION_RECORDS", "MASTER_RECORDS"
        ]
        assert req["state_graph"]["endpoint_receipt_journey"]["branch_count"] == 1
        assert req["state_graph"]["endpoint_receipt_journey"]["required_order"] == [
            {"branch_id": "1", "leg": 1, "direction": "EGRESS"},
            {"branch_id": "1", "leg": 1, "direction": "INGRESS"},
            {"branch_id": "1", "leg": 2, "direction": "EGRESS"},
            {"branch_id": "1", "leg": 2, "direction": "INGRESS"},
        ]
    assert derive_execution_request(a)["canonical_manifest_sha256"] != derive_execution_request(b)["canonical_manifest_sha256"]


def test_test5_run_manifest_waits_for_canonical_organization_endpoint_mapping(monkeypatch):
    monkeypatch.delenv("STEGVERSE_UNIVERSAL_INTR_INGRESS_URL", raising=False)
    monkeypatch.delenv("STEGVERSE_TVC_RELAY_AUTHORIZATION_ID", raising=False)
    result = execute_manifest(_manifest("A"))
    assert result["disposition"] == "FAIL_CLOSED"
    assert result["state"] == "FAIL_CLOSED"
    assert result["processing_capability"] == "stegbrowser"
    assert result["canonical_task_id"] == "EPHEMERAL-STEGBROWSER-EXTERNAL-AI-ACTIVATION-001"
    assert result["evaluation_boundary"] == "SDK_ORGANIZATION_DESTINATION_RESOLUTION"
    assert result["destination_resolution_source"] == "CANONICAL_CONNECTOR_CAPABILITY_OVERLAY"
    assert result["connector_profile_id"] == "sdk-manifest-ingress"
    assert result["connector_destination_subsystem"] == "SDK:ManifestIngress"
    assert result["completion_egress_controls_outbound_organization_routing"] is False
    assert result["consequence_committed"] is False

