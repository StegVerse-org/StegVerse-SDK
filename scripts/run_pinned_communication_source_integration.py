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
    parser = argparse.ArgumentParser(description="Run pinned live-source StegTalk + KnowledgeVault integration proof")
    parser.add_argument("--stegtalk-repo", required=True)
    parser.add_argument("--kv-repo", required=True)
    args = parser.parse_args()

    stegtalk_repo = Path(args.stegtalk_repo).resolve()
    kv_repo = Path(args.kv_repo).resolve()
    sys.path.insert(0, str(stegtalk_repo / "src"))
    sys.path.insert(0, str(kv_repo))

    from stegtalk.cross_edge_resolver import (  # type: ignore
        fallback_action,
        issue_execution_lease,
        resolve_cross_edge_path,
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

    ambiguous = fallback_action(outcome="TIMEOUT_AFTER_DISPATCH", selection_receipt=selection)
    assert ambiguous["action"] == "VERIFY_EXTERNALLY"
    confirmed_failure = fallback_action(
        outcome="FAILED",
        selection_receipt=selection,
        side_effect_absence_confirmed=True,
    )
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
            },
        )

        restarted = KnowledgeVaultExecutionStore(vault_root)
        restored_receipts = restarted.read_stream("Receipts", "source-integration-001")
        restored_attempts = restarted.read_stream("Attempts", "source-integration-001")
        assert restored_receipts == [selection]
        assert restored_attempts[0]["selection_sha256"] == selection["selection_sha256"]
        assert restored_attempts[0]["lease_epoch"] == 1

    result = {
        "proof_type": "PINNED_SOURCE_COMMUNICATION_INTEGRATION",
        "stegtalk_source_loaded": True,
        "knowledgevault_source_loaded": True,
        "selected_edge_id": selection["selected_edge_id"],
        "selected_bearer": selection["selected_bearer"],
        "fallback_edge_id": selection["fallback_order"][0]["edge_id"],
        "ambiguous_action": ambiguous["action"],
        "confirmed_failure_action": confirmed_failure["action"],
        "kv_receipt_reconstructed_after_restart": True,
        "kv_lease_reconstructed_after_restart": True,
        "selection_sha256": selection["selection_sha256"],
        "runtime_execution_performed": False,
        "physical_transport_proven": False,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
