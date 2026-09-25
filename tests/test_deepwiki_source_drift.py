"""Keep first-party drift corrections attached to source, never generated-page approval."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/deepwiki-review/CURRENT_SOURCE_DRIFT_CORRECTIONS.md"
PIN = "6ffbc38440408668fe23428dafafae60492b8591"

class ThreeSourceDriftTests(unittest.TestCase):
    def test_narrow_current_source_anchors(self):
        checks = {
            "stegverse/manifest_builder.py": {
                126: "def _route_declaration(",
                149: "def _validate_governance_request(",
                211: "def build_manifest(",
            },
            "tests/test_mir_sv_exp3_manifest.py": {
                43: "def test_diagnostic_does_not_upgrade_unobserved_runtime",
                47: 'NOT_OBSERVED',
                51: 'NONE_DIAGNOSTIC_ONLY',
            },
        }
        doc=DOC.read_text(encoding="utf-8")
        self.assertIn(PIN, doc)
        for file, assertions in checks.items():
            lines=(ROOT/file).read_text(encoding="utf-8").splitlines()
            for n, required in assertions.items():
                with self.subTest(file=file, line=n):
                    self.assertIn(required, lines[n-1])
        for original in ("98", "99", "439"):
            self.assertIn("| " + original + " |", doc)
        self.assertIn("not** be rewritten", doc)
        self.assertIn("do **not** retroactively", doc)

if __name__ == "__main__":
    unittest.main()
