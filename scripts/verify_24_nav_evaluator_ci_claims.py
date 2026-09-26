#!/usr/bin/env python3
"""Reconcile 24 original pending nonpriority claims with exact current source.

Source-only conclusions are not original InTr dispositions or permission to
redistribute third-party generated text. Source facts and wider claim-context
approval are deliberately separate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

FROZEN = "a729d9b0f487f785b0e8f92006f303e8520e3593b6eb6c4c5de43273daa72087"
INDEX = {
    210, 215, 217, 218, 219, 229, 235, 246, 249,
    324, 325, 326, 327, 328, 329, 330, 431, 440,
    463, 464, 467, 468, 469, 471
}
PRIOR_DENY = "DENY:CLAIM_NOT_ENTAILED_BY_AVAILABLE_SOURCE_SPAN"
ATOMIC_PASS = "FULL_ATOMIC_SOURCE_FACT_VERIFIED"


def reconcile(raw: bytes, original: dict, predecessor: list[dict],
              judgments: dict, root: Path, exact_head: str) -> dict:
    if hashlib.sha256(raw).hexdigest() != FROZEN:
        raise ValueError("DENY:ORIGINAL_DEEPWIKI_CAPTURE_CHANGED")
    if (original.get("raw_sha256") != FROZEN or
            len(original.get("rows", [])) != 640 or
            len(predecessor) != 640):
        raise ValueError("DENY:ORIGINAL_PREDECESSOR_PACKET_INCOMPLETE")
    if judgments.get("capture_sha256") != FROZEN:
        raise ValueError("DENY:SOURCE_JUDGMENT_CAPTURE_IDENTITY_MISMATCH")
    rows = judgments.get("records", [])
    if len(rows) != 24 or {x["index"] for x in rows} != INDEX:
        raise ValueError("DENY:REVIEW_SET_NOT_EXACT_OR_DUPLICATED")
    if not re.fullmatch(r"[0-9a-f]{40}", exact_head):
        raise ValueError("DENY:CURRENT_SOURCE_COMMIT_NOT_EXACT")
    root = root.resolve()
    findings = []
    for judgment in rows:
        idx = judgment["index"]
        source = original["rows"][idx]
        previous = predecessor[idx]
        if (source["index"] != idx or previous["index"] != idx or
                source["label"] != previous["source_label"] or
                source["offset"] != previous["offset"]):
            raise ValueError(f"DENY:ORIGINAL_CITATION_PREDECESSOR_MISMATCH:{idx}")
        if previous["disposition"] != PRIOR_DENY:
            raise ValueError(f"DENY:ORIGINAL_DISPOSITION_CHANGED:{idx}")
        if judgment.get("generated_paragraph_approved") is not False or (
            judgment.get("generated_page_republication_authorized") is not False or
            judgment.get("runtime_admission_observed") is not False
        ):
            raise ValueError(f"DENY:SOURCE_ONLY_REVIEW_AUTHORITY_ESCALATION:{idx}")
        fact = bool(judgment["atomic_source_fact_verified"])
        if fact != (judgment["disposition"] == ATOMIC_PASS):
            raise ValueError(f"DENY:ATOMIC_PREDICATE_CLASSIFICATION_CONFLICT:{idx}")
        path = (root / judgment["witness_path"]).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError(f"DENY:EXACT_SOURCE_FILE_UNAVAILABLE:{idx}")
        content = path.read_text(encoding="utf-8")
        lines = [i for i,line in enumerate(content.splitlines(), 1)
                 if judgment["exact_literal"] in line]
        if not lines:
            raise ValueError(f"DENY:CURRENT_ATOMIC_SOURCE_PREDICATE_NOT_OBSERVED:{idx}")
        findings.append({
            "index": idx,
            "page": source["page"],
            "original_label": source["label"],
            "original_offset": source["offset"],
            "original_claim_context_sha256": hashlib.sha256(
                source.get("claim_context", "").encode()
            ).hexdigest(),
            "original_source_excerpt_sha256": hashlib.sha256(
                source.get("source_excerpt", "").encode()
            ).hexdigest(),
            "prior_atomic_record_sha256": hashlib.sha256(
                json.dumps(previous,sort_keys=True,ensure_ascii=False).encode()
            ).hexdigest(),
            "prior_disposition": previous["disposition"],
            "exact_checked_out_source_sha": exact_head,
            "current_witness_file": judgment["witness_path"],
            "current_witness_file_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "current_literal": judgment["exact_literal"],
            "current_line_numbers": lines[:24],
            "narrow_fact": judgment["narrow_fact"],
            "unsupported_extension": judgment["unsupported_extension"],
            "source_review_disposition": judgment["disposition"],
            "atomic_source_fact_verified": fact,
            "complete_generated_context_approved": False,
            "generated_prose_republication_authorized": False,
            "authentic_InTr_observed": False,
        })
    full = sum(f["atomic_source_fact_verified"] for f in findings)
    if full != 6:
        raise ValueError("DENY:SOURCE_ATOMIC_FACT_PARTITION_CHANGED")
    return {
        "schema": "stegverse.deepwiki-nav-evaluator-ci24-successors/v1",
        "original_capture_sha256": FROZEN,
        "exact_checked_out_source_sha": exact_head,
        "reviewed_remaining_original_candidates": len(findings),
        "full_atomic_source_facts_verified": full,
        "narrow_or_unsupported_contexts": len(findings)-full,
        "full_generated_paragraphs_approved": 0,
        "generated_text_republication_authorized": False,
        "original_capture_or_quarantine_modified": False,
        "authentic_runtime_transitions_observed": 0,
        "findings": findings,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    for name in ("raw", "original", "predecessor", "judgments", "root", "out"):
        p.add_argument("--" + name, type=Path, required=True)
    a = p.parse_args()
    head = subprocess.check_output(["git","rev-parse","HEAD"],cwd=a.root,text=True).strip()
    result = reconcile(
        a.raw.read_bytes(),
        json.loads(a.original.read_text(encoding="utf-8")),
        json.loads(a.predecessor.read_text(encoding="utf-8")),
        json.loads(a.judgments.read_text(encoding="utf-8")),
        a.root,head)
    a.out.mkdir(parents=True,exist_ok=True)
    (a.out/"24-NAV_EVALUATOR_CI_SOURCE_SUCCESSORS.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k!="findings"},sort_keys=True))


if __name__=="__main__":
    main()
