#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import html
import json
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_site"

SOURCES = [
    Path("README.md"),
    Path("SDK_MIRROR_HANDOFF.md"),
    Path("docs/GENERIC_MANIFEST_PROCESSING_CONTRACT.md"),
    Path("docs/MANIFEST_RECEIPT_NAVIGATION_MIRROR_HANDOFF.md"),
    Path("schemas/stegverse.ingress-manifest.v1.schema.json"),
    Path("inspection/examples/external-framework-generic-manifest.json"),
]

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def source_revision() -> str:
    env_sha = os.environ.get("GITHUB_SHA", "").strip()
    if env_sha:
        return env_sha
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except Exception:
        return "UNAVAILABLE"

def copy_sources() -> list[dict[str, str]]:
    records = []
    for rel in SOURCES:
        src = ROOT / rel
        if not src.is_file():
            raise FileNotFoundError(rel)
        dst = OUT / "source" / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        records.append({
            "path": rel.as_posix(),
            "published_path": ("source/" + rel.as_posix()),
            "sha256": sha256(src),
        })
    return records

def build_index(revision: str) -> None:
    title = "StegVerse SDK Developer Wiki"
    body = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<style>
:root{{color-scheme:light dark}} body{{font-family:system-ui,-apple-system,sans-serif;max-width:1080px;margin:0 auto;padding:32px 20px;line-height:1.55}}
code,pre{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace}} pre{{padding:16px;overflow:auto;border:1px solid #8885;border-radius:10px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px}} .card{{border:1px solid #8885;border-radius:12px;padding:16px}}
a{{text-underline-offset:3px}} .muted{{opacity:.75}} .boundary{{border-left:4px solid currentColor;padding-left:14px}}
</style>
</head>
<body>
<h1>{html.escape(title)}</h1>
<p>Developer-facing documentation for the canonical <code>StegVerse-org/StegVerse-SDK</code> programmatic intake, testing, integration, evidence, replay, and reconstruction boundary.</p>
<p class="muted">Published from SDK source revision <code>{html.escape(revision)}</code>. This site is a documentation projection, not an authority surface.</p>

<h2>Core flow</h2>
<pre>source-native manifested data
-&gt; stegverse.ingress-manifest.v1
-&gt; caller-selected processing capability
-&gt; declared installed runtime route
-&gt; processor-specific evaluation
-&gt; canonical Master Records custody
-&gt; caller-selected return projection
-&gt; returned artifact + manifest_receipt_id
-&gt; replay / reconstruction where applicable</pre>

<h2>Developer paths</h2>
<div class="grid">
<div class="card"><h3>Manifest ingress</h3><p>Submit source-native manifested data through the generic ingress envelope.</p><a href="source/docs/GENERIC_MANIFEST_PROCESSING_CONTRACT.md">Processing contract</a><br><a href="source/schemas/stegverse.ingress-manifest.v1.schema.json">Ingress schema</a></div>
<div class="card"><h3>Examples and demos</h3><p>Start from a framework-neutral external manifest and the SDK builder/CLI guidance.</p><a href="source/inspection/examples/external-framework-generic-manifest.json">External-framework example</a><br><a href="source/README.md">SDK README / CLI examples</a></div>
<div class="card"><h3>Receipts</h3><p>Navigate <code>manifest_receipt_id</code>, governed result lineage, replay, and reconstruction.</p><a href="source/docs/MANIFEST_RECEIPT_NAVIGATION_MIRROR_HANDOFF.md">Receipt navigation</a></div>
<div class="card"><h3>Current implementation state</h3><p>Distinguish merged source, semantic validation, authentic governed runtime evidence, and release status.</p><a href="source/SDK_MIRROR_HANDOFF.md">SDK mirror handoff</a></div>
</div>

<h2>Selection is not authority</h2>
<div class="boundary">
<p><code>payload class != processing capability</code><br>
<code>processing capability != runtime route</code><br>
<code>processing selection != authority</code><br>
<code>route selection != authority</code><br>
<code>caller projection != canonical custody</code></p>
</div>

<h2>Authority boundaries</h2>
<p>The SDK validates/manifests intake and returns evidence. Interlock/InTr owns governed ingress/egress transition seams where required. Master Records is canonical custody/reconstruction authority. Publisher may materialize an approved presentation/publication projection but does not become governance authority. TV/TVC remains credential authority where credentials are required. This wiki grants none of those authorities.</p>

<h2>Machine-readable provenance</h2>
<p><a href="wiki-source-manifest.json">Wiki source manifest</a> records the exact published source revision and SHA-256 digest for each copied canonical source file.</p>
</body>
</html>
"""
    (OUT / "index.html").write_text(body, encoding="utf-8")

def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    (OUT / "CNAME").write_text("sdk.stegverse.org\n", encoding="utf-8")
    revision = source_revision()
    records = copy_sources()
    manifest = {
        "schema": "stegverse.sdk-public-developer-wiki-source-manifest/v1",
        "goal_task_id": "SDK-PUBLIC-DEVELOPER-WIKI-001",
        "public_origin": "https://sdk.stegverse.org/",
        "source_repository": "StegVerse-org/StegVerse-SDK",
        "source_revision": revision,
        "authority_effect": "NONE_DOCUMENTATION_PROJECTION_ONLY",
        "sources": records,
    }
    (OUT / "wiki-source-manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    build_index(revision)

if __name__ == "__main__":
    main()
