from pathlib import Path
import inspect
from stegverse import purpose_bound_worker_processor as p


def test_group_overlap_uses_post_barrier_execution_interval_fields():
    source = inspect.getsource(p._execute_group)
    assert "barrier.wait(timeout=5)" in source
    assert source.index("barrier.wait(timeout=5)") < source.index("execution_started_ns = time.monotonic_ns()")
    assert "execution_completed_ns = time.monotonic_ns()" in source
    assert 'max(row["execution_started_ns"] for row in workers)' in source
    assert 'min(row["execution_completed_ns"] for row in workers)' in source
    assert '"started_ns"' not in source
    assert '"completed_ns"' not in source
