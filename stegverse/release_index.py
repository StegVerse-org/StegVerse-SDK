from __future__ import annotations

import json
import re
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

RELEASE_API = "https://api.github.com/repos/StegVerse-Labs/StegCore/releases?per_page=100"
TAG_PREFIX = "stegverse-portable-v"
ASSET_RE = re.compile(r"^stegverse-sdk-(s|ns)-micro-ecosystem-v[^/]+\.(zip|tar\.gz)$", re.IGNORECASE)


class ReleaseIndexError(ValueError):
    pass


def _version_key(version: str) -> tuple[int, ...] | tuple[str]:
    parts = version.split(".")
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
    if not version:
        return None

    assets: dict[str, dict[str, dict[str, Any]]] = {"S": {}, "NS": {}}
    for asset in row.get("assets") or []:
        if not isinstance(asset, dict):
            continue
        name = str(asset.get("name") or "")
        match = ASSET_RE.match(name)
        if not match:
            continue
        deployment_class = match.group(1).upper()
        archive_format = "tar.gz" if name.lower().endswith(".tar.gz") else "zip"
        url = asset.get("browser_download_url")
        if not isinstance(url, str) or not url.startswith("https://github.com/StegVerse-Labs/StegCore/releases/download/"):
            continue
        assets[deployment_class][archive_format] = {
            "name": name,
            "url": url,
            "size": int(asset.get("size") or 0),
        }

    complete = all(set(assets[key]) == {"zip", "tar.gz"} for key in ("S", "NS"))
    return {
        "version": version,
        "tag": tag,
        "name": row.get("name") or tag,
        "published_at": row.get("published_at"),
        "prerelease": bool(row.get("prerelease")),
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
    releases.sort(key=lambda row: _version_key(row["version"]), reverse=True)
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
            "schema": "stegverse.sdk.release-index.v1",
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
        "schema": "stegverse.sdk.release-index.v1",
        "state": "PASS",
        "repository": "StegVerse-Labs/StegCore",
        "versions": versions,
        "latest_complete_version": next((row["version"] for row in versions if row["complete_dual_format_release"]), None),
        "authority_effect": "NONE",
    }
