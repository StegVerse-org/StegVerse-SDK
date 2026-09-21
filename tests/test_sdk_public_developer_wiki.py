import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class SdkPublicDeveloperWikiTests(unittest.TestCase):
    def test_required_canonical_sources_exist(self):
        for rel in [
            "README.md",
            "SDK_MIRROR_HANDOFF.md",
            "docs/GENERIC_MANIFEST_PROCESSING_CONTRACT.md",
            "docs/MANIFEST_RECEIPT_NAVIGATION_MIRROR_HANDOFF.md",
            "schemas/stegverse.ingress-manifest.v1.schema.json",
            "inspection/examples/external-framework-generic-manifest.json",
        ]:
            self.assertTrue((ROOT / rel).is_file(), rel)

    def test_build_is_exact_source_bound_and_non_authorizing(self):
        subprocess.run([sys.executable, str(ROOT / "scripts/build_sdk_public_wiki.py")], check=True, cwd=ROOT)
        out = ROOT / "_site"
        self.assertEqual((out / "CNAME").read_text().strip(), "sdk.stegverse.org")
        manifest = json.loads((out / "wiki-source-manifest.json").read_text())
        self.assertEqual(manifest["goal_task_id"], "SDK-PUBLIC-DEVELOPER-WIKI-001")
        self.assertEqual(manifest["authority_effect"], "NONE_DOCUMENTATION_PROJECTION_ONLY")
        for row in manifest["sources"]:
            src = ROOT / row["path"]
            self.assertEqual(hashlib.sha256(src.read_bytes()).hexdigest(), row["sha256"])
            self.assertEqual((out / row["published_path"]).read_bytes(), src.read_bytes())

    def test_index_exposes_developer_contract_and_boundaries(self):
        subprocess.run([sys.executable, str(ROOT / "scripts/build_sdk_public_wiki.py")], check=True, cwd=ROOT)
        page = (ROOT / "_site/index.html").read_text()
        for required in [
            "stegverse.ingress-manifest.v1",
            "caller-selected processing capability",
            "manifest_receipt_id",
            "Replay",
            "External-framework example",
            "Interlock/InTr",
            "Master Records",
            "Publisher",
            "TV/TVC",
            "documentation projection",
        ]:
            self.assertIn(required, page)

if __name__ == "__main__":
    unittest.main()
