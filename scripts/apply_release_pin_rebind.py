"""Apply a release-pin rebind request as one transition (SDK#484 V-P4(a), V-P7).

The request (.github/release-requests/*-pin-rebind-*.json) names an old and a new git pin and
the receipt the new pin must be bound to. Given the successor receipt, this verifies the chain
and rewrites every file that carries the pin, all or nothing:

1. the receipt binds the new pin as the component's source parent, and every other governed
   component keeps its current source parent;
2. optionally (--repo), the new pin descends from the old pin in a local clone;
3. each listed file holds the old pin exactly once, in its declared context;
4. after rewriting, pyproject.toml's governed-test pins verify against the receipt.

Without a receipt, or on any failed predicate, it prints the six-field FAIL_CLOSED and writes
nothing. Standard library only. --check verifies without writing.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from stegverse.release_dependency_alignment import (  # noqa: E402
    _release_component_executable_commits,
    verify_governed_test_dependency_alignment,
)

REQUEST_SCHEMA = "stegverse.sdk.release-pin-rebind-request.v1"


class RebindRefused(Exception):
    def __init__(self, request: Mapping[str, Any], failure_code: str, failed_predicate: str, detail: str):
        base = dict(request.get("unbound_disposition") or {})
        self.disposition = {
            "disposition": "FAIL_CLOSED",
            "failure_code": failure_code,
            "failed_predicate": failed_predicate,
            "required_evidence_or_repair": f"{detail}; {base.get('required_evidence_or_repair', '')}".rstrip("; "),
            "retry_entrypoint": base.get("retry_entrypoint") or request.get("command") or __file__,
            "owning_existing_goal": base.get("owning_existing_goal") or request.get("owning_existing_goal"),
            "next_attempt": base.get("next_attempt") or "rerun the command after the predicate holds",
            "authority_effect": "NONE",
        }
        super().__init__(json.dumps(self.disposition, sort_keys=True))


def governed_test_requirements(pyproject_text: str) -> list[str]:
    block = re.search(r"^governed-test\s*=\s*\[(.*?)\]", pyproject_text, re.S | re.M)
    if not block:
        return []
    return [f'{item} ; extra == "governed-test"' for item in re.findall(r'"([^"]+)"', block.group(1))]


def _ancestry_holds(repo: Path, old: str, new: str) -> bool:
    return subprocess.run(["git", "-C", str(repo), "merge-base", "--is-ancestor", old, new],
                          capture_output=True).returncode == 0


def plan(request: Mapping[str, Any], receipt: Mapping[str, Any] | None, root: Path = ROOT,
         repo: Path | None = None) -> dict[str, str]:
    """Return {path: new text} for the rebind, or raise RebindRefused with the six fields."""
    if request.get("schema") != REQUEST_SCHEMA:
        raise RebindRefused(request, "REBIND_REQUEST_INVALID", "REQUEST_IS_PIN_REBIND_V1", "unexpected request schema")
    old, new = request["old_pin"], request["new_pin"]
    if not all(re.fullmatch(r"[0-9a-f]{40}", pin) for pin in (old, new)) or old == new:
        raise RebindRefused(request, "REBIND_REQUEST_INVALID", "PINS_ARE_DISTINCT_40_HEX", f"{old} -> {new}")
    if receipt is None:
        raise RebindRefused(request, request["unbound_disposition"]["failure_code"],
                            request["unbound_disposition"]["failed_predicate"], "no successor receipt supplied")
    bound = _release_component_executable_commits(receipt)
    required = request["required_successor_receipt"]["components"]
    for repository, expected in required.items():
        if bound.get(repository) != expected["source_parent_commit"]:
            raise RebindRefused(request, "SUCCESSOR_RECEIPT_DOES_NOT_BIND_PIN", "RECEIPT_SOURCE_PARENTS_MATCH_REQUEST",
                                f"receipt binds {repository} to {bound.get(repository)}, request needs "
                                f"{expected['source_parent_commit']}")
    if repo is not None and not _ancestry_holds(repo, old, new):
        raise RebindRefused(request, "NEW_PIN_DOES_NOT_DESCEND_FROM_OLD", "OLD_PIN_IS_ANCESTOR_OF_NEW_PIN",
                            f"{old} is not an ancestor of {new} in {repo}")
    rewritten = {}
    for item in request["rewrites"]:
        path = root / item["path"]
        text = path.read_text(encoding="utf-8") if path.is_file() else ""
        if text.count(old) != 1:
            raise RebindRefused(request, "REBIND_TARGET_DRIFTED", "EACH_TARGET_HOLDS_OLD_PIN_EXACTLY_ONCE",
                                f"{item['path']} ({item['context']}) holds the old pin {text.count(old)} times")
        rewritten[item["path"]] = text.replace(old, new)
    requirements = governed_test_requirements(rewritten.get("pyproject.toml") or (root / "pyproject.toml").read_text())
    alignment = verify_governed_test_dependency_alignment(requirements, receipt)
    if not alignment["verified"]:
        raise RebindRefused(request, "REBOUND_PINS_DO_NOT_ALIGN", "GOVERNED_TEST_PINS_VERIFY_AGAINST_RECEIPT",
                            f"alignment reasons {alignment['reasons']}")
    return rewritten


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--request", required=True)
    parser.add_argument("--receipt", help="successor release receipt JSON (components with source_parent_commit)")
    parser.add_argument("--repo", help="local clone of the pinned repository, to verify ancestry")
    parser.add_argument("--check", action="store_true", help="verify only; write nothing")
    args = parser.parse_args(argv)
    request = json.loads(Path(args.request).read_text(encoding="utf-8"))
    receipt = json.loads(Path(args.receipt).read_text(encoding="utf-8")) if args.receipt else None
    try:
        rewritten = plan(request, receipt, ROOT, Path(args.repo) if args.repo else None)
    except RebindRefused as refused:
        print(json.dumps(refused.disposition, indent=2, sort_keys=True))
        return 2
    if not args.check:
        for rel, text in rewritten.items():
            (ROOT / rel).write_text(text, encoding="utf-8")
    print(json.dumps({"disposition": "ALLOW", "request_id": request["request_id"], "old_pin": request["old_pin"],
                      "new_pin": request["new_pin"], "files": sorted(rewritten), "written": not args.check,
                      "authority_effect": "NONE"}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
