#!/usr/bin/env python3
"""Recheck 27 source literals against the exact earlier frozen-review commit.

This is a successor evidence overlay; it never rewrites the previous 613/75
adjudications and never treats historical source as current live execution.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

try:
    from scripts.triage_frozen_deepwiki_citations import NARROW_LITERAL, CAPTURE_SHA256
except ModuleNotFoundError:
    from triage_frozen_deepwiki_citations import NARROW_LITERAL, CAPTURE_SHA256

HISTORICAL_REVISION = "eec03e0fa3a2ee327eb4e3368b3f8458ac85e582"

def reconcile(historical: dict, newer: dict, current_rows: list[dict],
              expected: dict[int,str] | None = None) -> dict:
    expected = NARROW_LITERAL if expected is None else expected
    if historical.get("raw_sha256") != CAPTURE_SHA256 or newer.get("raw_sha256") != CAPTURE_SHA256:
        raise ValueError("DENY:CAPTURE_PROVENANCE_CHANGED")
    if historical.get("source_revision") != HISTORICAL_REVISION:
        raise ValueError("DENY:ORIGINAL_SOURCE_REVISION_CHANGED")
    if len(historical["rows"]) != len(newer["rows"]) or len(historical["rows"]) != 640:
        raise ValueError("DENY:SOURCE_PACKET_PARTITION_CHANGED")
    if len(current_rows) != 640:
        raise ValueError("DENY:NEWER_ASSESSMENT_INCOMPLETE")
    evidence = []
    for index, literal in sorted(expected.items()):
        prev, recent, current = historical["rows"][index], newer["rows"][index], current_rows[index]
        if prev["offset"] != recent["offset"] or prev["offset"] != current["offset"]:
            raise ValueError(f"DENY:HISTORICAL_OFFSET_CHANGED:{index}")
        if prev["label"] != recent["label"]:
            raise ValueError(f"DENY:HISTORICAL_CITATION_LABEL_CHANGED:{index}")
        original = prev.get("source_excerpt") or ""
        if literal not in original:
            raise ValueError(f"DENY:ORIGINAL_NARROW_LITERAL_NOT_FOUND:{index}")
        live_match = bool(current["atomic_source_observations"])
        evidence.append({
            "index": index,
            "label": prev["label"],
            "offset": prev["offset"],
            "historical_source_revision": HISTORICAL_REVISION,
            "later_comparison_revision": newer["source_revision"],
            "exact_historical_literal": literal,
            "historical_excerpt_sha256": hashlib.sha256(original.encode()).hexdigest(),
            "predecessor_disposition": current["disposition"],
            "predecessor_evidence_sha256": hashlib.sha256(json.dumps(current,sort_keys=True).encode()).hexdigest(),
            "historical_exact_literal_revalidated": True,
            "current_source_narrow_fact_also_observed": live_match,
            "outcome": "NARROW_HISTORICAL_SOURCE_CONFIRMED_FULL_CLAIM_NOT_APPROVED",
            "generation_time_deepwiki_source_revision_parity": "UNKNOWN",
            "republication_allowed": False,
        })
    return {
        "schema": "stegverse.deepwiki-priority-historical-reconciliation/v1",
        "original_raw_sha256": CAPTURE_SHA256,
        "historic_review_source": HISTORICAL_REVISION,
        "later_review_source": newer["source_revision"],
        "historical_narrow_facts_revalidated": len(evidence),
        "same_literal_also_observed_in_newer_atomic_check": sum(
            r["current_source_narrow_fact_also_observed"] for r in evidence),
        "historical_only_remaining_source_drift": sum(
            not r["current_source_narrow_fact_also_observed"] for r in evidence),
        "full_generated_claim_semantic_approvals": 0,
        "external_generated_page_imports_approved": 0,
        "source_reconciliations": evidence,
    }

def main() -> None:
    parser = argparse.ArgumentParser()
    for k in ("historical", "later", "atomic", "out"):
        parser.add_argument("--"+k,type=Path,required=True)
    a=parser.parse_args()
    data=reconcile(
        json.loads(a.historical.read_text(encoding="utf-8")),
        json.loads(a.later.read_text(encoding="utf-8")),
        json.loads(a.atomic.read_text(encoding="utf-8")),
    )
    a.out.mkdir(parents=True,exist_ok=True)
    (a.out/"27-HISTORICAL_NARROW_RECONCILIATIONS.json").write_text(
        json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in data.items() if k!="source_reconciliations"},sort_keys=True))

if __name__=="__main__":
    main()
