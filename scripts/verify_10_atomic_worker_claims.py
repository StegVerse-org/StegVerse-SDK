#!/usr/bin/env python3
"""Exact-source, predecessor-linked, review-only ten-case atomic-worker audit."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

CAPTURE="a729d9b0f487f785b0e8f92006f303e8520e3593b6eb6c4c5de43273daa72087"
INDICES={150,151,153,154,155,156,158,159,162,164}
PRIOR="DENY:CLAIM_NOT_ENTAILED_BY_AVAILABLE_SOURCE_SPAN"
FULL="FULL_ATOMIC_SOURCE_FACT_VERIFIED"

def verify(raw:bytes,claims:dict,predecessors:list[dict],decisions:dict,root:Path,head:str)->dict:
    if hashlib.sha256(raw).hexdigest()!=CAPTURE or claims.get("raw_sha256")!=CAPTURE:
        raise ValueError("DENY:ORIGINAL_CAPTURE_IDENTITY")
    if len(claims.get("rows",[]))!=640 or len(predecessors)!=640:
        raise ValueError("DENY:ORIGINAL_CLAIM_PREDECESSOR_PACKET")
    rows=decisions.get("records",[])
    if decisions.get("original_capture_sha256")!=CAPTURE or len(rows)!=10 or {r["index"] for r in rows}!=INDICES:
        raise ValueError("DENY:REVIEW_COHORT_IDENTITY")
    if not re.fullmatch(r"[0-9a-f]{40}",head):
        raise ValueError("DENY:EXACT_HEAD_REQUIRED")
    root=root.resolve(); findings=[]
    for row in rows:
        i=row["index"]; prior=predecessors[i]; source=claims["rows"][i]
        if source["index"]!=i or prior["index"]!=i or prior["source_label"]!=source["label"] or prior["offset"]!=source["offset"] or prior["disposition"]!=PRIOR:
            raise ValueError(f"DENY:PREDECESSOR_IDENTITY_OR_CLASSIFICATION:{i}")
        if row.get("whole_generated_paragraph_approved") is not False or row.get("third_party_republication_authorized") is not False or row.get("authentic_execution_observed") is not False:
            raise ValueError(f"DENY:SOURCE_REVIEW_AUTHORITY_ESCALATION:{i}")
        atomic=(row["source_decision"]==FULL)
        if row["full_atomic_source_fact_verified"] is not atomic:
            raise ValueError(f"DENY:ATOMIC_SOURCE_CLASSIFICATION:{i}")
        path=(root/row["witness_path"]).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError(f"DENY:CURRENT_SOURCE_UNAVAILABLE:{i}")
        lines=[n for n,line in enumerate(path.read_text(encoding="utf-8").splitlines(),1) if row["exact_literal"] in line]
        if not lines:
            raise ValueError(f"DENY:CURRENT_SOURCE_PREDICATE_MISSING:{i}")
        findings.append({
            "original_index":i,"original_page":source["page"],
            "original_source_label":source["label"],"original_offset":source["offset"],
            "original_claim_context_sha256":hashlib.sha256((source.get("claim_context") or "").encode()).hexdigest(),
            "original_source_excerpt_sha256":hashlib.sha256((source.get("source_excerpt") or "").encode()).hexdigest(),
            "predecessor_atomic_row_sha256":hashlib.sha256(json.dumps(prior,sort_keys=True,ensure_ascii=False).encode()).hexdigest(),
            "predecessor_disposition":prior["disposition"],"exact_checked_out_head":head,
            "current_witness_path":row["witness_path"],"current_witness_file_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
            "exact_current_literal":row["exact_literal"],"current_line_numbers":lines[:20],
            "narrow_fact":row["narrow_fact"],"unsupported_inference":row["unsupported_extension"],
            "source_review_disposition":row["source_decision"],"full_atomic_source_fact_verified":atomic,
            "whole_generated_paragraph_approved":False,"third_party_page_import_allowed":False,
            "authentic_InTr_or_Master_Records_execution_observed":False,
        })
    full=sum(x["full_atomic_source_fact_verified"] for x in findings)
    if full!=5: raise ValueError("DENY:SOURCE_FACT_PARTITION_CHANGED")
    return {"schema":"stegverse.deepwiki-atomic-worker10-source-successors/v1",
        "original_capture_sha256":CAPTURE,"exact_sdk_head":head,"original_pending_candidates_reviewed":len(findings),
        "narrow_atomic_source_facts_verified":full,"narrow_or_nonallow_broader_contexts":len(findings)-full,
        "whole_generated_paragraphs_approved":0,"generated_text_republication_authorized":False,
        "authentic_runtime_transitions_observed":0,"original_capture_or_quarantine_modified":False,
        "findings":findings}

def main():
    p=argparse.ArgumentParser()
    for name in ("raw","claims","predecessors","decisions","root","out"):
        p.add_argument("--"+name,required=True,type=Path)
    a=p.parse_args()
    head=subprocess.check_output(["git","rev-parse","HEAD"],cwd=a.root,text=True).strip()
    result=verify(a.raw.read_bytes(),json.loads(a.claims.read_text()),json.loads(a.predecessors.read_text()),json.loads(a.decisions.read_text()),a.root,head)
    a.out.mkdir(parents=True,exist_ok=True)
    (a.out/"10-ATOMIC_WORKER_SOURCE_SUCCESSORS.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k!="findings"},sort_keys=True))
if __name__=="__main__":
    main()
