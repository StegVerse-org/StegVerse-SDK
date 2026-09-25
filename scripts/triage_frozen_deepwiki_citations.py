#!/usr/bin/env python3
"""Produce review registers from immutable DeepWiki capture, never publish it.

Narrow confirmations concern source *literals*, NOT the larger generated claims.
Every absent/mutated artifact or source excerpt fails closed.
"""
from __future__ import annotations
import argparse
import collections
import csv
import hashlib
import json
from pathlib import Path

CAPTURE_SHA256 = "a729d9b0f487f785b0e8f92006f303e8520e3593b6eb6c4c5de43273daa72087"
EXPECTED_PRIORITY = 75
NARROW_LITERAL = {
    19: "requests>=2.28.0", 20: "pyyaml>=6.0",
    37: "def evaluate_three_worker_experiment",
    38: "def review_stage1_org_receipt_snapshots",
    42: '"decision"] == "FAIL_CLOSED"',
    45: '"decision"] == "FAIL_CLOSED"',
    46: "credential_authority: TV/TVC",
    96: "def build_manifest",
    137: "partition reconstruction mismatch",
    161: "requires_workercoordinator_claim_fence",
    163: 'TEST2_SCENARIO = "TEST_2_ATOMIC_TASK_WORKER_BINDING"',
    165: 'TEST3_SCENARIO = "TEST_3_INVARIANCE_SHORT_LIVED_ACTOR_SEAM"',
    167: 'TEST3_LEGACY_SCENARIO = "TEST_3_RICHARD_SHORT_LIVED_ACTOR_SEAM"',
    200: '"canonical_cells"',
    201: '"receipt_requirements"',
    245: '"sdk_resolves_governance": False',
    254: "REPRESENTED_ONLY", 255: "RECOGNIZED_PROJECTED",
    256: "CANONICALLY_EVALUATED", 257: "LIVE_RUNTIME_BOUND",
    258: "UNKNOWN_RELATION_PRESERVED",
    291: "build_persistence_plan",
    292: "build_destination_binding",
    293: "write_with_adapter",
    371: 'NON_AUTHORIZING_LOCAL_REVIEW_ONLY',
    417: "EXPECTED_MANIFEST_SHA256",
    419: "EXPECTED_MANIFEST_BLOB_SHA1",
}
MISMATCH = {12, 13}


def build(raw: bytes, claims: dict, unresolved: dict) -> tuple[list[dict], list[dict]]:
    checksum = hashlib.sha256(raw).hexdigest()
    if checksum != CAPTURE_SHA256 or claims.get("raw_sha256") != checksum or unresolved.get("original_sha256") != checksum:
        raise ValueError("DENY:FROZEN_CAPTURE_HASH_MISMATCH")
    priority = [r for r in claims["rows"] if r["triage_signal"] == "LOW_LEXICAL_OVERLAP_REVIEW_FIRST"]
    if len(priority) != EXPECTED_PRIORITY or len({r["index"] for r in priority}) != EXPECTED_PRIORITY:
        raise ValueError("DENY:PRIORITY_SET_CHANGED")
    if not NARROW_LITERAL.keys() <= {r["index"] for r in priority} or not MISMATCH <= {r["index"] for r in priority}:
        raise ValueError("DENY:REVIEWED_INDEX_MISSING")
    reviewed = []
    for entry in priority:
        index = entry["index"]
        status = "FULL_CLAIM_REVIEW_PENDING"
        narrow = ""
        action = "Inspect full architectural claim against exact source and implementation/test neighbors."
        if index in MISMATCH:
            if "GovernanceIntakeRequest" not in entry["claim_context"]:
                raise ValueError("DENY:EXPECTED_DIAGRAM_CONTEXT_CHANGED")
            status = "CITATION_CONTEXT_MISMATCH"
            action = "Replace unsupported diagram source reference after source-specific diagram review."
        elif index in NARROW_LITERAL:
            narrow = NARROW_LITERAL[index]
            if narrow not in (entry.get("source_excerpt") or ""):
                raise ValueError(f"DENY:SOURCE_LITERAL_CHANGED:{index}")
            status = "NARROW_LITERAL_CONFIRMED_CONTEXT_NOT_FULLY_APPROVED"
            action = "Only narrow literal is supported; do not approve surrounding broader claim."
        reviewed.append({
            "occurrence_index": index, "page": entry["page"],
            "original_label": entry["label"], "source_url": entry["source_url"],
            "status": status, "confirmed_narrow_literal": narrow,
            "next_action": action, "full_claim_semantically_approved": False,
        })
    if len(unresolved["entries"]) != 27 or len(unresolved["malformed_contextual_entries"]) != 19:
        raise ValueError("DENY:UNRESOLVED_SET_CHANGED")
    defects = []
    for e in unresolved["entries"]:
        subs = e.get("composite_review", {}).get("subreferences", [])
        urls = e.get("proposals", []) + [u for s in subs for u in s.get("candidate_urls", [])]
        defects.append({"kind": "simple", "offset": e["offset"], "page": e["page"],
            "original_label": e["label"], "disposition": e["disposition"],
            "source_candidates": urls, "publication_approved": False,
            "next_action": "Check exact claim semantics; split any composites; explicitly repair or omit."})
    for e in unresolved["malformed_contextual_entries"]:
        p = e.get("source_candidate") or {}
        defects.append({"kind": "malformed", "offset": e["offset"], "page": "See frozen Markdown offset",
            "original_label": e["context"][-150:], "disposition": p.get("disposition", "CONTEXT_REVIEW_REQUIRED"),
            "source_candidates": p.get("proposals", []), "publication_approved": False,
            "next_action": "Parse surrounding Markdown; review proposed source and correct syntax separately."})
    return reviewed, defects


def export(raw: bytes, claims: dict, unresolved: dict, out: Path) -> dict:
    reviewed, defects = build(raw, claims, unresolved)
    out.mkdir(parents=True, exist_ok=True)
    for name, rows in (("priority-75-REVIEW-NOT-PUBLICATION.csv", reviewed),
                       ("unresolved-46-REVIEW-NOT-PUBLICATION.csv", defects)):
        with (out / name).open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]))
            writer.writeheader()
            for row in rows:
                writer.writerow({**row, "source_candidates": json.dumps(row.get("source_candidates", []))} if
                                "source_candidates" in row else row)
    summary = {
        "schema": "stegverse.deepwiki-citation-triage/v1",
        "frozen_capture_sha256": CAPTURE_SHA256,
        "frozen_source_revision": claims["source_revision"],
        "priority_total": len(reviewed),
        "priority_dispositions": dict(collections.Counter(r["status"] for r in reviewed)),
        "unresolved_defects": len(defects),
        "unresolved_direct_source_proposals": sum(
            bool(x["source_candidates"]) for x in defects if x["kind"] == "simple" and
            len(x["source_candidates"]) == 1),
        "semantically_approved_full_claims": 0,
        "approved_generated_imports": 0,
        "publication_allowed": False,
    }
    (out / "triage-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    ap = argparse.ArgumentParser()
    for arg in ("raw", "claims", "unresolved", "out"):
        ap.add_argument("--" + arg, type=Path, required=True)
    args = ap.parse_args()
    report = export(args.raw.read_bytes(),
                    json.loads(args.claims.read_text(encoding="utf-8")),
                    json.loads(args.unresolved.read_text(encoding="utf-8")), args.out)
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
