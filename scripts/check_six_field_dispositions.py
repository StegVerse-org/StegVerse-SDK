#!/usr/bin/env python3
"""Find refusals that lack the six-field actionable disposition.

Every non-ALLOW result (FAIL_CLOSED, DENY, BLOCK, BLOCKED, REFUSED) must carry
all six fields on the refusal object itself:

    failure_code, failed_predicate, required_evidence_or_repair,
    retry_entrypoint, owning_existing_goal, next_attempt

Scans JSON files (structurally) and GitHub workflow YAML files (heuristically,
``run:`` blocks only, without a YAML parser).  Standard library only.

Usage:
    python3 scripts/check_six_field_dispositions.py [paths...]
        [--output report.json] [--allow-legacy-file FILE]

Exit status is 0 only when the report disposition is ALLOW.
See docs/SIX_FIELD_DISPOSITION_CHECK.md.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

SCHEMA_ID = "stegverse.six-field-disposition-check.v1"
OWNING_GOAL = "SDK-STRUCTURAL-VALIDATOR-CONSOLIDATION-001"
RETRY_ENTRYPOINT = "scripts/check_six_field_dispositions.py"

SIX_FIELDS: Tuple[str, ...] = (
    "failure_code",
    "failed_predicate",
    "required_evidence_or_repair",
    "retry_entrypoint",
    "owning_existing_goal",
    "next_attempt",
)
NON_ALLOW = frozenset({"FAIL_CLOSED", "DENY", "BLOCK", "BLOCKED", "REFUSED"})
RESULT_KEYS: Tuple[str, ...] = ("disposition", "status", "decision", "result")
SKIP_DIRS = frozenset({".git", "node_modules", ".venv", "venv", "__pycache__"})
EXEMPTION_KEYS: Tuple[str, ...] = ("path", "reason", "owning_existing_goal")

_NON_ALLOW_RE = re.compile(
    r"(?<![A-Za-z0-9_])(" + "|".join(sorted(NON_ALLOW, key=len, reverse=True)) + r")(?![A-Za-z0-9_])"
)
_OUTPUT_RE = re.compile(
    r"(?<![A-Za-z0-9_])(echo|printf)(?![A-Za-z0-9_])"
    r"|(?<![A-Za-z0-9_.])print\("
    r"|(?<![A-Za-z0-9_])cat\s+<<"
    r'|>>\s*"?\$\{?GITHUB_OUTPUT'
    r"|::error"
)
_HEREDOC_RE = re.compile(r"""(?<![A-Za-z0-9_])cat\s+<<-?\s*(['"]?)([A-Za-z_][A-Za-z0-9_]*)\1""")
_RUN_RE = re.compile(r"^(\s*)(-\s+)?run\s*:(.*)$")
_BLOCK_SCALAR_RE = re.compile(r"^[|>][0-9+-]*\s*(#.*)?$")
_FIELD_RES = {f: re.compile(r"(?<![A-Za-z0-9_])" + re.escape(f) + r"(?![A-Za-z0-9_])") for f in SIX_FIELDS}


# --------------------------------------------------------------------------- #
# File discovery
# --------------------------------------------------------------------------- #

def _display(path: Path) -> str:
    try:
        return path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _is_json(path: Path) -> bool:
    return path.suffix == ".json"


def _is_workflow(path: Path) -> bool:
    return path.suffix in (".yml", ".yaml")


def discover(paths: Iterable[str]) -> Tuple[List[Path], List[Path], List[Dict[str, str]]]:
    json_files: set = set()
    workflow_files: set = set()
    skipped: List[Dict[str, str]] = []
    for raw in paths:
        p = Path(raw)
        if p.is_file():
            candidates: Iterable[Path] = [p]
        elif p.is_dir():
            found: List[Path] = []
            for dirpath, dirnames, filenames in os.walk(p):
                dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
                found.extend(Path(dirpath) / f for f in filenames)
            candidates = found
        else:
            skipped.append({"path": _display(p) if p.is_absolute() else p.as_posix(), "reason": "not_found"})
            continue
        for c in candidates:
            if _is_json(c):
                json_files.add(c.resolve())
            elif _is_workflow(c):
                workflow_files.add(c.resolve())
    return sorted(json_files), sorted(workflow_files), skipped


# --------------------------------------------------------------------------- #
# JSON scanning
# --------------------------------------------------------------------------- #

def _pointer_token(token: Any) -> str:
    return str(token).replace("~", "~0").replace("/", "~1")


def _is_empty(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    if isinstance(value, (list, dict)):
        return len(value) == 0
    return False


def _non_allow_value(obj: Dict[str, Any]) -> Optional[Tuple[str, str]]:
    for key in RESULT_KEYS:
        value = obj.get(key)
        if isinstance(value, str) and value in NON_ALLOW:
            return key, value
    return None


def scan_json_value(doc: Any, path: str) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []

    def walk(node: Any, pointer: str) -> None:
        if isinstance(node, dict):
            hit = _non_allow_value(node)
            if hit is not None:
                missing = [f for f in SIX_FIELDS if f not in node or _is_empty(node[f])]
                if missing:
                    findings.append({
                        "kind": "json",
                        "path": path,
                        "pointer": pointer,
                        "key": hit[0],
                        "value": hit[1],
                        "missing_fields": missing,
                    })
            for k in sorted(node, key=str):
                walk(node[k], pointer + "/" + _pointer_token(k))
        elif isinstance(node, list):
            for i, item in enumerate(node):
                walk(item, pointer + "/" + str(i))

    walk(doc, "")
    return findings


def _is_schema_file(path: Path, doc: Any) -> bool:
    return path.name.endswith(".schema.json") or (isinstance(doc, dict) and "$schema" in doc)


# --------------------------------------------------------------------------- #
# Workflow scanning (heuristic, no YAML parser)
# --------------------------------------------------------------------------- #

def _indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def extract_run_blocks(text: str) -> List[Tuple[int, List[str]]]:
    """Return (1-based line of the ``run:`` key, body lines) for each run block."""
    lines = text.splitlines()
    blocks: List[Tuple[int, List[str]]] = []
    i = 0
    while i < len(lines):
        m = _RUN_RE.match(lines[i])
        if not m:
            i += 1
            continue
        key_col = len(m.group(1)) + len(m.group(2) or "")
        value = m.group(3).strip()
        start = i + 1
        if _BLOCK_SCALAR_RE.match(value):
            body: List[str] = []
            j = i + 1
            while j < len(lines):
                ln = lines[j]
                if ln.strip() == "" or _indent(ln) > key_col:
                    body.append(ln)
                    j += 1
                else:
                    break
            while body and body[-1].strip() == "":
                body.pop()
            blocks.append((start, body))
            i = j
        else:
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
                value = value[1:-1]
            blocks.append((start, [value]))
            i += 1
    return blocks


def _refusal_emissions(body: List[str]) -> List[Tuple[int, str]]:
    emissions: List[Tuple[int, str]] = []
    heredoc_end: Optional[str] = None
    for offset, ln in enumerate(body):
        stripped = ln.strip()
        if heredoc_end is not None:
            if stripped == heredoc_end:
                heredoc_end = None
                continue
            is_output = True
        else:
            is_output = bool(_OUTPUT_RE.search(ln))
            hd = _HEREDOC_RE.search(ln)
            if hd:
                heredoc_end = hd.group(2)
        if stripped.startswith("#"):
            continue
        if is_output:
            tok = _NON_ALLOW_RE.search(ln)
            if tok:
                emissions.append((offset, tok.group(1)))
    return emissions


def scan_workflow_text(text: str, path: str) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    for line_no, body in extract_run_blocks(text):
        emissions = _refusal_emissions(body)
        if not emissions:
            continue
        joined = "\n".join(body)
        missing = [f for f in SIX_FIELDS if not _FIELD_RES[f].search(joined)]
        if missing:
            findings.append({
                "kind": "workflow",
                "path": path,
                "line": line_no,
                "tokens": sorted({t for _, t in emissions}),
                "missing_fields": missing,
            })
    return findings


# --------------------------------------------------------------------------- #
# Exemptions
# --------------------------------------------------------------------------- #

def load_exemptions(file: Optional[str]) -> Tuple[List[Dict[str, str]], List[str]]:
    if not file:
        return [], []
    errors: List[str] = []
    try:
        data = json.loads(Path(file).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return [], [f"{file}: unreadable exemption file ({exc.__class__.__name__})"]
    entries = data.get("entries") if isinstance(data, dict) else None
    if not isinstance(entries, list):
        return [], [f"{file}: missing 'entries' list"]
    valid: List[Dict[str, str]] = []
    for idx, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append(f"{file}: entries/{idx} is not an object")
            continue
        missing = [k for k in EXEMPTION_KEYS if not isinstance(entry.get(k), str) or not entry[k].strip()]
        if missing:
            errors.append(f"{file}: entries/{idx} missing {', '.join(missing)}")
            continue
        valid.append({k: entry[k] for k in EXEMPTION_KEYS})
    return valid, errors


def _exempting_entry(finding_path: str, entries: List[Dict[str, str]]) -> Optional[Dict[str, str]]:
    for entry in entries:
        pat = entry["path"].replace("\\", "/")
        if pat.startswith("./"):
            pat = pat[2:]
        if (
            finding_path == pat
            or finding_path.endswith("/" + pat)
            or fnmatch.fnmatchcase(finding_path, pat)
        ):
            return entry
    return None


# --------------------------------------------------------------------------- #
# Report
# --------------------------------------------------------------------------- #

def _sort_key(f: Dict[str, Any]) -> Tuple[str, str, int, str]:
    return (f["path"], f["kind"], int(f.get("line", 0)), f.get("pointer", ""))


def run(paths: List[str], allow_legacy_file: Optional[str] = None) -> Dict[str, Any]:
    json_files, workflow_files, skipped = discover(paths)
    findings: List[Dict[str, Any]] = []
    n_json = 0
    n_workflows = 0

    for f in json_files:
        shown = _display(f)
        try:
            doc = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, ValueError, UnicodeDecodeError):
            skipped.append({"path": shown, "reason": "unparsable_json"})
            continue
        if _is_schema_file(f, doc):
            skipped.append({"path": shown, "reason": "json_schema"})
            continue
        n_json += 1
        findings.extend(scan_json_value(doc, shown))

    for f in workflow_files:
        shown = _display(f)
        try:
            text = f.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            skipped.append({"path": shown, "reason": "unreadable_workflow"})
            continue
        n_workflows += 1
        findings.extend(scan_workflow_text(text, shown))

    entries, exemption_errors = load_exemptions(allow_legacy_file)
    remaining: List[Dict[str, Any]] = []
    exempted: List[Dict[str, Any]] = []
    for finding in findings:
        entry = _exempting_entry(finding["path"], entries)
        if entry is None:
            remaining.append(finding)
        else:
            exempted.append(dict(finding, exemption=entry))

    report: Dict[str, Any] = {
        "schema": SCHEMA_ID,
        "scanned": {
            "json": n_json,
            "workflows": n_workflows,
            "skipped": sorted(skipped, key=lambda s: (s["path"], s["reason"])),
        },
        "findings": sorted(remaining, key=_sort_key),
        "exempted": sorted(exempted, key=_sort_key),
    }

    if exemption_errors:
        report["exemption_errors"] = exemption_errors
        report.update(
            disposition="FAIL_CLOSED",
            failure_code="EXEMPTION_DECLARATION_INCOMPLETE",
            failed_predicate="EVERY_EXEMPTION_DECLARES_PATH_REASON_AND_OWNING_GOAL",
            required_evidence_or_repair=(
                "Give every entry in the --allow-legacy-file 'entries' list non-empty "
                "'path', 'reason' and 'owning_existing_goal' strings."
            ),
        )
    elif n_json + n_workflows == 0:
        report.update(
            disposition="FAIL_CLOSED",
            failure_code="NO_INPUTS_SCANNED",
            failed_predicate="AT_LEAST_ONE_INPUT_SCANNED",
            required_evidence_or_repair=(
                "Point the check at paths containing *.json result files or *.yml/*.yaml "
                "workflows; an empty scan is never ALLOW."
            ),
        )
    elif remaining:
        report.update(
            disposition="FAIL_CLOSED",
            failure_code="SIX_FIELD_DISPOSITION_INCOMPLETE",
            failed_predicate="EVERY_NON_ALLOW_RESULT_CARRIES_SIX_FIELDS",
            required_evidence_or_repair=(
                "Add the listed missing fields directly on each refusal object (not under a "
                "nested child object) or in the same workflow run block, or declare an "
                "exemption with path, reason and owning_existing_goal."
            ),
        )
    else:
        report["disposition"] = "ALLOW"

    if report["disposition"] != "ALLOW":
        report["retry_entrypoint"] = RETRY_ENTRYPOINT
        report["owning_existing_goal"] = OWNING_GOAL
        report["next_attempt"] = (
            "Re-run python3 " + RETRY_ENTRYPOINT + " " + " ".join(paths)
            + (" --allow-legacy-file " + allow_legacy_file if allow_legacy_file else "")
            + " after repair."
        )
    return report


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("paths", nargs="*", default=["."], help="files or directories (default: .)")
    parser.add_argument("--output", help="write the JSON report here instead of stdout")
    parser.add_argument("--allow-legacy-file", help="JSON file of declared exemptions")
    args = parser.parse_args(argv)

    report = run(args.paths or ["."], args.allow_legacy_file)
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"{report['disposition']}: {len(report['findings'])} finding(s); report at {args.output}")
    else:
        sys.stdout.write(text)
    return 0 if report["disposition"] == "ALLOW" else 1


if __name__ == "__main__":
    sys.exit(main())
