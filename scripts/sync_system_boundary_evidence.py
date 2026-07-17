#!/usr/bin/env python3
"""Synchronize system-boundary workflow evidence without manual observation.

The synchronizer polls completed GitHub Actions runs for the adapter and SDK,
selects only successful runs whose head commit contains the required workflow
binding commit, writes exact run-bound evidence, evaluates joint activation, and
writes the bounded downstream status packet.

It never enables production binding, authorizes release, transfers custody,
grants execution authority, or determines admissibility.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Iterable, Mapping

from stegverse.system_boundary_activation import evaluate_system_boundary_activation
from stegverse.system_boundary_downstream_status import build_downstream_status_packet

ROOT = Path(__file__).resolve().parents[1]
API = "https://api.github.com"

SOURCES = {
    "adapter": {
        "repository": "StegVerse-org/LLM-adapter",
        "workflow": "validate.yml",
        "workflow_path": ".github/workflows/validate.yml",
        "required_commit": "cf5bbe3b9b343600d27c249a02a40fe96c37e61e",
        "output": ROOT / "evidence/system-boundary-workflow-evidence.adapter.v0.1.json",
    },
    "sdk": {
        "repository": "StegVerse-org/StegVerse-SDK",
        "workflow": "validate.yml",
        "workflow_path": ".github/workflows/validate.yml",
        "required_commit": "3f282a30595d8b2e486415ac86824ba9d5c81cfa",
        "output": ROOT / "evidence/system-boundary-workflow-evidence.sdk.v0.1.json",
    },
}

ACTIVATION_OUTPUT = ROOT / "evidence/system-boundary-activation.v0.1.json"
DOWNSTREAM_OUTPUT = ROOT / "evidence/system-boundary-downstream-status.v0.1.json"


def _request_json(path: str, token: str | None = None) -> Any:
    request = urllib.request.Request(f"{API}{path}")
    request.add_header("Accept", "application/vnd.github+json")
    request.add_header("X-GitHub-Api-Version", "2022-11-28")
    request.add_header("User-Agent", "StegVerse-system-boundary-sync")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def commit_contains_required(
    repository: str,
    required_commit: str,
    observed_commit: str,
    token: str | None = None,
) -> bool:
    if observed_commit == required_commit:
        return True
    base = urllib.parse.quote(required_commit, safe="")
    head = urllib.parse.quote(observed_commit, safe="")
    comparison = _request_json(f"/repos/{repository}/compare/{base}...{head}", token)
    return comparison.get("status") in {"ahead", "identical"}


def select_qualifying_run(
    runs: Iterable[Mapping[str, Any]],
    *,
    repository: str,
    required_commit: str,
    token: str | None = None,
    contains=commit_contains_required,
) -> Mapping[str, Any] | None:
    for run in runs:
        if run.get("status") != "completed" or run.get("conclusion") != "success":
            continue
        if run.get("event") not in {"push", "workflow_dispatch", "pull_request"}:
            continue
        observed_commit = run.get("head_sha")
        if not isinstance(observed_commit, str) or not observed_commit:
            continue
        if contains(repository, required_commit, observed_commit, token):
            return run
    return None


def build_evidence(source: Mapping[str, Any], run: Mapping[str, Any] | None) -> dict[str, Any]:
    evidence = {
        "schema_version": "stegverse.system_boundary.workflow_evidence.v0.1",
        "repository": source["repository"],
        "workflow": source["workflow_path"],
        "required_commit": source["required_commit"],
        "observed_commit": None,
        "run_id": None,
        "run_url": None,
        "result": "PENDING",
        "production_binding_enabled": False,
        "release_authorized": False,
    }
    if run is not None:
        observed_commit = run["head_sha"]
        evidence.update(
            {
                "required_commit": observed_commit,
                "observed_commit": observed_commit,
                "run_id": str(run["id"]),
                "run_url": run["html_url"],
                "result": "PASS",
            }
        )
    return evidence


def fetch_source_evidence(source: Mapping[str, Any], token: str | None) -> dict[str, Any]:
    workflow = urllib.parse.quote(source["workflow"], safe="")
    payload = _request_json(
        f"/repos/{source['repository']}/actions/workflows/{workflow}/runs?status=completed&per_page=50",
        token,
    )
    run = select_qualifying_run(
        payload.get("workflow_runs", []),
        repository=source["repository"],
        required_commit=source["required_commit"],
        token=token,
    )
    return build_evidence(source, run)


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if path.exists() and path.read_text(encoding="utf-8") == rendered:
        return
    path.write_text(rendered, encoding="utf-8")


def synchronize(token: str | None = None) -> dict[str, Any]:
    evidence: dict[str, dict[str, Any]] = {}
    for name, source in SOURCES.items():
        try:
            evidence[name] = fetch_source_evidence(source, token)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError) as exc:
            print(f"warning: {name} evidence remains PENDING: {exc}", file=sys.stderr)
            evidence[name] = build_evidence(source, None)
        write_json(source["output"], evidence[name])

    activation = evaluate_system_boundary_activation(evidence["adapter"], evidence["sdk"])
    activation_payload = {
        "schema_version": "stegverse.system_boundary.activation.v0.1",
        "state": activation.state,
        "verified": activation.verified,
        "adapter_evidence": str(SOURCES["adapter"]["output"].relative_to(ROOT)),
        "sdk_evidence": str(SOURCES["sdk"]["output"].relative_to(ROOT)),
        "downstream_propagation_allowed": activation.verified and activation.state == "VERIFIED",
        "production_binding_enabled": False,
        "release_authorized": False,
        "errors": list(activation.errors),
    }
    write_json(ACTIVATION_OUTPUT, activation_payload)

    downstream = build_downstream_status_packet(evidence["adapter"], evidence["sdk"])
    downstream_payload = downstream.packet if downstream.accepted else {
        "schema_version": "stegverse.system_boundary.downstream_status.v0.1",
        "activation_state": "INVALID_EVIDENCE",
        "verified": False,
        "downstream_propagation_allowed": False,
        "targets": [],
        "status_only": True,
        "production_binding_enabled": False,
        "release_authorized": False,
        "execution_authority_granted": False,
        "custody_transferred": False,
        "admissibility_determined": False,
        "errors": list(downstream.errors),
    }
    write_json(DOWNSTREAM_OUTPUT, downstream_payload)
    return {"evidence": evidence, "activation": activation_payload, "downstream": downstream_payload}


if __name__ == "__main__":
    result = synchronize(os.environ.get("GITHUB_TOKEN"))
    print(json.dumps(result, indent=2, sort_keys=True))
