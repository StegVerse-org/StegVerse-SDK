#!/usr/bin/env python3
"""Build a hashed artifact manifest for evaluator-boundary reproduction.

The output is descriptive evidence only. It grants no GitHub, runtime,
governance, signing, or custody authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


DEFAULT_ARTIFACTS = (
    "pyproject.toml",
    "inspection/request.schema.json",
    "inspection/examples/governed-test-request.json",
    "stegverse/public_inspection.py",
    "stegverse/sovereign_validation_runtime.py",
    "stegverse/evaluation_boundary_verifier.py",
    "tests/test_public_inspection_request.py",
    "tests/test_public_inspection_runtime.py",
    "tests/test_evaluation_boundary_contract.py",
    "EVALUATOR_MANIFEST_NON_INTERFERENCE_MIRROR_HANDOFF.md",
    "docs/ODA3_EVALUATION_BOUNDARY_TEST_PLAN.md",
    "README.md",
    "LICENSE",
)


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _git(args: list[str], root: Path) -> str | None:
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return proc.stdout.strip() or None


def build_manifest(root: Path) -> dict[str, Any]:
    artifacts = []
    missing = []
    for relative in DEFAULT_ARTIFACTS:
        path = root / relative
        if not path.is_file():
            missing.append(relative)
            continue
        artifacts.append(
            {
                "path": relative,
                "bytes": path.stat().st_size,
                "sha256": _sha256(path),
            }
        )

    return {
        "schema": "stegverse.evaluation-boundary-artifact-manifest.v1",
        "repository": "StegVerse-org/StegVerse-SDK",
        "source_commit": _git(["rev-parse", "HEAD"], root),
        "source_branch": _git(["rev-parse", "--abbrev-ref", "HEAD"], root),
        "working_tree_porcelain": _git(["status", "--porcelain"], root),
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
        "missing_expected_artifacts": missing,
        "authority_granted": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Hash evaluator-boundary artifacts and bind them to a Git source commit")
    parser.add_argument("--root", default=".", help="repository checkout root")
    parser.add_argument("--output", help="optional JSON output path")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    manifest = build_manifest(root)
    rendered = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")

    clean = manifest["working_tree_porcelain"] == ""
    complete = not manifest["missing_expected_artifacts"]
    source_bound = bool(manifest["source_commit"])
    return 0 if clean and complete and source_bound else 2


if __name__ == "__main__":
    raise SystemExit(main())
