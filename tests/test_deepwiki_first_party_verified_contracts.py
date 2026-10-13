"""Verify new first-party corrections against exact pinned SDK source only.

The document links are frozen at revision PIN and are never rewritten. EXACT
instead pins each reviewed literal to the line it occupies in the *current*
working tree, so a merged change that moves or removes a literal is noticed
here rather than silently absorbed. When a pin is moved it keeps its literal;
the comment on the entry records the merged pull request that moved it and the
line it held at PIN.
"""
import re
import unittest
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
DOCUMENT = ROOT / "docs/deepwiki-review/FIRST_PARTY_VERIFIED_CONTRACTS.md"
PIN = "f5d9fdcc089bc8becdbc23a6107dab978dc15f56"
LINK = re.compile(
    r"https://github.com/StegVerse-org/StegVerse-SDK/blob/([0-9a-f]{40})/"
    r"([^\s)]+?)#L(\d+)(?:-L(\d+))?"
)
EXACT = {
    ("stegverse/manifest_contract.py", 51): "if route_id != CANONICAL_PRODUCTION_ROUTE_ID:",
    ("stegverse/manifest_contract.py", 71): "if declared_route_id != route_id:",
    # L211 at PIN. Moved by later route/profile publications, most recently
    # SDK#368 PR #446 (readiness qualification helpers, 267->269) and PR #447
    # (Ecosystem Chat / VA-scoped chat / HIL intake routes, 269->285).
    ("stegverse/manifest_builder.py", 288): "def build_manifest(",  # 285->288 with #512-#519
    ("stegverse/purpose_bound_worker_processor.py", 63): "partition reconstruction mismatch",
    ("stegverse/universal_entry_dispatch.py", 49): '"completed", "degraded", "unavailable", "failed_closed"',  # 48->49 with #512-#519
    ("stegverse/security_posture_request.py", 9): '"SECURE", "HIGH", "HIGHEST"',
    ("stegverse/security_posture_request.py", 40): 'NONE_REQUEST_INPUT_ONLY',
    ("stegverse/stage1_org_receipt_review.py", 5): "NEVER authenticates caller-supplied snapshots",
    ("stegverse/governance_reference_graph.py", 26): '"composition_grants_authority": False',
    # L15 and L33 at PIN. The 405 / 202-or-422 handling is unchanged; the
    # lines moved when PR #398 added the governed ask path to the adapter
    # (15->32, 33->58) and when SDK#368 PR #467 gated that path on readiness
    # qualification (32->35, 58->62).
    ("stegverse/ecosystem_chat_pipeline_http.py", 35): "return 405",
    ("stegverse/ecosystem_chat_pipeline_http.py", 62): "status = 202 if accepted else 422",
    ("stegverse/ecosystem_chat_pipeline.py", 27): "build_persistence_plan",
    ("stegverse/atomic_task_worker_processor.py", 185): "NONE_GRAPH_DERIVATION_ONLY",
    ("stegverse/publisher_return_binding.py", 3): "does not invoke Publisher",
    ("pyproject.toml", 29): "# requests removed 2026-10-13",
    ("scripts/build_sdk_public_wiki.py", 15): "SOURCES = [",
    ("evidence/system-boundary-downstream-status.v0.1.json", 7): '"production_binding_enabled": false',
}


class FirstPartyVerifiedContracts(unittest.TestCase):
    def test_reviewed_implementation_literals_still_hold(self):
        for (path, n), snippet in EXACT.items():
            with self.subTest(path=path, line=n):
                lines = (ROOT/path).read_text(encoding="utf-8").splitlines()
                self.assertIn(snippet, lines[n-1])

    def test_links_use_frozen_code_revision_with_real_line_ranges(self):
        source = DOCUMENT.read_text(encoding="utf-8")
        links = LINK.findall(source)
        self.assertGreaterEqual(len(links), 13)
        for revision, encoded, start, end in links:
            path = (ROOT / unquote(encoded)).resolve()
            self.assertEqual(revision, PIN)
            self.assertTrue(path.is_relative_to(ROOT.resolve()))
            self.assertTrue(path.is_file())
            maximum = len(path.read_text(encoding="utf-8").splitlines())
            self.assertLessEqual(1, int(start))
            self.assertLessEqual(int(start), int(end or start))
            self.assertLessEqual(int(end or start), maximum)

    def test_no_external_generated_pages_or_publication_authority(self):
        text = DOCUMENT.read_text(encoding="utf-8")
        self.assertNotIn("# Page:", text)
        self.assertNotIn("]()", text)
        self.assertIn("not** a revised or relicensed copy", text)
        self.assertIn("not** added to the live SDK Pages builder", text)
        self.assertIn("never itself an approval", text)


if __name__ == "__main__":
    unittest.main()
