#!/usr/bin/env python3
"""Fail-closed, offset-exact curatorial treatment of frozen DeepWiki citations.

Generated prose is not reviewed or licensed for public republication. Produces
a quarantine-only derivative with ALL 659 empty markdown citation targets
downgraded to non-link source labels and per-occurrence audit dispositions.
"""
from __future__ import annotations
import argparse
import collections
import csv
import hashlib
import json
import re
from pathlib import Path

RAW_SHA = "a729d9b0f487f785b0e8f92006f303e8520e3593b6eb6c4c5de43273daa72087"
MALFORMED = re.compile(r"`(?P<label>[A-Za-z0-9_./-]+:\d+(?:-\d+)?)\]\(\)")
ORIGINAL_PRIORITY_REASON = {
    56: "DIAGRAM_DEPICTS_MULTIPLE_UNPROVEN_RELATIONSHIPS",
    57: "DIAGRAM_REQUIRES_ADDITIONAL_RUNTIME_BOUNDARY_SOURCE",
    58: "EXPERIMENT_FUNCTION_NOT_THE_ENTIRE_DIAGRAM",
    59: "HANDOFF_CONDITIONS_NOT_LIVE_DIAGRAM_PROOF",
    61: "MODULE_HEADER_NOT_FULL_BEHAVIOR_PROOF",
    62: "TEST_FIXTURE_NOT_LIVE_BOUNDARY_EVIDENCE",
    78: "HISTORICAL_SOURCE_REVISION_DEPENDENT",
    100: "HISTORICAL_SOURCE_REVISION_DEPENDENT",
    152: "PROCESSOR_IMPLEMENTATION_NOT_LIVE_EXECUTION_PROOF",
    236: "HANDOFF_TITLE_NOT_FULL_DIAGRAM_PROOF",
    237: "BUILDER_FUNCTION_NOT_FULL_DIAGRAM_PROOF",
    275: "TEST_MODULE_NOT_UNIVERSAL_TAMPER_PROOF",
    283: "ADMISSIBILITY_CODE_SPAN_NOT_FULL_DIAGRAM",
    307: "DISABLED_WRITE_ADAPTER_CONTRADICTS_UNQUALIFIED_COMPLETION",
    377: "EXPERIMENT_FUNCTION_NOT_MULTIPHASE_EXECUTION_PROOF",
    394: "FIXTURE_TEST_CANNOT_AUTHENTICATE_EXTERNAL_WORKERS",
    435: "MIR_SCRIPT_POINTER_DOES_NOT_ESTABLISH_GOVERNED_RUN",
    496: "DIAGNOSTIC_JSON_NOT_COMPLETE_TEST_CATEGORY_INVENTORY",
    499: "STATUS_ONLY_NOT_LIVE_RUNTIME_PROOF",
    501: "EVIDENCE_JSON_IS_SOURCE_RECORD_NOT_RUNTIME_RECEIPT",
    502: "FIXTURE_HANDOFF_STATE_NOT_PRODUCTION_TRANSITION",
    552: "SOUTH_GLOSSARY_EXCEEDS_SINGLE_HANDOFF_SPAN",
    561: "TASK_JSON_ASSESSMENT_NOT_GENERIC_TRANSPORT_CONTRACT",
    582: "IMPORT_EXPORT_LIST_NOT_ADMISSIBILITY_RECEIPT",
    585: "TASK_JSON_PREDICATE_NOT_COMPLETE_DEFINITION",
    586: "SOVEREIGN_ROUTE_NOT_FULL_GOVERNANCE_POSTURE_GRAPH",
    587: "HANDOFF_DESCRIPTION_NOT_LIVE_GRAPH_EXECUTION",
    588: "BUILDER_FUNCTION_NOT_FULL_RELATIONSHIP_GRAPH",
    589: "SAFETY_IMPORT_NOT_GCAT_METRIC_SEMANTICS",
    590: "DUAL_ADAPTER_DATA_CLASS_NOT_GCAT_METRIC_PROOF",
    592: "SAFETY_IMPORT_NOT_GCAT_METRIC_SEMANTICS",
    593: "DUAL_ADAPTER_DATA_CLASS_NOT_GCAT_METRIC_PROOF",
    597: "TASK_COSV_VALUE_NOT_UNIVERSAL_VECTOR_DEFINITION",
    606: "TASK_PREDICATE_NOT_UNIVERSAL_FAIL_CLOSED_RULE",
    609: "TASK_PREDICATE_NOT_UNIVERSAL_FAIL_CLOSED_RULE",
    613: "RETURN_PROJECTION_NOT_RECORDS_ONLY_SYSTEM_INVARIANT",
    614: "FIXTURE_HASH_NOT_RETAINED_PRODUCTION_RECORDS",
    615: "RETURN_PROJECTION_NOT_RECORDS_ONLY_SYSTEM_INVARIANT",
    616: "FIXTURE_HASH_NOT_RETAINED_PRODUCTION_RECORDS",
    621: "FIXTURE_TASK_GROUP_NOT_COMPLETE_ATOMIC_WORKER",
    622: "FIXTURE_TASK_GROUP_NOT_COMPLETE_ATOMIC_WORKER",
    623: "HANDOFF_TASK_STATUS_NOT_COMPONENT011_DEFINITION",
    624: "HANDOFF_TASK_STATUS_NOT_COMPONENT011_DEFINITION",
    625: "DISPATCH_DESCRIPTION_NOT_COMPONENT011_RECEIPT_PROOF",
    636: "TASK_EVIDENCE_METADATA_NOT_MIR_GENERIC_DEFINITION",
    639: "TASK_EVIDENCE_METADATA_NOT_MIR_GENERIC_DEFINITION",
}
# Original frozen review cases: two demonstrated mismatches + 27 narrow facts;
# these reason codes never imply whole generated paragraph approval.
MISMATCH = {12, 13}
REPAIRS = {
    98: {"incorrect":"stegverse/manifest_builder.py:75-95",
         "correct":"stegverse/manifest_builder.py:126-147",
         "why":"_route_declaration moved to current source lines 126-147"},
    99: {"incorrect":"stegverse/manifest_builder.py:98-111",
         "correct":"stegverse/manifest_builder.py:149-170",
         "why":"_validate_governance_request moved to current source lines 149-170"},
    439: {"incorrect":"tests/test_mir_sv_exp3_manifest.py:39-48",
          "correct":"tests/test_mir_sv_exp3_manifest.py:43-51",
          "why":"diagnostic assertions now extend through the authority_effect check at line 51"},
}

def curate(raw: bytes, prior: dict, claims: dict, unresolved: dict,
           original_priority: list[dict]) -> tuple[bytes, dict, list[dict]]:
    rawhash = hashlib.sha256(raw).hexdigest()
    if rawhash != RAW_SHA or prior.get("input_sha256") != RAW_SHA or claims.get("raw_sha256") != RAW_SHA or unresolved.get("original_sha256") != RAW_SHA:
        raise ValueError("DENY:FROZEN_CAPTURE_OR_REPORT_HASH_MISMATCH")
    original = raw.decode("utf-8")
    entries = prior["entries"]
    if len(entries) != 640 or sum(bool(e["candidate_url"]) for e in entries) != 613:
        raise ValueError("DENY:ORIGINAL_CANDIDATE_PARTITION_CHANGED")
    if len(unresolved["entries"]) != 27 or len(unresolved["malformed_contextual_entries"]) != 19:
        raise ValueError("DENY:UNRESOLVED_PARTITION_CHANGED")
    priorities = {int(e["occurrence_index"]): e for e in original_priority}
    if len(priorities) != 75 or len(original_priority) != 75:
        raise ValueError("DENY:FROZEN_PRIORITY_SET_CHANGED")
    expected_broad = {i for i, e in priorities.items() if e["status"] == "FULL_CLAIM_REVIEW_PENDING"}
    if expected_broad != set(ORIGINAL_PRIORITY_REASON):
        raise ValueError("DENY:BROAD_PRIORITY_ADJUDICATION_INCOMPLETE")
    edits, rows = [], []
    broken_offsets = {e["offset"] for e in unresolved["entries"]}
    if broken_offsets != {e["offset"] for e in entries if not e["candidate_url"]}:
        raise ValueError("DENY:UNRESOLVED_OFFSETS_MISMATCH")
    for i, e in enumerate(entries):
        start = e["offset"]
        literal = "[" + e["label"] + "]()"
        if original[start:start + len(literal)] != literal or claims["rows"][i]["offset"] != start:
            raise ValueError("DENY:SOURCE_OFFSET_MISMATCH")
        claim = claims["rows"][i]
        status = "DENY:PENDING_CLAIM_SPECIFIC_SEMANTIC_REVIEW"
        reason = "SOURCE_SPAN_ONLY_NO_SEMANTIC_APPROVAL"
        if i in priorities:
            previous = priorities[i]["status"]
            if previous == "CITATION_CONTEXT_MISMATCH" and i in MISMATCH:
                status, reason = "DENY:CITATION_CONTEXT_MISMATCH", "DIAGRAM_SOURCE_DOES_NOT_SUPPORT_WIRING"
            elif previous == "NARROW_LITERAL_CONFIRMED_CONTEXT_NOT_FULLY_APPROVED":
                status, reason = "DENY:FULL_CLAIM_UNREVIEWED_NARROW_LITERAL_ONLY", "EXACT_LITERAL_NOT_PARAGRAPH_PROOF"
            elif previous == "FULL_CLAIM_REVIEW_PENDING":
                status, reason = "DENY:REVIEWED_INSUFFICIENT_EVIDENCE", ORIGINAL_PRIORITY_REASON[i]
            else:
                raise ValueError("DENY:INCONSISTENT_FROZEN_PRIORITY_STATUS")
        if start in broken_offsets:
            status, reason = "DENY:UNRESOLVED_SOURCE_LABEL_OMITTED", "NO_AUTHORIZED_REPLACEMENT"
        # No unapproved candidate URL is ever inserted into generated prose.
        replacement = "`" + e["label"].strip("`") + "`"
        edits.append((start, start + len(literal), replacement))
        rows.append({"kind":"simple","occurrence":i,"offset":start,"page":e["page"],
                     "original_label":e["label"],"original_url":e["candidate_url"],
                     "disposition":status,"reason":reason,"claim_context_sha256":
                     hashlib.sha256(claim["claim_context"].encode()).hexdigest(),
                     "source_excerpt_sha256":hashlib.sha256((claim["source_excerpt"] or "").encode()).hexdigest(),
                     "semantic_approval":False, "source_revision":prior["source_revision"]})
    for j, m in enumerate(unresolved["malformed_contextual_entries"]):
        offset = m["offset"]
        target = MALFORMED.search(original,max(0,offset-180),offset+3)
        if not target or target.end()-3 != offset:
            raise ValueError("DENY:MALFORMED_CONTEXT_NO_EXACT_REPAIR")
        edits.append((target.start(),target.end(),"`"+target["label"]+"`"))
        rows.append({"kind":"malformed","occurrence":j,"offset":offset,"page":"FROZEN_OFFSET",
                     "original_label":target["label"],"original_url":None,
                     "disposition":"DENY:MALFORMED_CITATION_OMITTED",
                     "reason":"RETAIN_PLAIN_LABEL_PENDING_SEMANTIC_SOURCE_REVIEW",
                     "claim_context_sha256":hashlib.sha256(m["context"].encode()).hexdigest(),
                     "source_excerpt_sha256":None,"semantic_approval":False,
                     "source_revision":prior["source_revision"]})
    edits.sort(key=lambda t:t[0])
    if any(a[1] > b[0] for a,b in zip(edits,edits[1:])) or len(edits)!=659:
        raise ValueError("DENY:OVERLAPPING_OR_INCOMPLETE_OFFSETS")
    sanitized = original
    for start,end,replacement in reversed(edits):
        sanitized = sanitized[:start] + replacement + sanitized[end:]
    if "]()" in sanitized:
        raise ValueError("DENY:EMPTY_CITATION_TARGET_RETAINED")
    drift = []
    for i, info in REPAIRS.items():
        old = entries[i]
        if old["label"] != info["incorrect"]:
            raise ValueError("DENY:SOURCE_DRIFT_ORIGINAL_LABEL_CHANGED")
        drift.append({"occurrence":i,"old_source":info["incorrect"],
                      "source_verified_proposed_current_anchor":info["correct"],
                      "reason":info["why"],"disposition":"DENY:REQUIRES_UPDATED_CLAIM_CONTEXT_REVIEW",
                      "semantic_approval":False})
    report = {"schema":"stegverse.deepwiki-frozen-curation/v1",
              "original_capture_sha256":RAW_SHA,
              "source_revision":prior["source_revision"],
              "simple_candidates_downgraded_to_nonlinks":613,
              "broken_simple_citations_omitted":27,
              "malformed_citations_omitted":19,
              "all_empty_targets_removed_in_quarantine_copy":659,
              "priority_broader_contexts_reviewed_nonallow":len(expected_broad),
              "new_source_drift_corrections":drift,
              "claim_rows":len(rows),"full_semantic_approvals":0,
              "generated_republication_permitted":False,
              "public_wiki_import_permitted":False,
              "review_copy_sha256":hashlib.sha256(sanitized.encode()).hexdigest(),
              "dispositions":dict(collections.Counter(r["disposition"] for r in rows))}
    return sanitized.encode(),report,rows

def main():
    p=argparse.ArgumentParser()
    for k in ("raw","prior","claims","unresolved","priority","out"):
        p.add_argument("--"+k,type=Path,required=True)
    a=p.parse_args()
    with a.priority.open(newline="",encoding="utf-8") as f:
        priority=list(csv.DictReader(f))
    result,report,rows=curate(a.raw.read_bytes(),
        json.loads(a.prior.read_text(encoding="utf-8")),
        json.loads(a.claims.read_text(encoding="utf-8")),
        json.loads(a.unresolved.read_text(encoding="utf-8")),priority)
    a.out.mkdir(parents=True,exist_ok=True)
    (a.out/"GENERATED_REVIEW_COPY_NOT_FOR_REPUBLICATION.md").write_bytes(result)
    (a.out/"613-CLAIM_AND_46-DEFECT_DISPOSITIONS.json").write_text(
        json.dumps(rows,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    (a.out/"frozen-curation-summary.json").write_text(
        json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,sort_keys=True))

if __name__=="__main__":
    main()
