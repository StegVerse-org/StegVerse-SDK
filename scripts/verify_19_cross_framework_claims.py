#!/usr/bin/env python3
"""Source-only successor review for 19 frozen cross-framework citations."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

FROZEN="a729d9b0f487f785b0e8f92006f303e8520e3593b6eb6c4c5de43273daa72087"
INDICES={410,411,412,413,414,416,418,421,422,423,424,425,426,428,433,434,436,437,438}
ORIGINAL_DENY="DENY:CLAIM_NOT_ENTAILED_BY_AVAILABLE_SOURCE_SPAN"

def verify(raw, claims, predecessor, decisions, root, exact_head):
    if hashlib.sha256(raw).hexdigest()!=FROZEN or claims.get("raw_sha256")!=FROZEN:
        raise ValueError("DENY:FROZEN_CAPTURE_MISMATCH")
    if len(claims.get("rows",[]))!=640 or len(predecessor)!=640:
        raise ValueError("DENY:ORIGINAL_CITATION_PACKET_INCOMPLETE")
    if decisions.get("original_capture_sha256")!=FROZEN:
        raise ValueError("DENY:DECISION_ORIGIN_MISMATCH")
    rows=decisions.get("records",[])
    if len(rows)!=19 or {r["index"] for r in rows}!=INDICES:
        raise ValueError("DENY:CROSS_FRAMEWORK_COHORT_NOT_EXACT")
    if not re.fullmatch(r"[0-9a-f]{40}",exact_head):
        raise ValueError("DENY:EXACT_COMMIT_MISSING")
    root=root.resolve(); out=[]
    for r in rows:
        i=r["index"]; old=claims["rows"][i]; prior=predecessor[i]
        if old["index"]!=i or prior["index"]!=i or prior["source_label"]!=old["label"] or prior["offset"]!=old["offset"] or prior["disposition"]!=ORIGINAL_DENY:
            raise ValueError(f"DENY:PREDECESSOR_IDENTITY_OR_DISPOSITION_MISMATCH:{i}")
        if r.get("complete_generated_claim_approved") is not False or r.get("generated_text_republication_allowed") is not False or r.get("authentic_governed_runtime_observed") is not False:
            raise ValueError(f"DENY:SOURCE_REVIEW_AUTHORITY_ESCALATION:{i}")
        if r["full_atomic_source_fact_verified"] != (r["source_decision"]=="FULL_ATOMIC_SOURCE_FACT_VERIFIED"):
            raise ValueError(f"DENY:SOURCE_REVIEW_PREDICATE_CLASSIFICATION:{i}")
        witness=(root/r["witness_path"]).resolve()
        if not witness.is_relative_to(root) or not witness.is_file():
            raise ValueError(f"DENY:WITNESS_SOURCE_UNAVAILABLE:{i}")
        line_numbers=[k for k,line in enumerate(witness.read_text(encoding="utf-8").splitlines(),1) if r["exact_literal"] in line]
        if not line_numbers:
            raise ValueError(f"DENY:EXACT_WITNESS_LITERAL_NOT_LOCATED:{i}")
        out.append({
            "index":i,"page":old["page"],"original_source_label":old["label"],"original_offset":old["offset"],
            "original_context_sha256":hashlib.sha256((old.get("claim_context") or "").encode()).hexdigest(),
            "original_excerpt_sha256":hashlib.sha256((old.get("source_excerpt") or "").encode()).hexdigest(),
            "predecessor_atomic_row_sha256":hashlib.sha256(json.dumps(prior,sort_keys=True,ensure_ascii=False).encode()).hexdigest(),
            "predecessor_disposition":prior["disposition"],"exact_checked_out_head":exact_head,
            "witness_path":r["witness_path"],"witness_sha256":hashlib.sha256(witness.read_bytes()).hexdigest(),
            "current_exact_literal":r["exact_literal"],"current_line_numbers":line_numbers[:24],
            "source_decision":r["source_decision"],"narrow_fact":r["narrow_fact"],"unsupported_extension":r["unsupported_extension"],
            "atomic_source_fact_verified":r["full_atomic_source_fact_verified"],
            "complete_generated_claim_approved":False,"third_party_republication_authorized":False,
            "authenticated_InTr_execution_observed":False,
        })
    verified=sum(r["atomic_source_fact_verified"] for r in out)
    if verified!=8: raise ValueError("DENY:EXPECTED_ATOMIC_SOURCE_PARTITION_CHANGED")
    return {"schema":"stegverse.deepwiki-crossframework19-source-successors/v1","original_capture_sha256":FROZEN,
        "exact_current_sdk_sha":exact_head,"original_nonpriority_candidates_reexamined":len(out),
        "narrow_atomic_source_facts_verified":verified,"narrow_or_nonallow_contexts":len(out)-verified,
        "complete_generated_claims_approved":0,"third_party_generated_page_import_allowed":False,
        "authenticated_runtime_transitions_observed":0,"original_capture_or_quarantine_modified":False,
        "findings":out}

def main():
    p=argparse.ArgumentParser()
    for key in ("raw","claims","predecessor","decisions","root","out"):
        p.add_argument("--"+key,required=True,type=Path)
    a=p.parse_args()
    sha=subprocess.check_output(["git","rev-parse","HEAD"],cwd=a.root,text=True).strip()
    result=verify(a.raw.read_bytes(),json.loads(a.claims.read_text()),
        json.loads(a.predecessor.read_text()),json.loads(a.decisions.read_text()),a.root,sha)
    a.out.mkdir(parents=True,exist_ok=True)
    (a.out/"19-CROSS_FRAMEWORK_SOURCE_SUCCESSORS.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k!="findings"},sort_keys=True))

if __name__=="__main__":
    main()
