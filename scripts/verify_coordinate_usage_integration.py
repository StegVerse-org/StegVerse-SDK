#!/usr/bin/env python3
from __future__ import annotations

from stegverse.coordinate_navigation import consume_navigation_envelope
from stegverse.session_usage_receipt import build_session_usage_receipt
from stegverse.transition_usage import TransitionUsageEvent, UsageMetric, build_usage_event


def main() -> int:
    registry = {
        "registry_version": "1.0.0",
        "coordinates": [{
            "coordinate_id": "ecosystem://runtime/micro-node-governance",
            "version": "1.0.0",
            "contract_ref": "examples/coordinates/runtime.micro-node-governance.json",
            "content_sha256": "a" * 64,
        }],
        "edges": [{
            "source": "ecosystem://runtime/micro-node-governance",
            "destination": "ecosystem://records/master-records",
            "authority_transfer": "NONE",
            "receipt_required": True,
        }],
    }
    envelope = {
        "envelope_version": "1.0.0",
        "navigation_id": "navigation-verification-001",
        "actor": "sdk:verification",
        "source_coordinate": "ecosystem://runtime/micro-node-governance",
        "destination_coordinate": "ecosystem://records/master-records",
        "context_refs": ["receipt:verification"],
        "authority_transfer": "NONE",
        "standing_transfer": "NONE",
        "delegation_transfer": "NONE",
        "data_transfer": "DECLARED_REFS_ONLY",
        "receipt_required": True,
        "commit_time_revalidation_required": True,
        "return_path": "ecosystem://runtime/micro-node-governance",
    }
    consumed = consume_navigation_envelope(envelope, registry)
    assert consumed["sdk_boundary"]["sdk_consumption_is_navigation_authority"] is False

    event = build_usage_event(TransitionUsageEvent(
        measurement_id="measurement-verification-001",
        session_id="session-verification-001",
        transition_id="transition-verification-001",
        entry_point="sdk",
        entry_point_role="TRANSPORT_AND_AGGREGATION",
        interaction_type="coordinate-navigation",
        metric_owner="sdk",
        measurement_source="sdk-verifier",
        evidence_class="MEASURED",
        metrics={"sdk_events": UsageMetric("1", "count", "MEASURED", "verification")},
        occurred_at="2026-07-18T00:00:00Z",
        receipt_refs=[consumed["consumer_sha256"]],
    ))
    receipt = build_session_usage_receipt([event])
    assert receipt["custody_posture"] == "HANDOFF_READY_NOT_CUSTODIED"
    assert receipt["authority_boundary"]["receipt_is_master_record_custody"] is False
    print("coordinate and usage integration verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
