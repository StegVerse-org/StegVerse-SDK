"""No transition path waits on a receiver (data/task-registry-global-invariants.json).

external_machine_awaiting_allowed=false and destination_liveness_is_transition_predicate=false:
nothing in the SDK runtime or its scripts may sleep, poll, retry until something answers, run
a resident listener, or treat a destination's reachability as the condition for a transition.
A receiver that is unavailable is DURABLE_QUEUE_OR_EVENT_EPHEMERAL_MATERIALIZATION with the six
fields, not a wait.

This scan fails on any such pattern in stegverse/ or scripts/ unless ALLOWLIST names the file,
the pattern and why it is not a transition predicate (SDK#484 V-P1, RESPONSE-064). An allowlist
entry whose pattern no longer occurs also fails, so the list cannot go stale.
"""
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCANNED = ("stegverse", "scripts")

PATTERNS = {
    "SLEEP": re.compile(r"\b(?:time|asyncio)\.sleep\("),
    "UNBOUNDED_LOOP": re.compile(r"^\s*while\s+True\s*:"),
    "BLOCKING_WAIT": re.compile(r"\.wait\(\s*timeout\s*="),
    "RESIDENT_LISTENER": re.compile(r"\bserve_forever\(|\bHTTPServer\b|\bsocketserver\.|\.listen\("),
    "RETRY_UNTIL_ALIVE": re.compile(r"\b(?:backoff|retry_until|until_alive|wait_until|poll_until)\b"),
    "LIVENESS_PROBE": re.compile(r"/(?:healthz|readyz|livez)\b"),
}

# (path, pattern) -> (occurrences, justification). Every entry is a reviewed non-predicate.
ALLOWLIST = {
    ("stegverse/purpose_bound_worker_processor.py", "SLEEP"): (
        1, "local observation dwell inside one process's concurrency measurement; no external receiver"),
    ("stegverse/purpose_bound_worker_processor.py", "BLOCKING_WAIT"): (
        2, "threading.Barrier between local worker threads of one process; no external receiver"),
    ("stegverse/purpose_bound_worker_cost_demo.py", "BLOCKING_WAIT"): (
        1, "threading.Barrier between three local worker threads of one demo process; no external receiver"),
    ("stegverse/mcp_cli.py", "UNBOUNDED_LOOP"): (
        1, "interactive menu prompt; EOF fails with an explicit message; not a transition path"),
    ("stegverse/mcp_transport.py", "BLOCKING_WAIT"): (
        2, "child-process cleanup in __exit__ (terminate, then kill); not a receiver wait"),
    ("scripts/inspect_remaining_deepwiki_citations.py", "UNBOUNDED_LOOP"): (
        1, "regex continuation parse loop over a string; terminates on no match"),
    ("scripts/run_ecosystem_chat_service.py", "RESIDENT_LISTENER"): (
        2, "local verification runner bounded by --max-requests (default 1, resident_process False; .github #98-D3)"),
    ("stegverse/llm_connection.py", "LIVENESS_PROBE"): (
        4, "descriptor endpoint strings (2) and the evidence-only adapter probe (2); a declared destination is "
           "never gated on it (llm_connect_cli, SDK#552 7b3b14b)"),
}


def _hits() -> Counter:
    found: Counter = Counter()
    for top in SCANNED:
        for path in sorted((ROOT / top).rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            rel = path.relative_to(ROOT).as_posix()
            for line in path.read_text(encoding="utf-8").splitlines():
                code = line.split("#", 1)[0]
                if not code.strip():
                    continue
                for name, pattern in PATTERNS.items():
                    if pattern.search(code):
                        found[(rel, name)] += 1
    return found


def test_no_unjustified_receiver_wait_on_any_path():
    unjustified = {key: count for key, count in _hits().items() if key not in ALLOWLIST}
    assert unjustified == {}, (
        "FAIL_CLOSED NO_EXTERNAL_MACHINE_AWAITING_AS_TRANSITION_PREDICATE: convert each hit to a six-field "
        "DURABLE_QUEUE_OR_EVENT_EPHEMERAL_MATERIALIZATION disposition, or justify it in ALLOWLIST: "
        f"{unjustified}")


def test_allowlist_counts_match_and_no_entry_is_stale():
    hits = _hits()
    mismatched = {key: (hits.get(key, 0), count) for key, (count, _) in ALLOWLIST.items() if hits.get(key, 0) != count}
    assert mismatched == {}, f"allowlist (found, allowed) mismatch; re-review these entries: {mismatched}"
    assert all(len(reason) > 20 for _, reason in ALLOWLIST.values())


def test_the_guard_catches_each_prohibited_pattern():
    samples = {
        "SLEEP": "    time.sleep(5)",
        "UNBOUNDED_LOOP": "    while True:",
        "BLOCKING_WAIT": "    event.wait(timeout=30)",
        "RESIDENT_LISTENER": "    server.serve_forever()",
        "RETRY_UNTIL_ALIVE": "    retry_until(receiver_up)",
        "LIVENESS_PROBE": '    urlopen(base + "/healthz")',
    }
    for name, line in samples.items():
        assert PATTERNS[name].search(line), name
    assert not PATTERNS["SLEEP"].search("    # time.sleep(5)".split("#", 1)[0])
