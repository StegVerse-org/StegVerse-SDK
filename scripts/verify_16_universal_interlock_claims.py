#!/usr/bin/env python3
"""Verify immutable predecessor and exact-current witnesses for 16 source-only citations."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

FROZEN="a729d9b0f487f785b0e8f92006f303e8520e3593b6eb6c4c5de43273daa72087"
INDICES={188,189,190,196,198,199,202,203,204,205,206,335,336,337,338,339}
PRIOR="DENY:CLAIM_NOT_ENTAILED_BY_AVAILABLE_SOURCE_SPAN"
FULL="FULL_ATOMIC_SOURCE_FACT_VERIFIED"

def verify(raw:bytes,original:dict,predecessor:list[dict],judgments:dict,root:Path,head:str)->dict:
    if hashlib.sha256(raw).hexdigest()!=FROZEN or original.get("raw_sha256")!=FROZEN:
        raise ValueError("DENY:ORIGINAL_CAPTURE_MISMATCH")
    if len(original.get("rows",[]))!=640 or len(predecessor)!=640:
        raise ValueError("DENY:PREDECESSOR_PACKET_INCOMPLETE")
    rows=judgments.get("records",[])
    if judgments.get("original_capture_sha256")!=FROZEN or len(rows)!=16 or {r["index"] for r in rows}!=INDICES:
        raise ValueError("DENY:EXACT_REVIEW_COHORT_INVALID")
    if not re.fullmatch(r"[a-f0-9]{40}",head):
        raise ValueError("DENY:EXACT_SOURCE_HEAD_MISSING")
    root=root.resolve()
    findings=[]
    for row in rows:
        i=row["index"]
        old=original["rows"][i]
        p=predecessor[i]
        if old["index"]!=i or p["index"]!=i or p["source_label"]!=old["label"] or p["offset"]!=old["offset"] or p["disposition"]!=PRIOR:
            raise ValueError(f"DENY:ORIGINAL_PREDECESSOR_IDENTITY_OR_DISPOSITION:{i}")
        if row.get("whole_generated_paragraph_approved") is not False or row.get("generated_page_import_authorized") is not False or row.get("authentic_InTr_execution_observed") is not False:
            raise ValueError(f"DENY:SOURCE_ONLY_AUTHORITY_ESCALATION:{i}")
        fact=row["source_decision"]==FULL
        if row["full_atomic_source_fact_verified"] is not fact:
            raise ValueError(f"DENY:ATOMIC_CLASSIFICATION_MISMATCH:{i}")
        witness=(root/row["witness_path"]).resolve()
        if not witness.is_relative_to(root) or not witness.is_file():
            raise ValueError(f"DENY:CURRENT_SOURCE_UNAVAILABLE:{i}")
        lines=[n for n,line in enumerate(witness.read_text(encoding="utf-8").splitlines(),1) if row["exact_literal"] in line]
        if not lines:
            raise ValueError(f"DENY:CURRENT_SOURCE_PREDICATE_ABSENT:{i}")
        findings.append({
            "original_index":i,"original_page":old["page"],
            "original_label":old["label"],"original_offset":old["offset"],
            "original_context_sha256":hashlib.sha256((old.get("claim_context") or "").encode()).hexdigest(),
            "original_excerpt_sha256":hashlib.sha256((old.get("source_excerpt") or "").encode()).hexdigest(),
            "predecessor_atomic_sha256":hashlib.sha256(json.dumps(p,sort_keys=True,ensure_ascii=False).encode()).hexdigest(),
            "predecessor_disposition":p["disposition"],
            "exact_checked_out_sdk_sha":head,"current_witness_path":row["witness_path"],
            "current_witness_sha256":hashlib.sha256(witness.read_bytes()).hexdigest(),
            "current_exact_literal":row["exact_literal"],"current_line_numbers":lines[:24],
            "source_review_decision":row["source_decision"],
            "narrow_fact":row["narrow_fact"],"unsupported_extension":row["unsupported_extension"],
            "atomic_source_fact_verified":fact,"whole_generated_paragraph_approved":False,
            "generated_page_import_authorized":False,"authentic_InTr_execution_observed":False,
        })
    full_count=sum(x["atomic_source_fact_verified"] for x in findings)
    if full_count!=9:
        raise ValueError("DENY:ATOMIC_SOURCE_FACT_PARTITION_CHANGED")
    return {
        "schema":"stegverse.deepwiki-universal-interlock16-successors/v1",
        "frozen_capture_sha256":FROZEN,"exact_checked_out_sdk_sha":head,
        "original_nonpriority_citations_reviewed":len(findings),
        "narrow_atomic_source_facts_verified":full_count,
        "narrow_or_nonallow_generated_contexts":len(findings)-full_count,
        "whole_generated_paragraphs_approved":0,
        "external_generated_page_import_authorized":False,
        "authentic_runtime_transitions_observed":0,
        "original_capture_or_quarantine_modified":False,
        "findings":findings,
    }

def main():
    parser=argparse.ArgumentParser()
    for field in ("raw","original","predecessor","judgments","root","out"):
        parser.add_argument("--"+field,required=True,type=Path)
    a=parser.parse_args()
    head=subprocess.check_output(["git","rev-parse","HEAD"],cwd=a.root,text=True).strip()
    packet=verify(a.raw.read_bytes(),json.loads(a.original.read_text(encoding="utf-8")),
        json.loads(a.predecessor.read_text(encoding="utf-8")),
        json.loads(a.judgments.read_text(encoding="utf-8")),a.root,head)
    a.out.mkdir(parents=True,exist_ok=True)
    (a.out/"16-UNIVERSAL_INTERLOCK_SOURCE_SUCCESSORS.json").write_text(
        json.dumps(packet,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in packet.items() if k!="findings"},sort_keys=True))
if __name__=="__main__":
    main()
