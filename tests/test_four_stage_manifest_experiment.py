from concurrent.futures import ThreadPoolExecutor
import inspect
import threading

import pytest

from stegverse import manifest_execution as manifest_execution
from stegverse import purpose_bound_worker_processor as p
from stegverse.route_resolution import (
    ATOMIC_TASK_WORKER_ROUTE_ID,
    PURPOSE_BOUND_WORKER_ROUTE_ID,
    PUBLISHED_ROUTES,
)


def _worker_request(name: str) -> dict:
    return {
        "schema": "stegverse.sdk.tt-purpose-bound-worker.v1",
        "transition_cell": {
            "cell_id": name,
            "protocol_version": "test-v1",
            "pre_state": {"worker_live": False},
            "candidate": {
                "operation_id": name,
                "operation_class": "ARBITRARY_TRACKED_TASK",
                "purpose": "serialized negative control",
                "required_capability": "text.integrity_summary",
                "max_lifetime_seconds": 30,
                "payload": {"text": name},
            },
        },
    }


def test_group_overlap_measures_only_post_barrier_invocation_interval():
    source = inspect.getsource(p._execute_group)
    assert "invocation_barrier.wait(timeout=5)" in source
    assert source.index("invocation_barrier.wait(timeout=5)") < source.index(
        "invocation = _invoke_worker(worker_request)"
    )
    invoke_source = inspect.getsource(p._invoke_worker)
    assert invoke_source.index("execution_started_ns = time.monotonic_ns()") < invoke_source.index(
        "time.sleep(_GROUP_INVOCATION_OBSERVATION_DWELL_SECONDS)"
    )
    assert invoke_source.index("time.sleep(_GROUP_INVOCATION_OBSERVATION_DWELL_SECONDS)") < invoke_source.index(
        "packet = run_purpose_bound_worker(worker_request)"
    )
    assert invoke_source.index("packet = run_purpose_bound_worker(worker_request)") < invoke_source.index(
        "execution_completed_ns = time.monotonic_ns()"
    )


def test_serialized_invocation_negative_control_does_not_report_overlap():
    requests = [_worker_request(f"w{i}") for i in range(3)]
    barrier = threading.Barrier(len(requests))
    lock = threading.Lock()

    def invoke(req):
        barrier.wait(timeout=5)
        with lock:
            return p._invoke_worker(req)

    with ThreadPoolExecutor(max_workers=3) as pool:
        rows = list(pool.map(invoke, requests))

    assert p._intervals_overlap(rows) is False


def test_partition_is_disjoint_and_reconstructs_source_exactly():
    source = "StegVerse tracks this arbitrary evaluator-submitted task."
    parts = p._partition_text(source, 3)
    assert "".join(part["text"] for part in parts) == source
    assert parts[0]["start_char"] == 0
    assert parts[-1]["end_char"] == len(source)
    assert all(
        left["end_char"] == right["start_char"]
        for left, right in zip(parts, parts[1:])
    )


def test_group_result_binding_recomputation_detects_tamper():
    bindings = [
        {"partition_id": "A", "worker_id": "w1", "task_result_hash": "a", "records_packet_hash": "b"},
        {"partition_id": "B", "worker_id": "w2", "task_result_hash": "c", "records_packet_hash": "d"},
    ]
    commitment = p._group_result_commitment("task", 2, bindings)
    assert p._verify_group_result_binding(commitment, "task", 2, bindings) is True
    tampered = [dict(row) for row in bindings]
    tampered[1]["task_result_hash"] = "changed"
    assert p._verify_group_result_binding(commitment, "task", 2, tampered) is False


def test_local_semantic_worker_routes_are_not_declared_governed_runtime():
    assert PUBLISHED_ROUTES[PURPOSE_BOUND_WORKER_ROUTE_ID]["routing_surface"] == (
        "SDK_LOCAL_SEMANTIC_DEMONSTRATION"
    )
    assert PUBLISHED_ROUTES[ATOMIC_TASK_WORKER_ROUTE_ID]["routing_surface"] == (
        "SDK_LOCAL_SEMANTIC_DEMONSTRATION"
    )


@pytest.mark.parametrize(
    "binding",
    [
        "stegverse.purpose_bound_worker_processor.execute_manifest",
        "stegverse.atomic_task_worker_processor.execute_manifest",
    ],
)
def test_governed_runtime_guard_rejects_local_semantic_binding(binding):
    with pytest.raises(ValueError, match="AUTHENTIC_GOVERNED_RUNTIME_BINDING_REQUIRED"):
        manifest_execution._require_nonterminal_local_semantic_boundary(
            {"routing_surface": "STEGAGENTS_GOVERNED_RUNTIME"},
            binding,
        )
