#!/usr/bin/env python3
"""Create a complete *unreviewed* per-citation source/claim inspection packet.

Never asserts that lexical similarity establishes the truth of a DeepWiki claim.
The raw DeepWiki capture and candidate report are not modified.
"""
from __future__ import annotations
import argparse
import collections
import hashlib
import json
import re
from pathlib import Path

STOP = {"the", "that", "with", "from", "into", "this", "there", "their", "would",
        "does", "have", "must", "only", "when", "same", "source", "file", "code",
        "line", "lines", "through", "where", "these", "which", "will", "also"}
WORDS = re.compile(r"[A-Za-z_][A-Za-z_0-9]{3,}")
PAGE = re.compile(r"^# Page:\s*(.+?)\s*$", re.M)


def tokens(s: str) -> set[str]:
    return {x.lower() for x in WORDS.findall(s) if x.lower() not in STOP}


def claim_context(md: str, offset: int) -> str:
    """Nearby claim for *inspection*, not a verified sentence extraction."""
    start = max(md.rfind("\n\n", 0, offset), md.rfind("# Page:", 0, offset))
    start = 0 if start < 0 else start + (2 if md.startswith("\n\n", start) else 0)
    end = md.find("\n\n", offset)
    end = min(len(md), offset + 1100) if end < 0 else min(end, offset + 1100)
    return md[start:end][-1100:]


def source_span(root: Path, item: dict) -> tuple[str | None, str]:
    path = item.get("candidate_path")
    if not path:
        return None, "NO_UNAMBIGUOUS_SOURCE_PATH"
    r = root.resolve()
    p = (r / path).resolve()
    if not p.is_relative_to(r) or not p.is_file():
        return None, "SOURCE_NOT_FOUND"
    try:
        lines = p.read_text(encoding="utf-8").splitlines()
    except (UnicodeError, OSError):
        return None, "SOURCE_NOT_TEXT"
    m = re.search(r":(\d+)(?:-(\d+))?`?$", item["label"])
    if m:
        a, b = int(m.group(1)), int(m.group(2) or m.group(1))
        if a < 1 or b > len(lines) or b < a:
            return None, "LINE_SPAN_NOT_CURRENT"
        return "\n".join(lines[a - 1:b]), "EXACT_DECLARED_SOURCE_SPAN"
    return "\n".join(lines[:100]), "FILE_PREVIEW_FIRST_100_LINES"


def build(md: str, report: dict, root: Path) -> dict:
    rows = []
    unique = {}
    for i, entry in enumerate(report["entries"]):
        claim = claim_context(md, entry["offset"])
        excerpt, proof = source_span(root, entry)
        a, b = tokens(claim), tokens(excerpt or "")
        overlap = sorted(a & b)
        # This is a triage signal only; exact matched tokens are not semantic proof.
        signal = "NOT_ASSESSABLE" if excerpt is None else (
            "LOW_LEXICAL_OVERLAP_REVIEW_FIRST" if len(overlap) < 2 else
            "LEXICAL_OVERLAP_STILL_REQUIRES_HUMAN_REVIEW")
        row = {"index": i, "page": entry["page"], "label": entry["label"],
               "offset": entry["offset"], "disposition": entry["disposition"],
               "source_url": entry["candidate_url"], "source_status": proof,
               "claim_context": claim, "source_excerpt": excerpt,
               "overlap_tokens": overlap[:30], "triage_signal": signal,
               "semantic_verified": False}
        rows.append(row)
        if entry["candidate_url"]:
            unique.setdefault(entry["candidate_url"], []).append(i)
    return {"schema": "stegverse.deepwiki-claim-review/v1",
            "raw_sha256": hashlib.sha256(md.encode("utf-8")).hexdigest(),
            "source_revision": report["source_revision"],
            "raw_citation_count": md.count("]()"),
            "candidate_total": len([x for x in rows if x["source_url"]]),
            "candidate_unique_urls": len(unique),
            "semantic_verified_count": 0,
            "source_revision_parity": "NOT_ESTABLISHED",
            "human_review_required": True, "publication_allowed": False,
            "triage_counts": dict(collections.Counter(x["triage_signal"] for x in rows)),
            "candidate_url_occurrences": unique, "rows": rows}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    ap.add_argument("--root", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    raw = a.input.read_text(encoding="utf-8")
    previous = json.loads(a.report.read_text(encoding="utf-8"))
    if hashlib.sha256(raw.encode("utf-8")).hexdigest() != previous["input_sha256"]:
        raise ValueError("Raw capture hash differs from citation resolver input")
    result = build(raw, previous, a.root)
    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / "source-claim-inspection-UNREVIEWED.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("raw_citation_count",
          "candidate_total", "candidate_unique_urls", "semantic_verified_count",
          "triage_counts", "publication_allowed")}, sort_keys=True))


if __name__ == "__main__":
    main()
