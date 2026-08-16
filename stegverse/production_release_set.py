"""Production release-set provenance for governed evaluator runs.

A release set is evidence, not authority. The immutable run snapshot records the
installed components that actually participated. A separate public catalog may
be refreshed later so replay/reconstruction can distinguish historical runtime
state from the ecosystem's current released state.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata as metadata
import json
import re
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

SCHEMA = "stegverse.production-release-set.v1"
CATALOG_SCHEMA = "stegverse.production-release-catalog.v1"
_HEX_SHA = re.compile(r"^[0-9a-fA-F]{7,64}$")

COMPONENTS = (
    {"role": "sdk_entry", "distribution": "stegverse-sdk", "repository": "StegVerse-org/StegVerse-SDK"},
    {"role": "governance_runtime", "distribution": "stegcore", "repository": "StegVerse-Labs/StegCore"},
    {"role": "manifest_route_carrier", "distribution": "stegverse-core-lite", "repository": "Data-Continuation/core-lite"},
    {"role": "exact_run_custody", "distribution": "stegverse-master-records", "repository": "master-records/orchestration"},
)


def _canonical_hash(value: Any) -> str:
    body = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(body).hexdigest()


def _direct_url(dist: metadata.Distribution) -> dict[str, Any]:
    try:
        text = dist.read_text("direct_url.json")
        value = json.loads(text) if text else {}
        return value if isinstance(value, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _release_tag_from_revision(revision: Any, commit_sha: Any) -> str | None:
    if not isinstance(revision, str) or not revision.strip():
        return None
    value = revision.strip()
    if value == commit_sha or _HEX_SHA.fullmatch(value):
        return None
    return value


def _installed_component(spec: dict[str, str]) -> dict[str, Any]:
    name = spec["distribution"]
    repo = spec["repository"]
    row: dict[str, Any] = {
        "role": spec["role"],
        "distribution": name,
        "repository": repo,
        "release_index_url": f"https://github.com/{repo}/releases",
        "authority_effect": "NONE",
    }
    try:
        dist = metadata.distribution(name)
    except metadata.PackageNotFoundError:
        row.update({
            "installed": False,
            "version": None,
            "commit_sha": None,
            "requested_revision": None,
            "release_tag": None,
            "release_binding_status": "NOT_INSTALLED",
            "release_url": None,
            "changelog_url": None,
            "source_url": None,
        })
        return row
    direct = _direct_url(dist)
    vcs = direct.get("vcs_info") if isinstance(direct.get("vcs_info"), dict) else {}
    commit_sha = vcs.get("commit_id")
    revision = vcs.get("requested_revision")
    release_tag = _release_tag_from_revision(revision, commit_sha)
    release_url = f"https://github.com/{repo}/releases/tag/{quote(release_tag, safe='')}" if release_tag else None
    row.update({
        "installed": True,
        "version": dist.version,
        "commit_sha": commit_sha,
        "requested_revision": revision,
        "release_tag": release_tag,
        "release_binding_status": "RELEASE_TAG_BOUND" if release_tag else "COMMIT_OR_PACKAGE_ONLY",
        "release_url": release_url,
        "changelog_url": release_url,
        "source_url": direct.get("url"),
    })
    return row


def installed_release_set() -> dict[str, Any]:
    """Return the exact installed production component set for run retention."""
    components = [_installed_component(dict(spec)) for spec in COMPONENTS]
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "components": components,
        "all_components_installed": all(row["installed"] for row in components),
        "all_components_commit_bound": all(bool(row.get("commit_sha")) for row in components),
        "all_components_release_tag_bound": all(row.get("release_binding_status") == "RELEASE_TAG_BOUND" for row in components),
        "historical_snapshot": True,
        "mutable_by_future_release": False,
        "authority_effect": "NONE",
    }
    payload["release_set_hash"] = _canonical_hash(payload)
    return payload


def _fetch_json(url: str, timeout: int) -> Any:
    req = Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "stegverse-sdk-production-release-catalog"})
    with urlopen(req, timeout=timeout) as response:  # nosec B310 - fixed public GitHub API roots
        return json.loads(response.read().decode("utf-8"))


def public_release_catalog(*, timeout: int = 15) -> dict[str, Any]:
    """Return current public releases and release changelogs for every production component."""
    rows: list[dict[str, Any]] = []
    for spec in COMPONENTS:
        repo = spec["repository"]
        api = f"https://api.github.com/repos/{repo}/releases?per_page=100"
        try:
            releases = _fetch_json(api, timeout)
            if not isinstance(releases, list):
                raise ValueError("invalid release response")
            normalized = [
                {
                    "tag": item.get("tag_name"),
                    "name": item.get("name") or item.get("tag_name"),
                    "published_at": item.get("published_at"),
                    "prerelease": bool(item.get("prerelease")),
                    "release_url": item.get("html_url"),
                    "changelog": item.get("body") or "",
                }
                for item in releases
                if isinstance(item, dict) and item.get("draft") is not True
            ]
            rows.append({
                "role": spec["role"],
                "distribution": spec["distribution"],
                "repository": repo,
                "state": "PASS",
                "latest_release": normalized[0] if normalized else None,
                "release_count": len(normalized),
                "releases": normalized,
            })
        except (OSError, HTTPError, URLError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
            rows.append({
                "role": spec["role"],
                "distribution": spec["distribution"],
                "repository": repo,
                "state": "UNAVAILABLE_NON_AUTHORIZING",
                "error": type(exc).__name__,
                "latest_release": None,
                "release_count": 0,
                "releases": [],
            })
    payload: dict[str, Any] = {
        "schema": CATALOG_SCHEMA,
        "components": rows,
        "all_components_have_release": all(row.get("latest_release") for row in rows),
        "authority_effect": "NONE",
    }
    payload["catalog_hash"] = _canonical_hash(payload)
    return payload


def compare_release_sets(original: dict[str, Any] | None, current: dict[str, Any]) -> dict[str, Any]:
    original_hash = original.get("release_set_hash") if isinstance(original, dict) else None
    return {
        "original_release_set_hash": original_hash,
        "current_release_set_hash": current.get("release_set_hash"),
        "same_installed_release_set": bool(original_hash) and original_hash == current.get("release_set_hash"),
        "release_set_changed_since_original_run": bool(original_hash) and original_hash != current.get("release_set_hash"),
        "historical_record_mutated": False,
        "authority_effect": "NONE",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="stegverse production-releases", description="Inspect the installed production release set or current public release catalog")
    parser.add_argument("mode", nargs="?", choices=("installed", "catalog"), default="catalog")
    parser.add_argument("--output", help="optional JSON output path")
    args = parser.parse_args(argv)
    payload = installed_release_set() if args.mode == "installed" else public_release_catalog()
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
