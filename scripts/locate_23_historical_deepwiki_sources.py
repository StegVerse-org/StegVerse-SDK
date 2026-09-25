#!/usr/bin/env python3
"""Read-only current-source locator for 23 historically supported SDK citations.

Historical exact source support is not lost when source lines move. Match the
same source file at checked-out SHA, never auto-publish or rewrite the frozen
public DeepWiki. Missing/changed source yields exact actionable non-ALLOW.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

REVIEWED_HISTORIC = "eec03e0fa3a2ee327eb4e3368b3f8458ac85e582"
FROZEN_CAPTURE = "a729d9b0f487f785b0e8f92006f303e8520e3593b6eb6c4c5de43273daa72087"
SAME_CODE_EQUIVALENTS = {
    # Names only; current call behavior and surrounding claims remain unapproved.
    96: ("stegverse/manifest_builder.py", "def build_manifest("),
    137: ("stegverse/purpose_bound_worker_processor.py", "partition reconstruction mismatch"),
}
REF = re.compile(r"^(?P<path>.+?)(?::(?P<start>\d+)(?:-(?P<end>\d+))?)?$")


def inspect_current(historical: dict, root: Path, exact_revision: str) -> dict:
    if historical.get("original_raw_sha256") != FROZEN_CAPTURE:
        raise ValueError("DENY:CAPTURE_HASH_CHANGED")
    if historical.get("historic_review_source") != REVIEWED_HISTORIC:
        raise ValueError("DENY:HISTORICAL_SOURCE_REVISION_CHANGED")
    original = historical["source_reconciliations"]
    if len(original) != 27:
        raise ValueError("DENY:HISTORICAL_NARROW_PARTITION_CHANGED")
    pending = [r for r in original if not r["current_source_narrow_fact_also_observed"]]
    if len(pending) != 23:
        raise ValueError("DENY:HISTORICAL_ONLY_SET_CHANGED")
    if not re.fullmatch(r"[a-f0-9]{40}",exact_revision):
        raise ValueError("DENY:CURRENT_REVISION_NOT_EXACT_COMMIT")
    results = []
    for earlier in pending:
        i = earlier["index"]
        match = REF.match(earlier["label"].strip("`"))
        if match is None:
            raise ValueError("DENY:MALFORMED_PREDECESSOR_REFERENCE")
        rel = match["path"]
        literal = earlier["exact_historical_literal"]
        substitute = SAME_CODE_EQUIVALENTS.get(i)
        if substitute:
            rel, literal = substitute
        file = (root / rel).resolve()
        if not file.is_relative_to(root.resolve()) or not file.is_file():
            state, occurrences = "DENY:CURRENT_SOURCE_FILE_UNAVAILABLE", []
        else:
            lines = file.read_text(encoding="utf-8").splitlines()
            occurrences = [n for n, line in enumerate(lines,1) if literal in line]
            state = ("NARROW_LITERAL_LOCATED_CURRENT_CODE_ONLY"
                     if occurrences else "DENY:CURRENT_EQUIVALENT_LITERAL_NOT_LOCATED")
        results.append({
            "index": i,
            "historic_source_label": earlier["label"],
            "historical_exact_literal": earlier["exact_historical_literal"],
            "current_search_literal": literal,
            "current_path": rel,
            "current_source_sha": exact_revision,
            "current_exact_line_numbers": occurrences[:20],
            "current_match_count": len(occurrences),
            "source_predicate_disposition": state,
            "full_generated_claim_approved": False,
            "execution_observed": False,
            "republication_authorized": False,
            "predecessor_historical_excerpt_sha256": earlier["historical_excerpt_sha256"],
            "predecessor_disposition": earlier["predecessor_disposition"],
        })
    return {
        "schema": "stegverse.deepwiki-current-locator-23/v1",
        "original_capture_sha256": FROZEN_CAPTURE,
        "historical_source_sha": REVIEWED_HISTORIC,
        "current_source_sha": exact_revision,
        "historical_only_rechecked": len(results),
        "exact_current_literal_located": sum(x["current_match_count"]>0 for x in results),
        "current_literal_missing_or_source_unavailable": sum(x["current_match_count"]==0 for x in results),
        "full_generated_claims_approved": 0,
        "original_capture_and_quarantine_modified": False,
        "findings": results,
    }


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--historical",type=Path,required=True)
    parser.add_argument("--root",type=Path,default=Path("."))
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    sha=subprocess.check_output(["git","rev-parse","HEAD"],cwd=args.root,text=True).strip()
    packet=json.loads(args.historical.read_text(encoding="utf-8"))
    result=inspect_current(packet,args.root,sha)
    args.out.mkdir(parents=True,exist_ok=True)
    (args.out/"23-CURRENT_NARROW_LITERAL_LOCATORS.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k!="findings"},sort_keys=True))


if __name__=="__main__":
    main()
