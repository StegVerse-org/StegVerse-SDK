#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from dataclasses import asdict
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
    parser = argparse.ArgumentParser(description="Run pinned StegTalk ST-031/ST-032 + KnowledgeVault native runtime-journal proof")
    parser.add_argument("--stegtalk-repo", required=True)
    parser.add_argument("--kv-repo", required=True)
    args = parser.parse_args()

    stegtalk_repo = Path(args.stegtalk_repo).resolve()
    kv_repo = Path(args.kv_repo).resolve()
    sys.path.insert(0, str(stegtalk_repo / "src"))
    sys.path.insert(0, str(kv_repo))

    from stegtalk.cross_edge_resolver import issue_execution_lease, resolve_cross_edge_path  # type: ignore
    from stegtalk.edge_runtime import (  # type: ignore
        EdgeExecutionRequest,
        execute_selected_edge,
        loopback_test_executor,
        next_runtime_action,
        receipt_as_record,
    )
    from execution.communication_runtime import CommunicationRuntimeJournal  # type: ignore
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

    lease_record = asdict(lease)
    execution_record = receipt_as_record(execution_receipt)

    with tempfile.TemporaryDirectory() as tmp:
        vault_root = Path(tmp) / "KnowledgeVault"
        journal = CommunicationRuntimeJournal(KnowledgeVaultExecutionStore(vault_root))
        stream_id = journal.begin(selection=selection, lease=lease_record)
        journal.record_execution(selection=selection, lease=lease_record, receipt=execution_record)
        # The durable KV layer must also suppress replay of the same exact observed receipt.
        journal.record_execution(selection=selection, lease=lease_record, receipt=execution_record)
        journal.record_recovery(
            attempt_id=selection["attempt_id"],
            decision={
                "action": ambiguous["action"],
                "reason": ambiguous["reason"],
                "new_authority_granted": False,
            },
        )

        restarted = CommunicationRuntimeJournal(KnowledgeVaultExecutionStore(vault_root))
        recovered = restarted.recover(selection["attempt_id"])
        assert recovered.selection == selection
        assert recovered.lease == lease_record
        assert recovered.execution_receipt == execution_record
        assert recovered.recovery_records[0]["action"] == "VERIFY_EXTERNALLY"
        attempts = restarted.store.read_stream("Attempts", stream_id)
        execution_observations = [row for row in attempts if row.get("record_type") == "EDGE_EXECUTION_OBSERVED"]
        assert len(execution_observations) == 1

    result = {
        "proof_type": "PINNED_SOURCE_COMMUNICATION_NATIVE_KV_RUNTIME_INTEGRATION",
        "stegtalk_source_loaded": True,
        "stegtalk_st031_loaded": True,
        "stegtalk_st032_loaded": True,
        "knowledgevault_source_loaded": True,
        "knowledgevault_native_runtime_journal_loaded": True,
        "selected_edge_id": selection["selected_edge_id"],
        "selected_bearer": selection["selected_bearer"],
        "fallback_edge_id": selection["fallback_order"][0]["edge_id"],
        "edge_runtime_callable_executed": True,
        "edge_execution_outcome": execution_receipt.outcome,
        "edge_execution_receipt_sha256": execution_receipt.receipt_sha256,
        "edge_duplicate_dispatch_suppressed": duplicate_receipt == execution_receipt,
        "kv_duplicate_execution_observation_suppressed": True,
        "ambiguous_action": ambiguous["action"],
        "confirmed_failure_action": confirmed_failure["action"],
        "kv_selection_reconstructed_after_restart": True,
        "kv_lease_reconstructed_after_restart": True,
        "kv_edge_execution_receipt_reconstructed_after_restart": True,
        "kv_recovery_decision_reconstructed_after_restart": True,
        "selection_sha256": selection["selection_sha256"],
        "loopback_test_only": True,
        "physical_transport_proven": False,
        "production_activation_proven": False,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
