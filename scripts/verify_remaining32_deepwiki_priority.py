#!/usr/bin/env python3
"""Fail-closed successor proof for 32 remaining broader-priority DeepWiki citations.

Outputs source-only review findings, never generated-text approvals. Verifies
the exact frozen predecessor (75 priorities, 640 original simple occurrences),
the remaining 32 vs earlier 14, and current checked-out file witnesses.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
from pathlib import Path

RAW_SHA256 = "a729d9b0f487f785b0e8f92006f303e8520e3593b6eb6c4c5de43273daa72087"
EARLIER_14 = {56, 57, 58, 59, 61, 62, 78, 100, 152, 307, 394, 499, 501, 502}
REMAINING_32 = {
    236,237,275,283,377,435,496,552,561,582,585,586,587,588,589,590,
    592,593,597,606,609,613,614,615,616,621,622,623,624,625,636,639,
}


def review(raw: bytes, priorities: list[dict], claims: dict, decisions: dict,
           root: Path, current_sha: str) -> dict:
    if hashlib.sha256(raw).hexdigest() != RAW_SHA256:
        raise ValueError("DENY:ORIGINAL_CAPTURE_HASH_CHANGED")
    if claims.get("raw_sha256") != RAW_SHA256 or len(claims.get("rows", [])) != 640:
        raise ValueError("DENY:ORIGINAL_CLAIM_PACKET_CHANGED")
    if len(priorities) != 75:
        raise ValueError("DENY:75_PRIORITY_PARTITION_CHANGED")
    original = {int(x["occurrence_index"]): x for x in priorities}
    if len(original) != 75:
        raise ValueError("DENY:DUPLICATE_FROZEN_PRIORITY")
    mismatch = {i for i, x in original.items() if x["status"] == "CITATION_CONTEXT_MISMATCH"}
    narrow = {i for i, x in original.items()
              if x["status"] == "NARROW_LITERAL_CONFIRMED_CONTEXT_NOT_FULLY_APPROVED"}
    broad = {i for i, x in original.items() if x["status"] == "FULL_CLAIM_REVIEW_PENDING"}
    if (len(mismatch),len(narrow),len(broad)) != (2,27,46):
        raise ValueError("DENY:75_PRIORITY_STATUS_PARTITION_CHANGED")
    if broad != EARLIER_14 | REMAINING_32 or EARLIER_14 & REMAINING_32:
        raise ValueError("DENY:46_BROADER_PRIORITY_COVERAGE_CHANGED")
    if decisions.get("original_capture_sha256") != RAW_SHA256:
        raise ValueError("DENY:DECISION_CAPTURE_PROVENANCE_CHANGED")
    rows = decisions.get("records", [])
    if len(rows) != 32 or {x["index"] for x in rows} != REMAINING_32:
        raise ValueError("DENY:32_SOURCE_REVIEW_SET_INCOMPLETE")
    if not re.fullmatch(r"[0-9a-f]{40}", current_sha):
        raise ValueError("DENY:EXACT_CURRENT_COMMIT_REQUIRED")
    out = []
    root = root.resolve()
    for decision in rows:
        index = decision["index"]
        pred = claims["rows"][index]
        original_row = original[index]
        original_label = str(original_row["original_label"]).strip("` ")
        source_label = str(pred["label"]).strip("` ")
        if original_label != source_label or pred["index"] != index:
            raise ValueError(f"DENY:ORIGINAL_CITATION_LABEL_MISMATCH:{index}")
        if not str(decision["disposition"]).startswith("DENY:"):
            raise ValueError(f"DENY:REVIEWED_CLAIM_AUTHORITY_ESCALATION:{index}")
        if decision.get("full_generated_claim_semantically_approved") is not False or (
            decision.get("publication_authorized") is not False
        ):
            raise ValueError(f"DENY:UNSUPPORTED_SEMANTIC_OR_REUSE_APPROVAL:{index}")
        rel = decision["witness_path"]
        file = (root / rel).resolve()
        if not file.is_relative_to(root) or not file.is_file():
            raise ValueError(f"DENY:CURRENT_WITNESS_UNAVAILABLE:{index}:{rel}")
        literal = decision["exact_literal"]
        lines = file.read_text(encoding="utf-8").splitlines()
        matches = [n for n, line in enumerate(lines, 1) if literal in line]
        if not matches:
            raise ValueError(f"DENY:CURRENT_WITNESS_LITERAL_NOT_VERIFIED:{index}:{rel}")
        source_excerpt = pred.get("source_excerpt") or ""
        context = pred.get("claim_context") or ""
        out.append({
            "occurrence_index": index,
            "page": original_row["page"],
            "original_label": original_label,
            "original_offset": pred["offset"],
            "original_claim_context_sha256": hashlib.sha256(context.encode()).hexdigest(),
            "original_source_excerpt_sha256": hashlib.sha256(source_excerpt.encode()).hexdigest(),
            "original_capture_sha256": RAW_SHA256,
            "current_checked_out_sha": current_sha,
            "current_witness_path": rel,
            "current_witness_file_sha256": hashlib.sha256(file.read_bytes()).hexdigest(),
            "exact_current_literal": literal,
            "current_literal_lines": matches[:20],
            "narrow_fact": decision["narrow_fact"],
            "unsupported_broader_claim": decision["unsupported"],
            "source_review_disposition": decision["disposition"],
            "original_source_revision_parity": "UNKNOWN",
            "full_generated_claim_semantically_approved": False,
            "generated_page_import_authorized": False,
            "authentic_InTr_execution_observed": False,
        })
    return {
        "schema": "stegverse.deepwiki-remaining32-source-reconciliation/v1",
        "raw_sha256": RAW_SHA256,
        "current_checked_out_sha": current_sha,
        "earlier_source_review_count": len(EARLIER_14),
        "new_source_review_count": len(out),
        "original_broader_priority_total": len(broad),
        "original_prioritized_narrow": len(narrow),
        "original_exact_citation_mismatches": len(mismatch),
        "full_generated_claim_semantically_approved": 0,
        "third_party_generated_pages_authorized": 0,
        "source_level_only": True,
        "findings": out,
    }


def main() -> None:
    p=argparse.ArgumentParser()
    for flag in ("raw", "original-priority", "claims", "decisions", "root", "out"):
        p.add_argument("--" + flag, type=Path, required=True)
    a=p.parse_args()
    with a.original_priority.open(newline="", encoding="utf-8") as f:
        priorities=list(csv.DictReader(f))
    current_sha=subprocess.check_output(
        ["git","rev-parse","HEAD"],cwd=a.root,text=True
    ).strip()
    result=review(a.raw.read_bytes(),priorities,
        json.loads(a.claims.read_text(encoding="utf-8")),
        json.loads(a.decisions.read_text(encoding="utf-8")),
        a.root,current_sha)
    a.out.mkdir(parents=True,exist_ok=True)
    (a.out/"32-SOURCE_PRIORITY_SUCCESSOR_REVIEW.json").write_text(
        json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k!="findings"},sort_keys=True))


if __name__=="__main__":
    main()
