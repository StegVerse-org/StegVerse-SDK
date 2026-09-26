#!/usr/bin/env python3
"""Verify frozen predecessor and exact-source successors for fourteen purpose-worker citations.

No source-review disposition constitutes authentic WorkerCoordinator, InTr or
Master Records evidence or licenses generated DeepWiki prose for republication.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

FROZEN = "a729d9b0f487f785b0e8f92006f303e8520e3593b6eb6c4c5de43273daa72087"
INDICES = {130,132,133,134,136,139,140,141,142,143,145,146,147,148}
ORIGINAL_DENY = "DENY:CLAIM_NOT_ENTAILED_BY_AVAILABLE_SOURCE_SPAN"
ATOMIC_VERIFIED = "FULL_ATOMIC_SOURCE_FACT_VERIFIED"


def reconcile(raw: bytes, claims: dict, prior: list[dict], decisions: dict,
              root: Path, head: str) -> dict:
    if hashlib.sha256(raw).hexdigest() != FROZEN or claims.get("raw_sha256") != FROZEN:
        raise ValueError("DENY:ORIGINAL_CAPTURE_CHANGED")
    if len(claims.get("rows", [])) != 640 or len(prior) != 640:
        raise ValueError("DENY:PREDECESSOR_PACKET_INCOMPLETE")
    rows = decisions.get("records", [])
    if decisions.get("original_capture_sha256") != FROZEN or len(rows) != 14 or {
        x["index"] for x in rows
    } != INDICES:
        raise ValueError("DENY:CURRENT_REVIEW_PARTITION_INVALID")
    if not re.fullmatch(r"[a-f0-9]{40}", head):
        raise ValueError("DENY:SOURCE_HEAD_NOT_EXACT")
    root = root.resolve()
    findings = []
    for row in rows:
        i = row["index"]
        original = claims["rows"][i]
        pred = prior[i]
        if (original["index"] != i or pred["index"] != i or
                pred["source_label"] != original["label"] or
                pred["offset"] != original["offset"] or
                pred["disposition"] != ORIGINAL_DENY):
            raise ValueError(f"DENY:ORIGINAL_PREDECESSOR_IDENTITY_INVALID:{i}")
        if (row.get("complete_generated_paragraph_approved") is not False or
                row.get("external_generated_content_republication_authorized") is not False or
                row.get("authentic_runtime_transition_observed") is not False):
            raise ValueError(f"DENY:SOURCE_REVIEW_AUTHORITY_ESCALATION:{i}")
        atomic = row["source_decision"] == ATOMIC_VERIFIED
        if row["full_atomic_source_fact_verified"] is not atomic:
            raise ValueError(f"DENY:ATOMIC_CLASSIFICATION_MISMATCH:{i}")
        witness = (root / row["witness_path"]).resolve()
        if not witness.is_relative_to(root) or not witness.is_file():
            raise ValueError(f"DENY:CURRENT_WITNESS_MISSING:{i}")
        lines = [n for n,s in enumerate(
            witness.read_text(encoding="utf-8").splitlines(),1
        ) if row["exact_literal"] in s]
        if not lines:
            raise ValueError(f"DENY:SOURCE_LITERAL_NOT_LOCATED:{i}")
        findings.append({
            "index": i,
            "original_page": original["page"],
            "original_source_label": original["label"],
            "original_offset": original["offset"],
            "original_claim_context_sha256": hashlib.sha256(
                (original.get("claim_context") or "").encode()
            ).hexdigest(),
            "original_source_excerpt_sha256": hashlib.sha256(
                (original.get("source_excerpt") or "").encode()
            ).hexdigest(),
            "predecessor_atomic_row_sha256": hashlib.sha256(
                json.dumps(pred,sort_keys=True,ensure_ascii=False).encode()
            ).hexdigest(),
            "predecessor_disposition": pred["disposition"],
            "exact_checked_out_sdk_sha": head,
            "current_witness_path": row["witness_path"],
            "current_witness_sha256": hashlib.sha256(witness.read_bytes()).hexdigest(),
            "exact_source_literal": row["exact_literal"],
            "current_exact_line_numbers": lines[:24],
            "narrow_source_fact": row["narrow_fact"],
            "broader_inference_unsupported": row["unsupported_extension"],
            "source_review_disposition": row["source_decision"],
            "full_atomic_source_fact_verified": atomic,
            "complete_generated_paragraph_approved": False,
            "generated_prose_republication_authorized": False,
            "authentic_InTr_or_Master_Records_observed": False,
        })
    atomic_count = sum(x["full_atomic_source_fact_verified"] for x in findings)
    if atomic_count != 10:
        raise ValueError("DENY:SOURCE_ATOMIC_PARTITION_CHANGED")
    return {
        "schema": "stegverse.deepwiki-purpose-worker14-successors/v1",
        "original_capture_sha256": FROZEN,
        "exact_checked_out_sdk_sha": head,
        "original_unresolved_candidates_reviewed": len(findings),
        "narrow_atomic_source_facts_verified": atomic_count,
        "broader_contexts_narrowed_or_denied": len(findings)-atomic_count,
        "whole_generated_paragraphs_approved": 0,
        "external_generated_page_republication_authorized": False,
        "authentic_runtime_transitions_observed": 0,
        "original_capture_or_quarantine_modified": False,
        "findings": findings,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    for field in ("raw","claims","predecessor","decisions","root","out"):
        p.add_argument("--"+field,required=True,type=Path)
    a = p.parse_args()
    head = subprocess.check_output(["git","rev-parse","HEAD"],cwd=a.root,text=True).strip()
    result = reconcile(
        a.raw.read_bytes(),
        json.loads(a.claims.read_text(encoding="utf-8")),
        json.loads(a.predecessor.read_text(encoding="utf-8")),
        json.loads(a.decisions.read_text(encoding="utf-8")),
        a.root,head,
    )
    a.out.mkdir(parents=True,exist_ok=True)
    (a.out/"14-PURPOSE_WORKER_SOURCE_SUCCESSORS.json").write_text(
        json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k!="findings"},sort_keys=True))


if __name__ == "__main__":
    main()
