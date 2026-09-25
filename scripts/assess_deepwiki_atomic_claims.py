#!/usr/bin/env python3
"""Evidence-limited atomic semantic assessment of every frozen DeepWiki citation.

Assess each individual claim/source pair. Exact source declarations may support a
*narrow source fact*, never an entire synthesized page, production observation,
ownership assertion, or publication right. All conclusions are DENY for import.
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import re
from pathlib import Path

ORIGINAL_SHA256 = "a729d9b0f487f785b0e8f92006f303e8520e3593b6eb6c4c5de43273daa72087"
SIMPLE = 640
ORIGINAL_LINK_CANDIDATES = 613
RISK = re.compile(
    r"\b(production|live|deployed|runtime|authentic(?:ated)?|"
    r"master\s*records|authoriz(?:ed|ation)|custody|grant(?:ed)?|"
    r"universally|guarantee(?:s|d)?)\b", re.I
)
SYMBOL = re.compile(r"(?m)^\s*(?:async\s+)?(?:def|class)\s+([A-Za-z_]\w*)\b")
ASSIGN = re.compile(
    r'(?m)^\s*([A-Z][A-Z0-9_]{3,})\s*=\s*(["\x27][^\n"\x27]{1,120}["\x27]|False|True|None|\d+)'
)
ENTRYPOINT = re.compile(
    r'(?m)^\s*([a-z][a-z\d-]{2,})\s*=\s*"([\w.]+:[A-Za-z_]\w*)"'
)
DEP = re.compile(r'(?m)^\s*"([a-z][a-z0-9-]{1,50}[!<>=~][^"\n]+)"')
TEST_ASSERT = re.compile(r"(?m)^\s*(?:self\.assert\w+\(|assert\s+)([^\n]+)")
CLAIM_CITES = re.compile(r"\[[^\]\n]+\]\(\)")
STOP = {"and","the","that","this","from","with","when","then","true",
        "false","none","only","have","been","does","which","must"}


def claim_near_reference(raw: str, offset: int) -> str:
    """Keep claim context adjacent to the citation, never the entire page."""
    a = raw.rfind("\n\n", 0, offset)
    a = 0 if a < 0 else a + 2
    segment = raw[a:offset]
    if segment.lstrip().startswith(("Sources:", "**Sources:**", "Source:")):
        previous = raw.rfind("\n\n", 0, max(0, a - 3))
        a = 0 if previous < 0 else previous + 2
        segment = raw[a:offset]
    # If this is a list or a table, the preceding row is the natural local claim.
    lines = segment.splitlines()
    if lines and (lines[-1].lstrip().startswith(("-", "*", "|")) or
                  segment.count("|") > 3):
        segment = lines[-1]
    segment = CLAIM_CITES.sub("", segment)
    # Remove code-fence diagrams from semantic-certification scope. Their
    # edges cannot be authenticated by matching node names in code.
    return re.sub(r"\s+", " ", segment[-1900:]).strip()


def source_class(path: str) -> str:
    p = path.lstrip("\x60/")
    if p.startswith(("tests/", "test_")):
        return "TEST_FIXTURE"
    if p.startswith("evidence/"):
        return "CHECKED_IN_EVIDENCE_NOT_EXTERNAL_AUTHENTICATION"
    if p.startswith(("docs/", "tasks/")) or "HANDOFF" in p or p == "README.md":
        return "SOURCE_DOCUMENTATION_NOT_RUNTIME"
    if p.startswith(".github/workflows/"):
        return "WORKFLOW_DECLARATION_NOT_RUN_EVIDENCE"
    if p.startswith("schemas/"):
        return "STATIC_SCHEMA_NOT_INGRESS_EVENT"
    if p == "pyproject.toml":
        return "PACKAGE_DECLARATION_NOT_DEPENDENCY_RIGHTS"
    if p.startswith(("stegverse/", "scripts/")):
        return "IMPLEMENTATION_SNIPPET_NOT_EXECUTION"
    return "UNCLASSIFIED_SOURCE"


def narrow_observations(claim: str, source: str, source_path: str) -> list[dict]:
    """Only exact assertion/identifier pairs; no numerical similarity scores."""
    found = []
    def add(kind: str, literal: str):
        if not any(x["literal"] == literal and x["kind"] == kind for x in found):
            found.append({"kind": kind, "literal": literal, "scope": "SOURCE_ONLY_NOT_FULL_CLAIM"})
    for m in SYMBOL.finditer(source):
        name = m.group(1)
        if len(name) >= 5 and re.search(r"(?<![\w])" + re.escape(name) + r"(?![\w])", claim):
            add("SOURCE_PYTHON_DECLARED_SYMBOL", name)
    for m in ASSIGN.finditer(source):
        key, value = m.groups()
        val = value.strip("\"'")
        if key in claim and (val in claim if len(val) >= 4 else
                             re.search(r"(?<![\w])" + re.escape(val) + r"(?![\w])", claim)):
            add("SOURCE_CONSTANT_EXACT_VALUE", key + " = " + value)
    if source_path == "pyproject.toml":
        for m in ENTRYPOINT.finditer(source):
            key, target = m.groups()
            if key in claim and target in claim:
                add("PACKAGE_DECLARED_ENTRYPOINT", key + " = " + target)
        for m in DEP.finditer(source):
            declaration = m.group(1)
            package = re.split(r"[!<>=~]", declaration, 1)[0]
            if declaration in claim:
                add("PACKAGE_DECLARED_REQUIREMENT", declaration)
            elif package in claim and re.search(re.escape(declaration).replace("\\", ""), claim):
                add("PACKAGE_DECLARED_REQUIREMENT", declaration)
    if source_path.startswith("tests/"):
        for m in TEST_ASSERT.finditer(source):
            body = m.group(1)
            identifiers = set(re.findall(r"\b[A-Za-z_]\w{4,}\b", body)) - STOP
            common = [x for x in identifiers if x in claim]
            # A test expectation confirms the existence of the assertion only.
            if len(common) >= 2:
                add("LOCAL_TEST_ASSERTION_ONLY", "; ".join(sorted(common)[:3]))
    if source_path.startswith(".github/workflows/"):
        for line in source.splitlines():
            if "python " in line:
                cmd = line.split("python ", 1)[1].strip().split()[0]
                if len(cmd) > 8 and cmd in claim:
                    add("DECLARED_CI_COMMAND_NOT_EXECUTION", cmd)
    if source_path.startswith("schemas/"):
        for ident in re.findall(r'"([A-Za-z_][\w-]{5,})"\s*:', source):
            if ident in claim:
                add("SCHEMA_KEY_PRESENT_NOT_VALIDATED_INGRESS", ident)
    return found[:12]


def assess(raw_bytes: bytes, claim_packet: dict, curations: list[dict],
           priority: list[dict], report: dict) -> dict:
    if hashlib.sha256(raw_bytes).hexdigest() != ORIGINAL_SHA256:
        raise ValueError("DENY:FROZEN_CAPTURE_BYTES_CHANGED")
    raw = raw_bytes.decode("utf-8")
    if (claim_packet["raw_sha256"] != ORIGINAL_SHA256 or
        report["input_sha256"] != ORIGINAL_SHA256 or
        len(claim_packet["rows"]) != SIMPLE or
        len(report["entries"]) != SIMPLE or len(curations) != 659 or
        claim_packet["candidate_total"] != ORIGINAL_LINK_CANDIDATES):
        raise ValueError("DENY:CLAIM_PACKET_OR_CITATION_PARTITION_CHANGED")
    if len(priority) != 75:
        raise ValueError("DENY:ORIGINAL_PRIORITY_EVIDENCE_INCOMPLETE")
    original = {int(r["occurrence_index"]): r for r in priority}
    if len(original) != 75:
        raise ValueError("DENY:DUPLICATED_PRIORITY_OCCURRENCE")
    records = []
    contexts = {}
    for i, entry in enumerate(claim_packet["rows"]):
        predecessor = curations[i]
        citation = report["entries"][i]
        if any((entry["offset"] != predecessor["offset"],
                entry["offset"] != citation["offset"],
                entry["label"] != citation["label"])):
            raise ValueError("DENY:PREDECESSOR_OCCURRENCE_MISMATCH:" + str(i))
        context = claim_near_reference(raw, entry["offset"])
        # The original full surrounding packet still retained for adjudication.
        context_hash = hashlib.sha256(context.encode("utf-8")).hexdigest()
        contexts.setdefault(context_hash, []).append(i)
        path = citation.get("candidate_path") or entry["label"].split(":")[0]
        category = source_class(path)
        source = entry.get("source_excerpt") or ""
        obs = narrow_observations(context, source, path)
        is_candidate = bool(citation.get("candidate_url"))
        risk = sorted({m.group(0).lower() for m in RISK.finditer(context)})
        if not is_candidate:
            verdict = "DENY:INVALID_OR_UNRESOLVED_ORIGINAL_CITATION"
            action = "Use separate 46-defect register; correct exact source and local claim before any linking."
        elif i in original and original[i]["status"] == "CITATION_CONTEXT_MISMATCH":
            verdict = "DENY:CONFIRMED_CITATION_CONTEXT_MISMATCH"
            action = "Replace cited source or rewrite unsupported diagram; compare named implementation modules."
        elif category in ("TEST_FIXTURE", "CHECKED_IN_EVIDENCE_NOT_EXTERNAL_AUTHENTICATION") and risk:
            verdict = "DENY:TEST_OR_RECORDED_STATUS_CANNOT_PROVE_LIVE_CLAIM"
            action = "Narrow claim to exact source-level assertion or require original authenticated runtime proof."
        elif obs:
            verdict = "NARROW_SOURCE_FACT_OBSERVED_FULL_CLAIM_DENIED"
            action = "Use only listed exact atomic facts in new first-party documentation; review all other clauses."
        elif category == "SOURCE_DOCUMENTATION_NOT_RUNTIME" and risk:
            verdict = "DENY:REPOSITORY_PROSE_CANNOT_AUTHENTICATE_RUNTIME"
            action = "Identify executable implementation plus original authority/custody receipts where required."
        elif category == "WORKFLOW_DECLARATION_NOT_RUN_EVIDENCE" and risk:
            verdict = "DENY:WORKFLOW_SOURCE_NOT_EXACT_HEAD_CI_EVIDENCE"
            action = "Check exact-head run logs and artifact for the specific validation, not workflow source alone."
        elif risk and category == "IMPLEMENTATION_SNIPPET_NOT_EXECUTION":
            verdict = "DENY:SOURCE_IMPLEMENTATION_CANNOT_PROVE_RUNTIME"
            action = "Separate code-path description from governed live execution and receipt evidence."
        else:
            verdict = "DENY:CLAIM_NOT_ENTAILED_BY_AVAILABLE_SOURCE_SPAN"
            action = "Inspect every asserted predicate against the exact source and tests; omit unsupported claims."
        if i in original and original[i]["status"] == "FULL_CLAIM_REVIEW_PENDING":
            if verdict == "NARROW_SOURCE_FACT_OBSERVED_FULL_CLAIM_DENIED":
                # Narrow declaration evidence cannot establish a complex diagram.
                verdict = "DENY:PRIORITY_BROADER_CONTEXT_WITH_ATOMIC_ONLY_SUPPORT"
        elif (i in original and
              original[i]["status"] == "NARROW_LITERAL_CONFIRMED_CONTEXT_NOT_FULLY_APPROVED"
              and not obs):
            verdict = "DENY:PREVIOUS_NARROW_FACT_EXACT_SOURCE_REVALIDATION_REQUIRED"
            action = ("Preserve prior narrow evidence but revalidate its exact historic "
                      "snippet/line; no current-source contradiction established.")
        records.append({
            "index": i, "page": entry["page"], "offset": entry["offset"],
            "source_label": entry["label"], "source_url": citation.get("candidate_url"),
            "source_revision": claim_packet["source_revision"],
            "original_DeepWiki_source_revision_parity": "UNKNOWN",
            "claim_unit_sha256": context_hash, "claim_unit_excerpt": context[:650],
            "source_excerpt_sha256": hashlib.sha256(source.encode()).hexdigest(),
            "source_category": category, "atomic_source_observations": obs,
            "risk_terms": risk, "priority75_original_status":
                original[i]["status"] if i in original else None,
            "disposition": verdict, "required_correction": action,
            "full_semantic_approval": False, "publication_allowed": False,
        })
    # This procedure genuinely assesses every original simple occurrence,
    # including broken citations, but never upgrades a token match to meaning.
    counts = dict(collections.Counter(x["disposition"] for x in records))
    by_page = {}
    for row in records:
        group = by_page.setdefault(row["page"], {"total": 0, "original_candidates": 0,
            "narrow_fact_available": 0, "full_semantic_approved": 0})
        group["total"] += 1
        group["original_candidates"] += bool(row["source_url"])
        group["narrow_fact_available"] += bool(row["atomic_source_observations"])
    pending = [x for x in records if curations[x["index"]]["disposition"] ==
               "DENY:PENDING_CLAIM_SPECIFIC_SEMANTIC_REVIEW"]
    summary = {
        "schema": "stegverse.deepwiki-atomic-semantic-evidence/v1",
        "raw_sha256": ORIGINAL_SHA256,
        "source_revision": claim_packet["source_revision"],
        "generation_time_source_parity": "UNKNOWN",
        "reviewed_simple_occurrences": len(records),
        "reviewed_original_candidates": sum(bool(x["source_url"]) for x in records),
        "pending538_reassessed": len(pending),
        "original_priority75_reassessed": sum(x["priority75_original_status"] is not None for x in records),
        "unique_nearby_claim_units": len(contexts),
        "narrow_source_observations": sum(bool(x["atomic_source_observations"]) for x in records),
        "full_claim_semantically_approved": 0,
        "generated_wiki_pages_approved": 0,
        "original_defective_citation_count": 46,
        "all_original_citations_hold_nonallow": True,
        "dispositions": counts,
        "page_summary": by_page,
    }
    if summary["pending538_reassessed"] != 538 or summary["original_priority75_reassessed"] != 75:
        raise ValueError("DENY:PRIORITY_OR_PREDECESSOR_538_MISMATCH")
    return {"summary": summary, "records": records, "claim_unit_members": contexts}


def main() -> None:
    p = argparse.ArgumentParser()
    for flag in ("raw", "claims", "curation", "priority", "report", "out"):
        p.add_argument("--" + flag, type=Path, required=True)
    a = p.parse_args()
    with a.priority.open(encoding="utf-8", newline="") as f:
        priority = list(csv.DictReader(f))
    result = assess(a.raw.read_bytes(),
        json.loads(a.claims.read_text(encoding="utf-8")),
        json.loads(a.curation.read_text(encoding="utf-8")), priority,
        json.loads(a.report.read_text(encoding="utf-8")))
    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / "613-ATOMIC-CLAIM-EVIDENCE-NONAUTHORITATIVE.json").write_text(
        json.dumps(result["records"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (a.out / "semantic-source-audit-summary.json").write_text(
        json.dumps(result["summary"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (a.out / "claim-context-deduplication.json").write_text(
        json.dumps(result["claim_unit_members"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result["summary"].items() if k != "page_summary"}, sort_keys=True))


if __name__ == "__main__":
    main()
