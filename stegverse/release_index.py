from __future__ import annotations

import argparse
import json
import re
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

RELEASE_API = "https://api.github.com/repos/StegVerse-Labs/StegCore/releases?per_page=100"
TAG_PREFIX = "stegverse-portable-v"
SEMVER = r"[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?"
ASSET_RE = re.compile(
    rf"^stegverse-sdk-(s|ns)-micro-ecosystem-v({SEMVER})\.(zip|tar\.gz)$",
    re.IGNORECASE,
)


class ReleaseIndexError(ValueError):
    pass


def _version_key(version: str) -> tuple[int, ...] | tuple[str]:
    core = version.split("-", 1)[0].split("+", 1)[0]
    parts = core.split(".")
    if parts and all(part.isdigit() for part in parts):
        return tuple(int(part) for part in parts)
    return (version,)


def normalize_release(row: dict[str, Any]) -> dict[str, Any] | None:
    tag = str(row.get("tag_name") or "")
    if not tag.startswith(TAG_PREFIX):
        return None
    if row.get("draft") is True:
        return None
    version = tag[len(TAG_PREFIX):]
    if not re.fullmatch(SEMVER, version):
        return None

    assets: dict[str, dict[str, dict[str, Any]]] = {"S": {}, "NS": {}}
    package_versions: dict[str, str | None] = {"S": None, "NS": None}
    inconsistent_package_version = False
    for asset in row.get("assets") or []:
        if not isinstance(asset, dict):
            continue
        name = str(asset.get("name") or "")
        match = ASSET_RE.match(name)
        if not match:
            continue
        deployment_class = match.group(1).upper()
        package_version = match.group(2)
        archive_format = "tar.gz" if match.group(3).lower() == "tar.gz" else "zip"
        url = asset.get("browser_download_url")
        if not isinstance(url, str) or not url.startswith("https://github.com/StegVerse-Labs/StegCore/releases/download/"):
            continue
        prior = package_versions[deployment_class]
        if prior is not None and prior != package_version:
            inconsistent_package_version = True
        package_versions[deployment_class] = package_version
        assets[deployment_class][archive_format] = {
            "name": name,
            "url": url,
            "size": int(asset.get("size") or 0),
            "package_version": package_version,
        }

    complete = (
        not inconsistent_package_version
        and all(set(assets[key]) == {"zip", "tar.gz"} for key in ("S", "NS"))
        and all(package_versions[key] is not None for key in ("S", "NS"))
    )
    return {
        "version": version,
        "release_version": version,
        "tag": tag,
        "name": row.get("name") or tag,
        "published_at": row.get("published_at"),
        "prerelease": bool(row.get("prerelease")),
        "package_versions": package_versions,
        "assets": assets,
        "complete_dual_format_release": complete,
        "authority_effect": "NONE",
    }


def versions_from_rows(rows: list[Any]) -> list[dict[str, Any]]:
    releases: list[dict[str, Any]] = []
    for row in rows:
        if isinstance(row, dict):
            normalized = normalize_release(row)
            if normalized is not None:
                releases.append(normalized)
    releases.sort(key=lambda row: _version_key(row["release_version"]), reverse=True)
    return releases


def fetch_versions(*, timeout: int = 15) -> dict[str, Any]:
    request = Request(
        RELEASE_API,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "stegverse-sdk-release-index",
        },
    )
    try:
        with urlopen(request, timeout=timeout) as response:  # nosec B310 - fixed public GitHub API URL
            rows = json.loads(response.read().decode("utf-8"))
    except (OSError, HTTPError, URLError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return {
            "schema": "stegverse.sdk.release-index.v2",
            "state": "UNAVAILABLE_NON_AUTHORIZING",
            "repository": "StegVerse-Labs/StegCore",
            "versions": [],
            "error": type(exc).__name__,
            "authority_effect": "NONE",
        }
    if not isinstance(rows, list):
        raise ReleaseIndexError("invalid_github_release_index")
    versions = versions_from_rows(rows)
    return {
        "schema": "stegverse.sdk.release-index.v2",
        "state": "PASS",
        "repository": "StegVerse-Labs/StegCore",
        "versions": versions,
        "latest_complete_version": next((row["release_version"] for row in versions if row["complete_dual_format_release"]), None),
        "authority_effect": "NONE",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="stegverse-versions",
        description="Show versioned portable StegVerse releases and S/NS package component versions from the canonical public GitHub release index.",
    )
    parser.add_argument("--complete-only", action="store_true", help="show only releases containing version-consistent S and NS ZIP and TAR.GZ pairs")
    args = parser.parse_args(argv)
    try:
        result = fetch_versions()
    except ReleaseIndexError as exc:
        print(json.dumps({"state": "FAIL_CLOSED", "error": str(exc), "authority_effect": "NONE"}, indent=2, sort_keys=True))
        return 2
    if args.complete_only:
        result = dict(result)
        result["versions"] = [row for row in result["versions"] if row["complete_dual_format_release"]]
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["state"] in {"PASS", "UNAVAILABLE_NON_AUTHORIZING"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
