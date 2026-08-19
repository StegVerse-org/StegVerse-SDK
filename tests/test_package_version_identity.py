from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


class PackageVersionIdentityTests(unittest.TestCase):
    def test_pyproject_owns_current_public_version(self):
        text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertRegex(text, r"(?m)^name\s*=\s*[\"']stegverse-sdk[\"']\s*$")
        self.assertRegex(text, r"(?m)^version\s*=\s*[\"']1\.1\.0[\"']\s*$")
        self.assertNotRegex(text, r"(?m)^version\s*=\s*[\"']1\.0\.13[\"']\s*$")

    def test_setup_py_contains_no_independent_distribution_metadata(self):
        text = (ROOT / "setup.py").read_text(encoding="utf-8")
        prohibited = (
            r"\bversion\s*=",
            r"\bname\s*=\s*[\"']stegverse-sdk",
            r"\binstall_requires\s*=",
            r"\bpython_requires\s*=",
            r"\bentry_points\s*=",
        )
        for pattern in prohibited:
            with self.subTest(pattern=pattern):
                self.assertIsNone(re.search(pattern, text), pattern)

    def test_release_handoff_blocks_consumed_1_0_13_identity(self):
        text = (ROOT / "PRODUCTION_RELEASE_SET_MIRROR_HANDOFF.md").read_text(encoding="utf-8")
        self.assertIn("current_public_package_candidate: 1.1.0", text)
        self.assertIn("historical_v1.0.13_mutable: false", text)
        self.assertIn("MUST NOT be published to PyPI as `1.0.13`", text)
        self.assertIn("v1.0.13-evaluation-r2", text)
        self.assertIn("SUPERSEDED", text)


if __name__ == "__main__":
    unittest.main()
