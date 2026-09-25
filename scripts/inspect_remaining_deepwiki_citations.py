#!/usr/bin/env python3
"""Source-verify uniquely reconstructable unresolved DeepWiki citations.

Produces review *proposals*, not publication replacements. Preserves raw text.
"""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import quote

FUNCTION = re.compile(r"^([\w./-]+\.py):([A-Za-z_]\w*)$")
RANGE = re.compile(r"^(.+?):(\d+)(?:-(\d+))?$")

def propose(label: str, root: Path, sha: str) -> dict:
    original = label.strip(" `")
    reason = None
    # Strip repo-root leading slash only if the *exact* ensuing path exists.
    normalized = original.lstrip("/") if original.startswith("/.github/") else original
    root = root.resolve()
    symbol = FUNCTION.fullmatch(normalized)
    if symbol:
        path, name = symbol.groups()
        file = (root / path).resolve()
        if not file.is_relative_to(root) or not file.is_file():
            return {"label": label, "disposition": "SOURCE_ABSENT", "proposals": []}
        try:
            tree = ast.parse(file.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, SyntaxError):
            return {"label": label, "disposition": "SYMBOL_SOURCE_UNREADABLE", "proposals": []}
        defs = [node for node in ast.walk(tree) if isinstance(
            node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name]
        if len(defs) != 1:
            return {"label": label, "disposition": "SYMBOL_NOT_UNIQUE", "proposals": []}
        a, b = defs[0].lineno, defs[0].end_lineno
        reason = "EXACT_SYMBOL_DEFINITION_SOURCE_VERIFIED_SEMANTICS_UNREVIEWED"
    else:
        m = RANGE.fullmatch(normalized)
        if not m:
            return {"label": label, "disposition": "COMPOSITE_OR_NONLOCATOR_REVIEW", "proposals": []}
        path, a, b = m.group(1), int(m.group(2)), int(m.group(3) or m.group(2))
        file = (root / path).resolve()
        if not file.is_relative_to(root) or not file.is_file():
            return {"label": label, "disposition": "SOURCE_ABSENT", "proposals": []}
        try:
            count = len(file.read_text(encoding="utf-8").splitlines())
        except (OSError, UnicodeError):
            return {"label": label, "disposition": "SOURCE_UNREADABLE", "proposals": []}
        if a < 1 or b < a:
            return {"label": label, "disposition": "INVALID_LINE_RANGE", "proposals": []}
        if b > count:
            # Do not silently clip the original generated reference.
            return {"label": label, "disposition": "LINE_RANGE_INCORRECT",
                    "source_lines": count, "declared_range": [a, b],
                    "proposed_clipped_range": [a, count] if a <= count else None,
                    "proposals": []}
        reason = ("UNAMBIGUOUS_ROOT_SLASH_NORMALIZED_SEMANTICS_UNREVIEWED" if
                  normalized != original else "SOURCE_LINE_VERIFIED_SEMANTICS_UNREVIEWED")
    url = ("https://github.com/StegVerse-org/StegVerse-SDK/blob/" + sha +
           "/" + quote(path, safe="/") + f"#L{a}" + (f"-L{b}" if b != a else ""))
    return {"label": label, "disposition": reason, "proposals": [url],
            "source_revision": sha, "semantic_verified": False}


SOURCE_SPAN = re.compile(r"(?P<path>[A-Za-z0-9_.\\/-]+\\.[A-Za-z0-9]+):(?P<start>\\d+)(?:-(?P<end>\\d+))?")
CONTINUED_RANGE = re.compile(r"\\s*,\\s*(\\d+)(?:-(\\d+))?")


def composite_proposals(label: str, root: Path, sha: str) -> dict:
    """Return individually checked anchors; never treat a partial list as resolved."""
    out = []
    covered = []
    for match in SOURCE_SPAN.finditer(label):
        path = match.group("path").lstrip("\u0060")
        values = [(match.group("start"), match.group("end"))]
        end = match.end()
        while True:
            following = CONTINUED_RANGE.match(label, end)
            if not following:
                break
            values.append(following.groups())
            end = following.end()
        for a, b in values:
            p = propose(f"{path}:{a}" + (f"-{b}" if b else ""), root, sha)
            out.append({"fragment": f"{path}:{a}" + (f"-{b}" if b else ""),
                        "disposition": p["disposition"],
                        "candidate_urls": p.get("proposals", [])})
        covered.append([match.start(), end])
    return {"subreferences": out, "covered_offsets": covered,
            "validated_subreferences": sum(bool(x["candidate_urls"]) for x in out),
            "partial_or_ambiguous": True, "semantic_verified": False}

def inspect(raw: str, prior: dict, root: Path) -> dict:
    rows = []
    sha = prior["source_revision"]
    for item in prior["entries"]:
        if item.get("candidate_url"):
            continue
        row = propose(item["label"], root, sha)
        if not row["proposals"] and row["disposition"] in ("COMPOSITE_OR_NONLOCATOR_REVIEW", "SOURCE_ABSENT"):\n            row["composite_review"] = composite_proposals(item["label"], root, sha)\n        row.update({"page": item["page"], "offset": item["offset"]})
        rows.append(row)
    # Context-sensitive occurrences must not be parsed as independent links
    # until their original Markdown including nearby code fences is reviewed.
    simple_spans = [(x["offset"], x["offset"] + len(x["label"]) + 4) for x in prior["entries"]]\n    malformed = []\n    for m in re.finditer(r"\\]\\(\\)", raw):\n        if any(a <= m.start() < b for a, b in simple_spans):\n            continue\n        preceding = raw[max(0, m.start() - 160):m.end()]\n        tail = list(SOURCE_SPAN.finditer(preceding))\n        candidate = tail[-1] if tail else None\n        row = {"offset": m.start(), "context": preceding[-160:],\n               "source_candidate": None, "publication_allowed": False}\n        if candidate and preceding[candidate.end():].startswith("]()"):\n            path, start, end = (candidate.group("path"),\n                                candidate.group("start"), candidate.group("end"))\n            ref = f"{path}:{start}" + (f"-{end}" if end else "")\n            row["source_candidate"] = propose(ref, root, sha)\n        malformed.append(row)\n    complex_count = len(malformed)
    return {"schema": "stegverse.deepwiki-unresolved-review/v1",
            "original_sha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
            "source_revision": sha, "previous_unresolved_simple": len(rows),
            "malformed_contextual_occurrences": complex_count,
            "source_verified_suggestions": sum(bool(x["proposals"]) for x in rows),
            "resolved_for_publication": 0, "publication_allowed": False,\n            "malformed_contextual_entries": malformed,
            "entries": rows}

def main():
    p = argparse.ArgumentParser()
    for name in ("input", "report", "root", "out"):
        p.add_argument("--" + name, type=Path, required=True)
    a = p.parse_args()
    raw = a.input.read_text(encoding="utf-8")
    prior = json.loads(a.report.read_text(encoding="utf-8"))
    if hashlib.sha256(raw.encode("utf-8")).hexdigest() != prior["input_sha256"]:
        raise ValueError("Original capture changed")
    result = inspect(raw, prior, a.root)
    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / "remaining-citation-proposals-UNREVIEWED.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k:result[k] for k in ("previous_unresolved_simple",
        "malformed_contextual_occurrences", "source_verified_suggestions",
        "resolved_for_publication", "publication_allowed")}, sort_keys=True))

if __name__ == "__main__":
    main()
