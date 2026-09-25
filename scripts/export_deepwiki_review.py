#!/usr/bin/env python3
"""Read-only public DeepWiki MCP evidence export. No publication or source mutation."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import urllib.error
import urllib.request

ENDPOINT = "https://mcp.deepwiki.com/mcp"
REPOSITORY = "StegVerse-org/StegVerse-SDK"
MAX_RESPONSE_BYTES = 12_000_000


def extract_jsonrpc(raw: bytes, content_type: str) -> dict:
    """Accept MCP's application/json or SSE-formatted JSON-RPC response."""
    if len(raw) > MAX_RESPONSE_BYTES:
        raise ValueError("Oversize DeepWiki response")
    data = raw.decode("utf-8")
    if "text/event-stream" in content_type or data.lstrip().startswith("event:"):
        events = [line[5:].strip() for line in data.splitlines() if line.startswith("data:")]
        candidates = [json.loads(item) for item in events if item and item != "[DONE]"]
        if not candidates:
            raise ValueError("No JSON-RPC SSE data events")
        body = next((item for item in candidates if "result" in item or "error" in item), candidates[-1])
    else:
        body = json.loads(data)
    if not isinstance(body, dict) or "error" in body or "result" not in body:
        raise ValueError("DeepWiki MCP error or missing result: " + str(body)[:250])
    if body["result"].get("isError") is True:
        raise ValueError("DeepWiki tool returned isError")
    return body


def rpc_call(name: str, request_id: int, timeout: float = 50.0) -> dict:
    payload = json.dumps({
        "jsonrpc": "2.0", "id": request_id, "method": "tools/call",
        "params": {"name": name, "arguments": {"repoName": REPOSITORY}},
    }).encode()
    request = urllib.request.Request(
        ENDPOINT, data=payload, method="POST",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "MCP-Protocol-Version": "2025-03-26",
            "User-Agent": "StegVerse-SDK-read-only-documentation-review/1",
        })
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read(MAX_RESPONSE_BYTES + 1)
        return extract_jsonrpc(raw, response.headers.get("Content-Type", ""))


def response_text(body: dict) -> str:
    result = body["result"]
    content = result.get("content", [])
    segments = [c.get("text", "") for c in content if isinstance(c, dict) and c.get("type") == "text"]
    return "\n\n".join(segments).strip()


def compare_page_coverage(structure: str, contents: str) -> int:
    """Require the full-content headings to match every advertised page exactly."""
    import collections
    import re
    advertised = re.findall(r"^\s*-\s+\d+(?:\.\d+)*\s+(.+?)\s*$", structure, re.MULTILINE)
    observed = re.findall(r"^# Page:\s*(.+?)\s*$", contents, re.MULTILINE)
    if not advertised or collections.Counter(advertised) != collections.Counter(observed):
        raise ValueError("DeepWiki structure/content coverage mismatch")
    if len(advertised) != len(set(advertised)):
        raise ValueError("Duplicate DeepWiki page titles")
    return len(advertised)


def export(out: Path) -> dict:
    # Structure and complete-content tools are both independently requested.
    # Neither is treated as publication approval or exact-source verification.
    results = {}
    for i, name in enumerate(("read_wiki_structure", "read_wiki_contents"), 1):
        body = rpc_call(name, i)
        text = response_text(body)
        if not text or len(text) < 30:
            raise ValueError("Incomplete/empty result from " + name)
        results[name] = {"raw_result": body["result"], "text": text}

    page_count = compare_page_coverage(results["read_wiki_structure"]["text"], results["read_wiki_contents"]["text"])

    # Do not infer upstream completeness beyond the returned page tree. The
    # review artifact intentionally retains the full raw MCP tool responses.
    out.mkdir(parents=True, exist_ok=True)
    records = []
    for name, entry in results.items():
        for suffix, data in (("json", json.dumps(entry["raw_result"], indent=2, ensure_ascii=False) + "\n"),
                             ("md", entry["text"] + "\n")):
            path = out / (name + "." + suffix)
            path.write_text(data, encoding="utf-8")
            records.append({"path": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                            "bytes": path.stat().st_size})
    manifest = {
        "schema": "stegverse.deepwiki-review-export/v1",
        "repository": REPOSITORY,
        "endpoint": ENDPOINT,
        "content_status": "UNREVIEWED_EXTERNAL_GENERATION",
        "captured_page_count": page_count,
        "coverage": "ALL_RETURNED_STRUCTURE_TITLES_MATCH_FULL_CONTENT_SECTIONS",
        "publication_allowed": False,
        "authority_effect": "NONE_REVIEW_ONLY",
        "completeness": "STRUCTURE_AND_CONTENT_TOOL_RESPONSES_CAPTURED_NOT_INDEPENDENTLY_PROVEN",
        "files": records,
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="deepwiki-review-export")
    args = parser.parse_args()
    manifest = export(Path(args.out))
    print(json.dumps({"exported": True, "files": len(manifest["files"]),
                      "authority_effect": manifest["authority_effect"]}))


if __name__ == "__main__":
    main()
