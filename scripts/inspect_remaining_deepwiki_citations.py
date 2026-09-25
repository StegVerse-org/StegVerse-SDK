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

def inspect(raw: str, prior: dict, root: Path) -> dict:
    rows = []
    sha = prior["source_revision"]
    for item in prior["entries"]:
        if item.get("candidate_url"):
            continue
        row = propose(item["label"], root, sha)
        row.update({"page": item["page"], "offset": item["offset"]})
        rows.append(row)
    # Context-sensitive occurrences must not be parsed as independent links
    # until their original Markdown including nearby code fences is reviewed.
    complex_count = raw.count("]()") - len(prior["entries"])
    return {"schema": "stegverse.deepwiki-unresolved-review/v1",
            "original_sha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
            "source_revision": sha, "previous_unresolved_simple": len(rows),
            "malformed_contextual_occurrences": complex_count,
            "source_verified_suggestions": sum(bool(x["proposals"]) for x in rows),
            "resolved_for_publication": 0, "publication_allowed": False,
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
