"""StegVerse governance gate for any GitHub repository (free tier).

Runs inside another organization's CI with the standard library only: it loads
the SDK's own verifier and structural validator modules by path, without
importing the package (whose dependencies a caller need not install).

Checks:
- every portable governance evidence bundle found under the bundle globs is
  independently verified (stegverse.portable-governance-verification-bundle);
- every JSON Schema file is classified against the SDK structural validator
  contract (informational; it never fails the gate).

The report is evidence only. It grants no execution, admissibility, standing,
custody or credential authority, and records metered units for tier pricing.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import sys
import types
from pathlib import Path
from typing import Sequence

REPORT_SCHEMA = "stegverse.governance-gate-report.v1"
TIER = "FREE"
FREE_TIER_LIMITS = {"bundles": 25, "schemas": 200}
DEFAULT_BUNDLE_GLOBS = (".stegverse/governance/**/*.json",)
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__"}
PACKAGE_DIR = Path(__file__).resolve().parent
DISPOSITIONS = {"ALLOW", "DENY", "FAIL_CLOSED"}
OWNING_EXISTING_GOAL = "SDK-STRUCTURAL-VALIDATOR-CONSOLIDATION-001"
RETRY_ENTRYPOINT = "stegverse/governance_gate.py::run_gate"
_NON_ALLOW = {
    "NO_GOVERNANCE_BUNDLES_FOUND": (
        "AT_LEAST_ONE_PORTABLE_GOVERNANCE_BUNDLE",
        "Commit at least one stegverse.portable-governance-verification-bundle.v1 object "
        "matching the bundle glob. The manifest constraint lives inside that bundle.",
        "Rerun this checker after the bundle is in the repository. An empty glob is not a verification.",
    ),
    "FREE_TIER_LIMIT_EXCEEDED": (
        "BUNDLE_AND_SCHEMA_COUNTS_WITHIN_RECORDED_LIMITS",
        "Select at most 25 bundles and 200 classified schemas. The recorded limits are "
        "FREE_TIER_LIMITS in stegverse/governance_gate.py.",
        "Rerun this checker on a selection inside those limits.",
    ),
    "BUNDLE_VERIFICATION_FAILED": (
        "EVERY_SELECTED_BUNDLE_RECOMPUTES",
        "Repair each bundle whose status is not ALLOW so its manifest hashes, predecessor "
        "receipt references, and identity fields match. The bundle error is on this report.",
        "Rerun this checker on the repaired bundles. Do not retry a bundle whose hashes do not match.",
    ),
}


def _sdk_module(name: str):
    """Import stegverse.<name> without executing stegverse/__init__.py."""
    package = sys.modules.get("stegverse")
    if package is None or not hasattr(package, "__path__"):
        package = types.ModuleType("stegverse")
        package.__path__ = [str(PACKAGE_DIR)]
        sys.modules["stegverse"] = package
    return importlib.import_module(f"stegverse.{name}")


def _files(root: Path, patterns: Sequence[str]) -> list[Path]:
    found = set()
    for pattern in patterns:
        for path in root.glob(pattern):
            if path.is_file() and not SKIP_DIRS.intersection(path.relative_to(root).parts):
                found.add(path)
    return sorted(found)


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _is_schema_file(path: Path, document) -> bool:
    return isinstance(document, dict) and (
        "$schema" in document or path.name.endswith(".schema.json")
    )


def verify_bundles(root: Path, patterns: Sequence[str]) -> list[dict]:
    verifier = _sdk_module("portable_governance_verifier")
    results = []
    for path in _files(root, patterns):
        rel = path.relative_to(root).as_posix()
        try:
            document = _load(path)
            if not isinstance(document, dict):
                raise ValueError("bundle JSON root must be an object")
            report = verifier.verify_portable_governance_bundle(document)
            results.append({"path": rel, "status": _gate_status(report.get("status", "FAIL_CLOSED")),
                            "report_sha256": hashlib.sha256(json.dumps(report, sort_keys=True).encode()).hexdigest()})
        except (OSError, ValueError, TypeError, KeyError, RecursionError) as exc:
            results.append({"path": rel, "status": "FAIL_CLOSED", "error": f"{type(exc).__name__}: {exc}"})
    return results


def classify_schemas(root: Path) -> list[dict]:
    validator = _sdk_module("structural_validator_candidate")
    results = []
    for path in _files(root, ("**/*.json",)):
        try:
            document = _load(path)
        except (OSError, ValueError, RecursionError):
            continue
        if not _is_schema_file(path, document):
            continue
        digest = hashlib.sha256(validator.canonical_bytes(document)).hexdigest() if _encodable(validator, document) else None
        admitted = validator.check_schema(document, digest) if digest else {"valid": False, "errors": [{"code": "INVALID_SCHEMA_ENCODING"}]}
        results.append({"path": path.relative_to(root).as_posix(),
                        "sdk_contract_compatible": bool(admitted["valid"]),
                        "blocking_codes": sorted({e["code"] for e in admitted.get("errors", [])})})
    return results


def _encodable(validator, document) -> bool:
    try:
        validator.canonical_bytes(document)
        return True
    except (TypeError, ValueError, RecursionError):
        return False


def _gate_status(status: object) -> str:
    """Map a verifier status onto ALLOW, DENY, or FAIL_CLOSED."""
    if status == "PASS":
        status = "ALLOW"
    if status not in DISPOSITIONS:
        return "FAIL_CLOSED"
    return str(status)


def _non_allow(reason: str) -> dict:
    failed_predicate, repair, next_attempt = _NON_ALLOW[reason]
    return {
        "failure_code": reason,
        "failed_predicate": failed_predicate,
        "required_evidence_or_repair": repair,
        "retry_entrypoint": RETRY_ENTRYPOINT,
        "owning_existing_goal": OWNING_EXISTING_GOAL,
        "next_attempt": next_attempt,
    }


def read_workflow_disposition(path: str | Path) -> str:
    """Return the report disposition, or FAIL_CLOSED when the file is missing or unparsable."""
    try:
        report = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError):
        return "FAIL_CLOSED"
    if not isinstance(report, dict):
        return "FAIL_CLOSED"
    value = report.get("disposition")
    if value not in DISPOSITIONS:
        return "FAIL_CLOSED"
    return str(value)


def run_gate(root: Path, bundle_globs: Sequence[str] = DEFAULT_BUNDLE_GLOBS, check_schemas: bool = True) -> dict:
    bundles = verify_bundles(root, bundle_globs)
    schemas = classify_schemas(root) if check_schemas else []
    over_limit = {name: count for name, count in (("bundles", len(bundles)), ("schemas", len(schemas)))
                  if count > FREE_TIER_LIMITS[name]}
    failed = [b for b in bundles if b["status"] != "ALLOW"]
    if over_limit:
        disposition = "FAIL_CLOSED"
        reason = "FREE_TIER_LIMIT_EXCEEDED"
    elif not bundles:
        disposition = "FAIL_CLOSED"
        reason = "NO_GOVERNANCE_BUNDLES_FOUND"
    elif failed:
        disposition = "FAIL_CLOSED"
        reason = "BUNDLE_VERIFICATION_FAILED"
    else:
        disposition = "ALLOW"
        reason = "ALL_BUNDLES_VERIFIED"
    report = {
        "schema": REPORT_SCHEMA,
        "tier": TIER,
        "disposition": disposition,
        "reason": reason,
        "usage": {"bundles_verified": len(bundles), "schemas_classified": len(schemas),
                  "limits": FREE_TIER_LIMITS, "over_limit": over_limit},
        "bundles": bundles,
        "schemas": {"compatible": sum(s["sdk_contract_compatible"] for s in schemas), "total": len(schemas),
                    "files": schemas},
        "sdk_validator_contract": _sdk_module("structural_validator_candidate").CONTRACT["contract_version"],
        "authority": {"verification_authority": "NONE", "execution_authorized": False, "standing_minted": False,
                      "admissibility_decided": False, "custody_claimed": False, "credential_issued": False},
    }
    if disposition != "ALLOW":
        report.update(_non_allow(reason))
    return report


def _summary(report: dict) -> str:
    lines = [f"## StegVerse governance gate: {report['disposition']}", "",
             f"Tier: {report['tier']} | Reason: `{report['reason']}`", "",
             f"Governance bundles verified: {report['usage']['bundles_verified']}",
             f"Schemas compatible with SDK validator contract {report['sdk_validator_contract']}: "
             f"{report['schemas']['compatible']}/{report['schemas']['total']}", ""]
    for bundle in report["bundles"]:
        lines.append(f"- `{bundle['path']}`: {bundle['status']}" + (f" ({bundle['error']})" if "error" in bundle else ""))
    lines += ["", "Evidence only: this gate grants no execution, admissibility, standing, custody or credential authority."]
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="stegverse-governance-gate", description=__doc__.splitlines()[0])
    parser.add_argument("root", nargs="?", default=".", help="Repository root to check")
    parser.add_argument("--bundle-glob", action="append", help="Glob for governance bundles (repeatable)")
    parser.add_argument("--no-schemas", action="store_true", help="Skip JSON Schema classification")
    parser.add_argument("--output", help="Write the JSON report here (default: stdout)")
    parser.add_argument("--summary", help="Append a Markdown summary here (e.g. $GITHUB_STEP_SUMMARY)")
    args = parser.parse_args(argv)
    report = run_gate(Path(args.root).resolve(), tuple(args.bundle_glob or DEFAULT_BUNDLE_GLOBS), not args.no_schemas)
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    if args.summary:
        with open(args.summary, "a", encoding="utf-8") as handle:
            handle.write(_summary(report))
    return 0 if report["disposition"] == "ALLOW" else 1


if __name__ == "__main__":
    raise SystemExit(main())
