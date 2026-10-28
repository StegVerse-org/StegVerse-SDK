"""CM-GOV-1: reproduce governance-gate behavior at pinned SDK commits.

For each pinned ref this installs the gate exactly as the reusable workflow
does (the ``stegverse/`` tree of that commit, checked out beside the caller),
then runs both the checker and the workflow's own ``run:`` step against the
same caller trees:

- ``empty``: no governance bundle matches the glob;
- ``valid``: one bundle that recomputes;
- ``tampered``: the same bundle with a mutated receipt;
- ``not_object``: a bundle file whose JSON root is a list.

The checker runs with ``python3 -I -S``: no site-packages, so the run proves
the gate needs no installed dependency. Install and rollback are checked by
hashing the workspace before install and after removing the install and the
report; the caller tree must never change. The output is deterministic (no
temp paths, no timestamps), so two runs on the same refs produce the same
bytes.

Standard library only. Needs a git checkout that holds the pinned commits.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path
from typing import Sequence

REPORT_SCHEMA = "stegverse.governance-gate-pin-reproduction.v1"
SIX_FIELDS = ("failure_code", "failed_predicate", "required_evidence_or_repair",
              "retry_entrypoint", "owning_existing_goal", "next_attempt")
# Third ref: the SDK#534 commit whose workflow defaults sdk_ref to job.workflow_sha. It is an ancestor of
# the commit holding this file, so recording it here is not self-referential.
DEFAULT_REFS = ("ba5bbf42eabec6a6ae3b0efdff7c683967a79083", "3dd6c80b54828821f83834e76a90b62ccd0237f0",
                "4c9dfac7b31c5dcd30a8bc9b13e6d11353a51328")
SELF_REF_DEFAULT = "job.workflow_sha"
GATE_PATH = "stegverse/governance_gate.py"
WORKFLOW_PATH = ".github/workflows/governance-gate.yml"
REPORT_NAME = "stegverse-governance-report.json"
ROOT = Path(__file__).resolve().parents[1]
VALID_BUNDLE = ROOT / "tests" / "fixtures" / "governance-gate-pin" / "valid-bundle.json"


def _git(repo: Path, *args: str) -> bytes:
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True).stdout


def _install(repo: Path, ref: str | None, workspace: Path) -> None:
    """Materialize <ref>:stegverse into workspace/.stegverse-sdk (the workflow's sparse checkout).

    ``ref=None`` installs the working tree's ``stegverse/`` instead, for checkouts without history.
    """
    target = workspace / ".stegverse-sdk"
    if ref is None:
        shutil.copytree(repo / "stegverse", target / "stegverse", ignore=shutil.ignore_patterns("__pycache__"))
        return
    archive = _git(repo, "archive", "--format=tar", ref, "stegverse")
    target.mkdir()
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        tar.extractall(target, filter="data")


def git_blob_sha(data: bytes) -> str:
    """The git blob id of ``data``, computed without git."""
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def reproduce_tree(root: Path = ROOT, valid_bundle: Path = VALID_BUNDLE) -> dict:
    """Run the scenarios against the working tree's gate and workflow (no git history needed)."""
    valid = json.loads(valid_bundle.read_text(encoding="utf-8"))
    workflow = (root / WORKFLOW_PATH).read_bytes()
    scenarios, install = _scenarios(root, None, run_step_script(workflow.decode()), valid)
    return {"gate_blob": git_blob_sha((root / GATE_PATH).read_bytes()), "workflow_blob": git_blob_sha(workflow),
            "scenarios": scenarios, "install_rollback": install}


def run_step_script(workflow_text: str) -> str:
    """Return the body of the ``id: run`` step's ``run: |`` block, dedented."""
    lines = workflow_text.splitlines()
    for index, line in enumerate(lines):
        if re.match(r"\s*-\s+id:\s*run\s*$", line):
            break
    else:
        raise ValueError("workflow has no step with id: run")
    for start in range(index + 1, len(lines)):
        if re.match(r"\s*run:\s*\|\s*$", lines[start]):
            break
    else:
        raise ValueError("run step has no block scalar")
    body = []
    indent = None
    for line in lines[start + 1:]:
        if line.strip() == "":
            body.append("")
            continue
        current = len(line) - len(line.lstrip())
        if indent is None:
            indent = current
        if current < indent:
            break
        body.append(line[indent:])
    return "\n".join(body).rstrip() + "\n"


def _tree_digest(path: Path) -> str:
    digest = hashlib.sha256()
    for item in sorted(p for p in path.rglob("*") if p.is_file()):
        digest.update(item.relative_to(path).as_posix().encode() + b"\0" + item.read_bytes() + b"\0")
    return digest.hexdigest()


def _callers(valid: dict) -> dict[str, dict[str, object]]:
    tampered = copy.deepcopy(valid)
    tampered["spe_receipt"]["reasons"] = ["mutated after receipt"]
    return {
        "empty": {},
        "valid": {".stegverse/governance/bundle.json": valid},
        "tampered": {".stegverse/governance/bundle.json": tampered},
        "not_object": {".stegverse/governance/bundle.json": [valid]},
    }


def _write_caller(root: Path, files: dict[str, object]) -> None:
    root.mkdir()
    (root / "README.md").write_text("caller repository\n", encoding="utf-8")
    for rel, document in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _summarize(report_path: Path) -> dict:
    if not report_path.exists():
        return {"report_present": False}
    report = json.loads(report_path.read_text(encoding="utf-8"))
    return {
        "report_present": True,
        "observed_disposition": report.get("disposition"),
        "reason": report.get("reason"),
        "bundle_statuses": [bundle.get("status") for bundle in report.get("bundles", [])],
        "six_fields_present": [field for field in SIX_FIELDS if report.get(field)],
        "authority_all_false": not any(v for k, v in report.get("authority", {}).items()
                                       if k != "verification_authority")
        and report.get("authority", {}).get("verification_authority") == "NONE",
        "report_sha256": hashlib.sha256(report_path.read_bytes()).hexdigest(),
    }


def _run_checker(workspace: Path) -> dict:
    report = workspace / REPORT_NAME
    proc = subprocess.run([sys.executable, "-I", "-S", ".stegverse-sdk/stegverse/governance_gate.py", "caller",
                           "--output", REPORT_NAME], cwd=workspace, capture_output=True, text=True)
    result = {"exit_status": proc.returncode, **_summarize(report)}
    report.unlink(missing_ok=True)
    return result


def _run_workflow_step(workspace: Path, script: str) -> dict:
    output = workspace / "github_output"
    summary = workspace / "step_summary"
    env = {"PATH": f"{Path(sys.executable).parent}{os.pathsep}{os.environ.get('PATH', '')}",
           "HOME": str(workspace), "BUNDLE_GLOB": ".stegverse/governance/**/*.json", "CHECK_SCHEMAS": "true",
           "GITHUB_OUTPUT": str(output), "GITHUB_STEP_SUMMARY": str(summary)}
    proc = subprocess.run(["bash", "-e", "-c", script], cwd=workspace, env=env, capture_output=True, text=True)
    outputs = dict(line.split("=", 1) for line in output.read_text(encoding="utf-8").splitlines() if "=" in line) \
        if output.exists() else {}
    for path in (output, summary, workspace / REPORT_NAME):
        path.unlink(missing_ok=True)
    return {"job_exit_status": proc.returncode, "disposition_output": outputs.get("disposition")}


def _scenarios(repo: Path, checker_commit: str | None, script: str, valid: dict) -> tuple[dict, dict]:
    scenarios = {}
    install = {}
    for name, files in _callers(valid).items():
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            _write_caller(workspace / "caller", files)
            before = _tree_digest(workspace)
            caller_before = _tree_digest(workspace / "caller")
            _install(repo, checker_commit, workspace)
            checker = _run_checker(workspace)
            step = _run_workflow_step(workspace, script)
            caller_unchanged = _tree_digest(workspace / "caller") == caller_before
            shutil.rmtree(workspace / ".stegverse-sdk")
            restored = _tree_digest(workspace) == before
        scenarios[name] = {"checker": checker, "workflow_step": step}
        install[name] = {"caller_tree_unchanged": caller_unchanged, "rollback_restores_workspace": restored}
    return scenarios, install


def reproduce_ref(repo: Path, ref: str, valid: dict) -> dict:
    commit = _git(repo, "rev-parse", f"{ref}^{{commit}}").decode().strip()
    workflow = _git(repo, "show", f"{commit}:{WORKFLOW_PATH}").decode()
    script = run_step_script(workflow)
    sdk_ref_default = re.search(r"sdk_ref:.*?default:\s*(\S+)", workflow, re.S)
    sdk_ref_default = sdk_ref_default.group(1) if sdk_ref_default else None
    if sdk_ref_default in ("''", '""') and "${{ job.workflow_sha }}" in workflow:
        # Empty default resolves to the commit the workflow was called at: the checker of this same commit.
        sdk_ref_default = SELF_REF_DEFAULT
    actions = sorted(set(re.findall(r"uses:\s*(actions/[\w-]+@\S+)", workflow)))
    scenarios, install = _scenarios(repo, commit, script, valid)
    # What a caller gets when it pins this workflow and keeps the default sdk_ref: the run step of this
    # commit driving the checker of the default commit. Only reproducible for a pinned (40-hex) default.
    default_combination = None
    if sdk_ref_default and re.fullmatch(r"[0-9a-f]{40}", sdk_ref_default) and sdk_ref_default != commit:
        combined, _ = _scenarios(repo, sdk_ref_default, script, valid)
        default_combination = {name: s["workflow_step"] for name, s in combined.items()}
    elif sdk_ref_default == SELF_REF_DEFAULT:
        default_combination = {name: s["workflow_step"] for name, s in scenarios.items()}
    return {
        "ref": commit,
        "gate_blob": _git(repo, "rev-parse", f"{commit}:{GATE_PATH}").decode().strip(),
        "workflow_blob": _git(repo, "rev-parse", f"{commit}:{WORKFLOW_PATH}").decode().strip(),
        "workflow_sdk_ref_default": sdk_ref_default,
        "workflow_with_default_sdk_ref": default_combination,
        "workflow_actions": actions,
        "actions_pinned_by_sha": all(re.fullmatch(r"actions/[\w-]+@[0-9a-f]{40}", a) for a in actions),
        "dispositions_observed": sorted({s["checker"].get("observed_disposition") for s in scenarios.values()} - {None}),
        "scenarios": scenarios,
        "install_rollback": install,
    }


def reproduce(repo: Path, refs: Sequence[str], valid_bundle: Path = VALID_BUNDLE) -> dict:
    valid = json.loads(valid_bundle.read_text(encoding="utf-8"))
    results = [reproduce_ref(repo, ref, valid) for ref in refs]
    # Rollback of the pin itself: re-run the first ref after the others; its results must be identical.
    rollback = reproduce_ref(repo, refs[0], valid) if len(refs) > 1 else results[0]
    return {
        "schema": REPORT_SCHEMA,
        "valid_bundle_sha256": hashlib.sha256(valid_bundle.read_bytes()).hexdigest(),
        "refs": results,
        "pin_rollback_reproduces_first_ref": rollback == results[0],
        "authority": {"verification_authority": "NONE", "execution_authorized": False,
                      "evidence_class": "LOCAL_DETERMINISTIC_REPRODUCTION"},
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", default=str(ROOT), help="Git checkout holding the pinned commits")
    parser.add_argument("--ref", action="append", help="Pinned SDK commit (repeatable; first is the rollback target)")
    parser.add_argument("--output", help="Write the JSON result here (default: stdout)")
    args = parser.parse_args(argv)
    result = reproduce(Path(args.repo), tuple(args.ref or DEFAULT_REFS))
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
