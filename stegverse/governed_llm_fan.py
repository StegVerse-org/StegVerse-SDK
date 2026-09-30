"""Execute an N-branch LLM fan from the SDK, with no worker in the path.

Test 6's shape is several workers, each calling a different LLM, answering one
question. Until now the fan was executed by a GitHub Actions worker in
StegVerse-Labs/.github, which translated the v2 journey into one v1 round trip
per branch, minted an ephemeral lease for each, and called the StegBrowser
owner. None of that is authority: it is translation, lease data and
orchestration, so it belongs where the capability is offered rather than in CI.

This module does that work in the SDK. The branch requests it produces are
byte-identical to the worker's, so a packet replays the same either way.

What it does not do is execute a browser. The LLM interaction stays with the
StegBrowser owner, reached through an injected executor with StegBrowser's own
`(request, lease)` signature, so that owner needs no adapter and no browser
semantics enter the SDK. When no executor is supplied the installed
``stegbrowser`` package is used; if it is absent this fails closed naming the
dependency rather than reaching into a sibling checkout.

Non-authorizing. Producing components and receipts is not admission: nothing
here grants execution authority, and a fan that fails part way reports what
completed instead of presenting an incomplete packet as whole.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json
from typing import Any, Callable, Dict, List, Mapping, Optional
from urllib.parse import urlsplit

from .stegbrowser_processor import derive_state_graph

FAN_RESULT_SCHEMA = "stegverse.governed-llm-fan-result/v1"
LEASE_SCHEMA = "stegbrowser.ecosystem-ephemeral-lease.v1"
BRANCH_REQUEST_SCHEMA = "stegbrowser.llm-profile-request.v1"
JOURNEY_V1 = "stegverse.packet-carried-endpoint-receipt-journey/v1"
PROFILE = "llm.v1"

#: Four endpoint receipts per branch: origin EGRESS, ephemeral INGRESS,
#: ephemeral EGRESS on the predecessor-linked return manifest, origin INGRESS.
RECEIPTS_PER_BRANCH = 4

#: StegBrowser's own signature, so the owner is passed in unwrapped.
BranchExecutor = Callable[[Mapping[str, Any], Mapping[str, Any]], Mapping[str, Any]]

STATUS_COMPLETED = "COMPLETED"
STATUS_FAILED = "FAILED"
STATUS_NOT_ATTEMPTED = "NOT_ATTEMPTED"

FAILURE_EXECUTOR_UNAVAILABLE = "STEGBROWSER_EXECUTOR_UNAVAILABLE"
FAILURE_BRANCH_EXECUTION = "BRANCH_LLM_INTERACTION_DID_NOT_COMPLETE"
FAILURE_BRANCH_RESULT_SHAPE = "BRANCH_EXECUTOR_RETURNED_UNRECOGNIZED_RESULT"

EXECUTOR_REPAIR = (
    "install the stegbrowser package into this environment, or pass "
    "executor= with StegBrowser's execute_manifested_llm_browser_operation"
)


class GovernedLlmFanError(RuntimeError):
    """Raised when a fan cannot be attempted at all."""


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256(value: Any) -> str:
    return "sha256:" + sha256(_canonical(value).encode("utf-8")).hexdigest()


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _stamp(moment: datetime) -> str:
    return moment.isoformat().replace("+00:00", "Z")


def branch_operations(graph: Mapping[str, Any]) -> List[Dict[str, Any]]:
    """Project a state graph's journey into one v1 round trip per branch.

    A v2 journey fans to N parallel branches; v1 describes exactly one round
    trip, which is what the StegBrowser owner executes. Each branch's
    journey_id is qualified by its branch id, so the four receipts a branch
    produces are attributable to it and cannot be mistaken for another's --
    and that qualified id is what binds the components at composition time.
    """
    request = graph.get("request")
    if not isinstance(request, Mapping):
        raise GovernedLlmFanError("state graph carries no StegBrowser request")
    journey = request.get("journey") if isinstance(request.get("journey"), Mapping) else {}
    origin = journey.get("origin_endpoint")
    branches = graph.get("branches")
    if not isinstance(branches, list) or not branches:
        # A graph built before the journey generalized carries the round trip at
        # request level; it is the single-branch case.
        return [dict(request)]

    journey_id = journey.get("journey_id")
    operations: List[Dict[str, Any]] = []
    for branch in branches:
        if not isinstance(branch, Mapping):
            raise GovernedLlmFanError("each journey branch must be an object")
        outbound = branch.get("outbound_manifest_sha256")
        operations.append({
            "schema": BRANCH_REQUEST_SCHEMA,
            "profile": PROFILE,
            "prompt": branch.get("prompt"),
            "response_marker": branch.get("response_marker"),
            "provider": branch.get("provider"),
            "model": branch.get("model"),
            "secure_url": branch.get("secure_url"),
            "browser_actions": branch.get("browser_actions"),
            "journey": {
                "schema": JOURNEY_V1,
                "journey_id": f"{journey_id}:{branch.get('branch_id')}",
                "origin_endpoint": origin,
                "ephemeral_endpoint": branch.get("ephemeral_endpoint"),
                "outbound_manifest_sha256": outbound,
                "return_manifest_sha256": branch.get("return_manifest_sha256"),
                "return_predecessor_manifest_sha256": outbound,
            },
        })
    return operations


def mint_branch_lease(
    operation: Mapping[str, Any],
    *,
    fan_id: str,
    index: int,
    requester: str,
    ttl_minutes: int = 10,
) -> Dict[str, Any]:
    """Return one branch's ephemeral lease.

    Each branch leases its own session: no branch reuses another's, nothing
    persists, and the lease is scoped to the single host the manifest named.
    """
    host = (urlsplit(str(operation.get("secure_url") or "")).hostname or "").lower()
    issued = _utc_now()
    return {
        "schema": LEASE_SCHEMA,
        "lease_id": f"sdk-{fan_id[:20]}-{index}",
        "task_id": fan_id,
        "requester": requester,
        "purpose": "manifest-selected credential-free llm.v1 browser operation",
        "issued_at": _stamp(issued),
        "expires_at": _stamp(issued + timedelta(minutes=ttl_minutes)),
        "allowed_origins": [host],
        "allowed_actions": ["navigate", "read_public", "submit_form"],
        "retain_artifacts": ["navigation_receipt", "content_commitment", "governance_receipt"],
        "max_navigations": 4,
        "persistent_profile": False,
        "persist_cookies": False,
        "persist_history": False,
    }


def _resolve_executor(executor: Optional[BranchExecutor]) -> BranchExecutor:
    if executor is not None:
        return executor
    try:  # the installed owner package, never a sibling checkout
        from stegbrowser.llm_browser_execution import (  # type: ignore[import-not-found]
            execute_manifested_llm_browser_operation,
        )
    except ImportError as exc:
        raise GovernedLlmFanError(f"{FAILURE_EXECUTOR_UNAVAILABLE}: {EXECUTOR_REPAIR}") from exc
    return execute_manifested_llm_browser_operation


def run_governed_llm_fan(
    manifest: Mapping[str, Any],
    *,
    executor: Optional[BranchExecutor] = None,
    requester: str = "SDK:EcosystemChat",
    lease_ttl_minutes: int = 10,
) -> Dict[str, Any]:
    """Run every branch of a manifest's fan and return its components.

    The components are ``stegbrowser.llm-profile-result.v1`` results, in branch
    order, ready for compose_governed_response. A branch that fails does not
    discard the branches already executed: their receipts are kept and the fan
    reports itself incomplete, because an incomplete packet presented as whole
    is worse than a fan that says where it stopped.
    """
    graph = derive_state_graph(manifest)
    operations = branch_operations(graph)
    journey = graph["request"]["journey"]
    fan_journey_id = str(journey["journey_id"])
    fan_id = _sha256(graph["request"])[7:27]

    run = _resolve_executor(executor)

    components: List[Dict[str, Any]] = []
    receipts: List[Dict[str, Any]] = []
    branch_rows: List[Dict[str, Any]] = []
    failure: Optional[Dict[str, Any]] = None

    for index, operation in enumerate(operations, start=1):
        branch_id = str(operation["journey"]["journey_id"]).rsplit(":", 1)[-1]
        host = (urlsplit(str(operation.get("secure_url") or "")).hostname or "").lower()
        if failure is not None:
            branch_rows.append({
                "branch_id": branch_id, "branch_index": index,
                "status": STATUS_NOT_ATTEMPTED, "secure_url_host": host,
            })
            continue

        lease = mint_branch_lease(
            operation, fan_id=fan_id, index=index,
            requester=requester, ttl_minutes=lease_ttl_minutes,
        )
        try:
            outcome = run(operation, lease)
        except Exception as exc:  # the owner boundary fails closed
            failure = {
                "failure_code": FAILURE_BRANCH_EXECUTION,
                "failed_predicate": "MANIFEST_SELECTED_STEGBROWSER_BROWSER_OPERATION_COMPLETED",
                "branch_id": branch_id,
                "branch_index": index,
                "branches_completed": len(components),
                "error_type": type(exc).__name__,
                "error_message": str(exc)[:1000],
                "required_evidence_or_repair": (
                    "repair the StegBrowser owner or the manifest's branch data, "
                    "then retry the same manifest"
                ),
                "retry_entrypoint": "stegverse.governed_llm_fan.run_governed_llm_fan",
            }
            branch_rows.append({
                "branch_id": branch_id, "branch_index": index,
                "status": STATUS_FAILED, "secure_url_host": host,
            })
            continue

        if not isinstance(outcome, Mapping) or not isinstance(outcome.get("result"), Mapping):
            failure = {
                "failure_code": FAILURE_BRANCH_RESULT_SHAPE,
                "failed_predicate": "BRANCH_EXECUTOR_RETURNED_A_PROFILE_RESULT",
                "branch_id": branch_id,
                "branch_index": index,
                "branches_completed": len(components),
                "required_evidence_or_repair": (
                    "the executor must return {'result': <llm-profile-result.v1>, "
                    "'endpoint_receipts': [...]}"
                ),
                "retry_entrypoint": "stegverse.governed_llm_fan.run_governed_llm_fan",
            }
            branch_rows.append({
                "branch_id": branch_id, "branch_index": index,
                "status": STATUS_FAILED, "secure_url_host": host,
            })
            continue

        result = dict(outcome["result"])
        branch_receipts = list(outcome.get("endpoint_receipts") or [])
        components.append(result)
        receipts.extend(branch_receipts)
        branch_rows.append({
            "branch_id": branch_id,
            "branch_index": index,
            "status": STATUS_COMPLETED,
            "secure_url_host": host,
            "provider": result.get("provider"),
            "model": result.get("model"),
            "journey_id": result.get("journey_id"),
            "response_commitment": result.get("response_commitment"),
            "endpoint_receipt_count": len(branch_receipts),
        })

    required = RECEIPTS_PER_BRANCH * len(operations)
    fan: Dict[str, Any] = {
        "schema": FAN_RESULT_SCHEMA,
        "fan_journey_id": fan_journey_id,
        "branch_count": len(operations),
        "components": components,
        "component_count": len(components),
        "endpoint_receipts": receipts,
        "required_endpoint_receipts": required,
        "observed_endpoint_receipts": len(receipts),
        "branches": branch_rows,
        "complete": (
            failure is None
            and len(components) == len(operations)
            and len(receipts) == required
        ),
        "failure": failure,
        # The point of this module: the fan runs where the capability is offered.
        "worker_in_path": False,
        "executor_supplied_by_caller": executor is not None,
        "boundary": {
            "fan_executes_a_browser": False,
            "fan_grants_execution_authority": False,
            "fan_is_admission": False,
            "partial_fan_presented_as_complete": False,
        },
    }
    fan["fan_sha256"] = _sha256(fan)
    return fan


__all__ = [
    "BRANCH_REQUEST_SCHEMA", "BranchExecutor", "EXECUTOR_REPAIR",
    "FAILURE_BRANCH_EXECUTION", "FAILURE_BRANCH_RESULT_SHAPE",
    "FAILURE_EXECUTOR_UNAVAILABLE", "FAN_RESULT_SCHEMA", "GovernedLlmFanError",
    "LEASE_SCHEMA", "RECEIPTS_PER_BRANCH", "STATUS_COMPLETED", "STATUS_FAILED",
    "STATUS_NOT_ATTEMPTED", "branch_operations", "mint_branch_lease",
    "run_governed_llm_fan",
]
