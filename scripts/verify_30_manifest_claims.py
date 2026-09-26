#!/usr/bin/env python3
"""Exact-source successor review for 30 original nonpriority DeepWiki claims.

No external generated text is copied into source. Full *atomic source predicate*
verification is a different state than approval of a generated paragraph, an
authorized page import, or an authentic InTr disposition.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

RAW_SHA256 = "a729d9b0f487f785b0e8f92006f303e8520e3593b6eb6c4c5de43273daa72087"
INDICES = {18,74,75,76,77,80,81,83,85,95,97,98,99,105,106,107,
           108,109,110,111,113,114,115,116,117,118,119,120,122,128}
SOURCE_OK = "FULL_ATOMIC_SOURCE_CLAIM_VERIFIED"


def reconcile(raw: bytes, claims: dict, predecessor: list[dict], decisions: dict,
              root: Path, current_sha: str) -> dict:
    if hashlib.sha256(raw).hexdigest() != RAW_SHA256:
        raise ValueError("DENY:FROZEN_CAPTURE_MUTATED")
    if claims.get("raw_sha256") != RAW_SHA256 or len(claims.get("rows", [])) != 640:
        raise ValueError("DENY:ORIGINAL_CLAIM_PACKET_MISSING")
    if len(predecessor) != 640 or predecessor[0]["index"] != 0:
        raise ValueError("DENY:PREDECESSOR_ATOMIC_PACKET_INCOMPLETE")
    rows=decisions.get("records", [])
    if len(rows)!=30 or {x["index"] for x in rows} != INDICES:
        raise ValueError("DENY:30_CASE_PARTITION_CHANGED")
    if decisions.get("input_capture_sha256") != RAW_SHA256:
        raise ValueError("DENY:DECISION_CAPTURE_PROVENANCE_CHANGED")
    if not re.fullmatch(r"[a-f0-9]{40}", current_sha):
        raise ValueError("DENY:EXACT_COMMIT_NOT_SUPPLIED")
    root=root.resolve()
    verified=[]
    for item in rows:
        idx=item["index"]
        original=claims["rows"][idx]
        prior=predecessor[idx]
        if original["index"]!=idx or prior["index"]!=idx:
            raise ValueError(f"DENY:PREDECESSOR_INDEX_CONFLICT:{idx}")
        if original["offset"]!=prior["offset"] or original["label"]!=prior["source_label"]:
            raise ValueError(f"DENY:PREDECESSOR_IDENTITY_CONFLICT:{idx}")
        if prior["disposition"] != "DENY:CLAIM_NOT_ENTAILED_BY_AVAILABLE_SOURCE_SPAN":
            raise ValueError(f"DENY:PREDECESSOR_NOT_IN_REMAINING_436:{idx}")
        source=(root/item["witness_path"]).resolve()
        if not source.is_relative_to(root) or not source.is_file():
            raise ValueError(f"DENY:SOURCE_WITNESS_UNAVAILABLE:{idx}")
        literal=item["exact_source_predicate"]
        contents=source.read_text(encoding="utf-8")
        positions=[number for number,line in enumerate(contents.splitlines(),1) if literal in line]
        if not positions:
            raise ValueError(f"DENY:EXACT_WITNESS_PREDICATE_MISSING:{idx}")
        if bool(item["full_atomic_source_claim_approved"]) != (
            item["source_review_disposition"]==SOURCE_OK
        ):
            raise ValueError(f"DENY:DISPOSITION_MISMATCH:{idx}")
        if item["whole_generated_context_approved"] or item["generated_prose_republication_allowed"]:
            raise ValueError(f"DENY:GENERATED_TEXT_PROMOTED:{idx}")
        claim=original.get("claim_context","") or ""
        snippet=original.get("source_excerpt","") or ""
        verified.append({
            "index":idx,
            "page":original["page"],
            "original_label":original["label"],
            "original_offset":original["offset"],
            "original_claim_context_sha256":hashlib.sha256(claim.encode()).hexdigest(),
            "original_excerpt_sha256":hashlib.sha256(snippet.encode()).hexdigest(),
            "frozen_capture_sha256":RAW_SHA256,
            "prior_evidence_sha256":hashlib.sha256(
                json.dumps(prior,sort_keys=True,ensure_ascii=False).encode()
            ).hexdigest(),
            "prior_disposition":prior["disposition"],
            "checked_out_sdk_sha":current_sha,
            "witness_path":item["witness_path"],
            "witness_file_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
            "current_exact_predicate":literal,
            "current_lines":positions[:20],
            "source_review_disposition":item["source_review_disposition"],
            "narrow_fact":item["narrow_fact"],
            "unsupported_extension":item["unsupported_extension"],
            "full_atomic_source_claim_approved":item["full_atomic_source_claim_approved"],
            "full_generated_paragraph_approved":False,
            "generated_text_publication_authorized":False,
            "authentic_runtime_transition_observed":False,
        })
    full=sum(x["full_atomic_source_claim_approved"] for x in verified)
    if full!=13:
        raise ValueError("DENY:ATOMIC_REVIEW_APPROVAL_COUNT_CHANGED")
    return {
        "schema":"stegverse.deepwiki-manifest30-source-successor/v1",
        "frozen_capture_sha256":RAW_SHA256,
        "exact_checked_out_sdk_sha":current_sha,
        "reviewed_original_remaining_candidate_count":len(verified),
        "full_atomic_source_predicates_verified":full,
        "narrow_only_or_denied":len(verified)-full,
        "original_frozen_capture_unchanged":True,
        "full_generated_paragraph_approvals":0,
        "third_party_page_imports_authorized":0,
        "review_only_not_InTr":True,
        "findings":verified,
    }


def main():
    p=argparse.ArgumentParser()
    for name in ("raw","claims","predecessor","decisions","root","out"):
        p.add_argument("--"+name,type=Path,required=True)
    args=p.parse_args()
    sha=subprocess.check_output(["git","rev-parse","HEAD"],cwd=args.root,text=True).strip()
    packet=reconcile(
        args.raw.read_bytes(),
        json.loads(args.claims.read_text(encoding="utf-8")),
        json.loads(args.predecessor.read_text(encoding="utf-8")),
        json.loads(args.decisions.read_text(encoding="utf-8")),
        args.root,sha,
    )
    args.out.mkdir(parents=True,exist_ok=True)
    (args.out/"30-MANIFEST_CLAIM_SEMANTIC_SUCCESSORS.json").write_text(
        json.dumps(packet,indent=2,ensure_ascii=False)+"\n",encoding="utf-8"
    )
    print(json.dumps({k:v for k,v in packet.items() if k!="findings"},sort_keys=True))


if __name__=="__main__":
    main()
