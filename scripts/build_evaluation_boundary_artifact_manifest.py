#!/usr/bin/env python3
"""Build a hashed artifact manifest for evaluator-boundary reproduction.

The output is descriptive evidence only. It grants no GitHub, runtime,
governance, signing, or custody authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
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

_COMMIT_RE = re.compile(r"^[0-9a-fA-F]{40}$")


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


def build_manifest(
    root: Path,
    *,
    source_commit: str | None = None,
    source_branch: str | None = None,
    archive_source: bool = False,
) -> dict[str, Any]:
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

    git_commit = _git(["rev-parse", "HEAD"], root)
    git_branch = _git(["rev-parse", "--abbrev-ref", "HEAD"], root)
    git_status = _git(["status", "--porcelain"], root)

    if source_commit is not None and not _COMMIT_RE.fullmatch(source_commit):
        raise ValueError("--source-commit must be a full 40-character Git commit SHA")
    if archive_source and source_commit is None:
        raise ValueError("--archive-source requires --source-commit")

    effective_commit = source_commit or git_commit
    effective_branch = source_branch or git_branch
    if archive_source:
        binding_method = "IMMUTABLE_GITHUB_COMMIT_ARCHIVE"
        working_tree_state = "NOT_APPLICABLE_ARCHIVE"
    else:
        binding_method = "LOCAL_GIT_CHECKOUT"
        working_tree_state = git_status

    return {
        "schema": "stegverse.evaluation-boundary-artifact-manifest.v1",
        "repository": "StegVerse-org/StegVerse-SDK",
        "source_commit": effective_commit,
        "source_branch": effective_branch,
        "source_binding_method": binding_method,
        "working_tree_porcelain": working_tree_state,
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
        "missing_expected_artifacts": missing,
        "authority_granted": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Hash evaluator-boundary artifacts and bind them to an exact Git source commit")
    parser.add_argument("--root", default=".", help="repository checkout or exact commit-archive root")
    parser.add_argument("--output", help="optional JSON output path")
    parser.add_argument("--source-commit", help="explicit full commit SHA for an immutable archive materialization")
    parser.add_argument("--source-branch", help="optional source branch label")
    parser.add_argument(
        "--archive-source",
        action="store_true",
        help="declare that root came from an immutable commit archive rather than a Git working tree",
    )
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    manifest = build_manifest(
        root,
        source_commit=args.source_commit,
        source_branch=args.source_branch,
        archive_source=args.archive_source,
    )
    rendered = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")

    if args.archive_source:
        clean_or_immutable = manifest["working_tree_porcelain"] == "NOT_APPLICABLE_ARCHIVE"
    else:
        clean_or_immutable = manifest["working_tree_porcelain"] == ""
    complete = not manifest["missing_expected_artifacts"]
    source_bound = bool(manifest["source_commit"])
    return 0 if clean_or_immutable and complete and source_bound else 2


if __name__ == "__main__":
    raise SystemExit(main())
