"""Keep first-party drift corrections attached to source, never generated-page approval."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/deepwiki-review/CURRENT_SOURCE_DRIFT_CORRECTIONS.md"
PIN = "6ffbc38440408668fe23428dafafae60492b8591"

class ThreeSourceDriftTests(unittest.TestCase):
    def test_narrow_current_source_anchors(self):
        # Anchors keep their literal and move to the literal's current line when
        # a merged change moves it; the document links stay frozen at PIN.
        checks = {
            "stegverse/manifest_builder.py": {
                # L126 / L149 / L211 at PIN. Drifted across route, capability
                # and execution-profile publications (PR #384, #385, #422,
                # #426, I-12a), then SDK#368 PR #446 (170->172, 199->201,
                # 267->269) and PR #447 (172->188, 201->217, 269->285).
                188: "def _route_declaration(",
                217: "def _validate_governance_request(",
                285: "def build_manifest(",
            },
            "tests/test_mir_sv_exp3_manifest.py": {
                # L43 / L47 / L51 at PIN; 4534b5a (destination taken from the
                # manifest instead of an ingress argument) removed one line
                # above the test, 43->42, 47->46, 51->50.
                42: "def test_diagnostic_does_not_upgrade_unobserved_runtime",
                46: 'NOT_OBSERVED',
                50: 'NONE_DIAGNOSTIC_ONLY',
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
