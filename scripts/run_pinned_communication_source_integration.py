#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


def _edge(edge_id: str, bearer: str, score: float) -> dict:
    return {
        "edge_id": edge_id,
        "advertisement_id": f"adv:{edge_id}:1",
        "observed_at": "2026-08-22T22:30:00Z",
        "expires_at": "2026-08-22T23:30:00Z",
        "attested": True,
        "available_bearers": [bearer],
        "metrics": {
            "security": score,
            "privacy": score,
            "recipient_compatibility": score,
            "reliability": score,
            "receipt_quality": score,
            "bidirectionality": score,
            "resilience": score,
            "latency": score,
            "bandwidth": score,
            "cost": score,
            "energy": score,
            "metadata_minimization": score,
        },
        "capabilities": {
            "local_bearers": [],
            "requires_relay": False,
            "store_and_forward": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run pinned live-source StegTalk ST-031/ST-032 + KnowledgeVault integration proof")
    parser.add_argument("--stegtalk-repo", required=True)
    parser.add_argument("--kv-repo", required=True)
    args = parser.parse_args()

    stegtalk_repo = Path(args.stegtalk_repo).resolve()
    kv_repo = Path(args.kv_repo).resolve()
    sys.path.insert(0, str(stegtalk_repo / "src"))
    sys.path.insert(0, str(kv_repo))

    from stegtalk.cross_edge_resolver import (  # type: ignore
        issue_execution_lease,
        resolve_cross_edge_path,
    )
    from stegtalk.edge_runtime import (  # type: ignore
        EdgeExecutionRequest,
        execute_selected_edge,
        loopback_test_executor,
        next_runtime_action,
        receipt_as_record,
    )
    from execution.vault_store import KnowledgeVaultExecutionStore  # type: ignore

    now = datetime(2026, 8, 22, 22, 35, tzinfo=timezone.utc)
    selection = resolve_cross_edge_path(
        attempt_id="source-integration:001",
        posture="AUTO",
        edge_advertisements=[
            _edge("source-integration:gateway", "stegtalk-ip", 0.95),
            _edge("source-integration:phone", "sms", 0.55),
        ],
        recipient={"state": "KNOWN", "accepted_bearers": ["stegtalk-ip", "sms"]},
        constraints={
            "remote_edge_execution_authorized": True,
            "multipath_authorized": False,
            "relay_permission": "allowed",
            "allow_store_and_forward": True,
            "bearer_preference": ["stegtalk-ip", "sms"],
        },
        policy_version="stegtalk.cross-edge.v0.1",
        now=now,
    )
    assert selection["selected_edge_id"] == "source-integration:gateway"
    assert selection["selected_bearer"] == "stegtalk-ip"
    assert selection["fallback_order"][0]["edge_id"] == "source-integration:phone"

    lease = issue_execution_lease(
        attempt_id="source-integration:001",
        selection_receipt=selection,
        lease_epoch=1,
        expires_at="2026-08-22T22:45:00Z",
        now=now,
    )
    assert lease.edge_id == selection["selected_edge_id"]

    request = EdgeExecutionRequest(
        attempt_id=selection["attempt_id"],
        selection_sha256=selection["selection_sha256"],
        edge_id=selection["selected_edge_id"],
        bearer=selection["selected_bearer"],
        payload_ref="kv://source-integration/payload/001",
        idempotency_key="source-integration:001:dispatch:1",
        lease_epoch=lease.lease_epoch,
    )
    execution_cache = {}
    execution_receipt = execute_selected_edge(
        selection_receipt=selection,
        lease=lease,
        request=request,
        executors={selection["selected_edge_id"]: loopback_test_executor(outcome="DELIVERED")},
        execution_cache=execution_cache,
    )
    duplicate_receipt = execute_selected_edge(
        selection_receipt=selection,
        lease=lease,
        request=request,
        executors={selection["selected_edge_id"]: loopback_test_executor(outcome="FAILED", side_effect_absence_confirmed=True)},
        execution_cache=execution_cache,
    )
    assert duplicate_receipt == execution_receipt
    assert execution_receipt.outcome == "DELIVERED"
    assert next_runtime_action(selection_receipt=selection, receipt=execution_receipt)["action"] == "STOP"

    ambiguous_receipt = execute_selected_edge(
        selection_receipt=selection,
        lease=lease,
        request=EdgeExecutionRequest(
            attempt_id=selection["attempt_id"],
            selection_sha256=selection["selection_sha256"],
            edge_id=selection["selected_edge_id"],
            bearer=selection["selected_bearer"],
            payload_ref="kv://source-integration/payload/001",
            idempotency_key="source-integration:001:dispatch:ambiguous",
            lease_epoch=lease.lease_epoch,
        ),
        executors={selection["selected_edge_id"]: loopback_test_executor(outcome="TIMEOUT_AFTER_DISPATCH")},
    )
    ambiguous = next_runtime_action(selection_receipt=selection, receipt=ambiguous_receipt)
    assert ambiguous["action"] == "VERIFY_EXTERNALLY"

    failed_receipt = execute_selected_edge(
        selection_receipt=selection,
        lease=lease,
        request=EdgeExecutionRequest(
            attempt_id=selection["attempt_id"],
            selection_sha256=selection["selection_sha256"],
            edge_id=selection["selected_edge_id"],
            bearer=selection["selected_bearer"],
            payload_ref="kv://source-integration/payload/001",
            idempotency_key="source-integration:001:dispatch:failed",
            lease_epoch=lease.lease_epoch,
        ),
        executors={selection["selected_edge_id"]: loopback_test_executor(outcome="FAILED", side_effect_absence_confirmed=True)},
    )
    confirmed_failure = next_runtime_action(selection_receipt=selection, receipt=failed_receipt)
    assert confirmed_failure["action"] == "TRY_FALLBACK"
    assert confirmed_failure["fallback"]["edge_id"] == "source-integration:phone"

    with tempfile.TemporaryDirectory() as tmp:
        vault_root = Path(tmp) / "KnowledgeVault"
        store = KnowledgeVaultExecutionStore(vault_root)
        store.append_receipt("source-integration-001", selection)
        store.append_attempt(
            "source-integration-001",
            {
                "attempt_id": lease.attempt_id,
                "selected_edge_id": lease.edge_id,
                "lease_epoch": lease.lease_epoch,
                "lease_expires_at": lease.expires_at,
                "selection_sha256": selection["selection_sha256"],
                "dispatch_state": "LEASED",
            },
        )
        store.append_receipt("source-integration-001", receipt_as_record(execution_receipt))
        store.append_attempt(
            "source-integration-001",
            {
                "attempt_id": lease.attempt_id,
                "selected_edge_id": lease.edge_id,
                "lease_epoch": lease.lease_epoch,
                "selection_sha256": selection["selection_sha256"],
                "edge_execution_receipt_sha256": execution_receipt.receipt_sha256,
                "dispatch_state": execution_receipt.dispatch_state,
                "outcome": execution_receipt.outcome,
            },
        )

        restarted = KnowledgeVaultExecutionStore(vault_root)
        restored_receipts = restarted.read_stream("Receipts", "source-integration-001")
        restored_attempts = restarted.read_stream("Attempts", "source-integration-001")
        assert restored_receipts[0] == selection
        assert restored_receipts[1]["receipt_sha256"] == execution_receipt.receipt_sha256
        assert restored_attempts[0]["selection_sha256"] == selection["selection_sha256"]
        assert restored_attempts[0]["lease_epoch"] == 1
        assert restored_attempts[1]["edge_execution_receipt_sha256"] == execution_receipt.receipt_sha256
        assert restored_attempts[1]["outcome"] == "DELIVERED"

    result = {
        "proof_type": "PINNED_SOURCE_COMMUNICATION_RUNTIME_INTEGRATION",
        "stegtalk_source_loaded": True,
        "stegtalk_st031_loaded": True,
        "stegtalk_st032_loaded": True,
        "knowledgevault_source_loaded": True,
        "selected_edge_id": selection["selected_edge_id"],
        "selected_bearer": selection["selected_bearer"],
        "fallback_edge_id": selection["fallback_order"][0]["edge_id"],
        "edge_runtime_callable_executed": True,
        "edge_execution_outcome": execution_receipt.outcome,
        "edge_execution_receipt_sha256": execution_receipt.receipt_sha256,
        "duplicate_dispatch_suppressed": duplicate_receipt == execution_receipt,
        "ambiguous_action": ambiguous["action"],
        "confirmed_failure_action": confirmed_failure["action"],
        "kv_receipt_reconstructed_after_restart": True,
        "kv_lease_reconstructed_after_restart": True,
        "kv_edge_execution_receipt_reconstructed_after_restart": True,
        "selection_sha256": selection["selection_sha256"],
        "loopback_test_only": True,
        "physical_transport_proven": False,
        "production_activation_proven": False,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
