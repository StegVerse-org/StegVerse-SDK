#!/usr/bin/env python3
"""Verify the public SDK console and bundled AdmittedCode proof surface."""
from __future__ import annotations

import json
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from stegverse import cli
from stegverse.sdk_surfaces import list_sdk_surfaces

ROOT = Path(__file__).resolve().parents[1]


def capture(argv: list[str]) -> tuple[int, str]:
    stream = StringIO()
    with redirect_stdout(stream):
        code = cli.main(argv)
    return code, stream.getvalue()


def main() -> int:
    surfaces = list_sdk_surfaces()
    ids = {row["id"] for row in surfaces}
    required = {
        "admissibility",
        "llm-admissibility",
        "math-admissibility",
        "admittedcode",
        "universal-entry",
        "bridges",
        "entry-points",
    }

    checks: dict[str, bool] = {
        "all_required_surfaces_registered": required.issubset(ids),
        "all_surfaces_non_authorizing": all(row.get("authority_effect") == "NONE" for row in surfaces),
        "all_surfaces_have_help_metadata": all(row.get("summary") and row.get("command") and row.get("module") and row.get("documentation") for row in surfaces),
        "readme_exists": (ROOT / "README.md").is_file(),
        "console_docs_exist": (ROOT / "docs" / "SDK_CONSOLE.md").is_file(),
        "allow_fixture_exists": (ROOT / "examples" / "governed_llm_demo" / "admittedcode" / "admissibility_receipt.allow.json").is_file(),
        "deny_fixture_exists": (ROOT / "examples" / "governed_llm_demo" / "admittedcode" / "admissibility_receipt.deny.json").is_file(),
    }

    demo_code, demo_output = capture(["demo", "admittedcode"])
    checks["admittedcode_demo_exits_zero"] = demo_code == 0
    try:
        payload = json.loads(demo_output)
    except json.JSONDecodeError:
        payload = {}
    results = payload.get("results", {}) if isinstance(payload, dict) else {}
    checks["admittedcode_allow_accepted"] = results.get("allow", {}).get("verification", {}).get("status") == "ACCEPTED"
    checks["admittedcode_allow_preserved"] = results.get("allow", {}).get("verification", {}).get("decision") == "ALLOW"
    checks["admittedcode_deny_accepted"] = results.get("deny", {}).get("verification", {}).get("status") == "ACCEPTED"
    checks["admittedcode_deny_preserved"] = results.get("deny", {}).get("verification", {}).get("decision") == "DENY"
    checks["admittedcode_demo_non_authorizing"] = payload.get("authority_effect") == "NONE"

    help_code, help_output = capture(["help-surface", "admittedcode"])
    checks["admittedcode_help_exits_zero"] = help_code == 0
    checks["admittedcode_help_points_to_demo"] = "stegverse demo admittedcode" in help_output
    checks["admittedcode_help_explains_semantics"] = "result semantics" in help_output.lower()

    readme = (ROOT / "README.md").read_text(encoding="utf-8") if checks["readme_exists"] else ""
    docs = (ROOT / "docs" / "SDK_CONSOLE.md").read_text(encoding="utf-8") if checks["console_docs_exist"] else ""
    checks["readme_exposes_console"] = "stegverse surfaces" in readme
    checks["readme_exposes_admittedcode_demo"] = "stegverse demo admittedcode" in readme
    checks["docs_expose_admittedcode_demo"] = "stegverse demo admittedcode" in docs
    checks["readme_states_tvtvc_boundary"] = "TV/TVC" in readme

    status = "PASS" if all(checks.values()) else "FAIL"
    print(json.dumps({"status": status, "checks": checks}, indent=2, sort_keys=True))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
