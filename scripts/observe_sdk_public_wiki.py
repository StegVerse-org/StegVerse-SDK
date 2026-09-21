#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

CASES = [
    {
        "id": "SDK_PUBLIC_SCHEMA_PAGE_OBSERVED",
        "url": "https://sdk.stegverse.org/source/schemas/stegverse.ingress-manifest.v1.schema.json",
        "markers": ['"title": "StegVerse ingress manifest v1"', '"manifest_profile"'],
    },
    {
        "id": "SDK_PUBLIC_EXAMPLE_PAGE_OBSERVED",
        "url": "https://sdk.stegverse.org/source/inspection/examples/external-framework-generic-manifest.json",
        "markers": ['"source_framework": "ELAN"', '"manifest_profile": "stegverse.ingress-manifest.v1"'],
    },
    {
        "id": "SDK_PUBLIC_RECEIPT_NAVIGATION_PAGE_OBSERVED",
        "url": "https://sdk.stegverse.org/source/docs/MANIFEST_RECEIPT_NAVIGATION_MIRROR_HANDOFF.md",
        "markers": ["Manifest Receipt Navigation Mirror Handoff", "manifest_receipt_id"],
    },
    {
        "id": "SITE_SDK_PUBLIC_WIKI_LINK_OBSERVED",
        "url": "https://stegverse.org/wikis.html",
        "markers": ["StegVerse SDK Developer Wiki", "https://sdk.stegverse.org/"],
    },
]

def fetch(case: dict[str, object]) -> dict[str, object]:
    req = urllib.request.Request(
        str(case["url"]),
        headers={
            "User-Agent": "StegVerse-SDK-Public-Wiki-Observer/1.0",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
    )
    result = {
        "id": case["id"],
        "url": case["url"],
        "http_status": None,
        "final_url": None,
        "content_type": None,
        "sha256": None,
        "bytes": 0,
        "markers": {},
        "passed": False,
        "error": None,
    }
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            body = response.read()
            result["http_status"] = int(response.status)
            result["final_url"] = response.geturl()
            result["content_type"] = response.headers.get("Content-Type")
    except urllib.error.HTTPError as exc:
        body = exc.read()
        result["http_status"] = int(exc.code)
        result["final_url"] = exc.geturl()
        result["content_type"] = exc.headers.get("Content-Type")
        result["error"] = f"HTTPError:{exc.code}"
    except Exception as exc:
        body = b""
        result["error"] = f"{type(exc).__name__}:{exc}"

    text = body.decode("utf-8", errors="replace")
    result["bytes"] = len(body)
    result["sha256"] = hashlib.sha256(body).hexdigest() if body else None
    marker_results = {m: (m in text) for m in case["markers"]}
    result["markers"] = marker_results
    result["passed"] = result["http_status"] == 200 and all(marker_results.values())
    return result

def main() -> int:
    results = [fetch(case) for case in CASES]
    report = {
        "schema": "stegverse.sdk-public-wiki-public-observation/v1",
        "goal_task_id": "SDK-PUBLIC-DEVELOPER-WIKI-001",
        "authority_effect": "NONE_OBSERVATION_ONLY",
        "results": results,
        "all_passed": all(row["passed"] for row in results),
    }
    out = Path("artifacts/sdk-public-wiki-observation.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["all_passed"] else 1

if __name__ == "__main__":
    sys.exit(main())
