from pathlib import Path
import json
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


class PackageVersionIdentityTests(unittest.TestCase):
    def test_pyproject_owns_release_candidate_version(self):
        text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertRegex(text, r"(?m)^name\s*=\s*[\"']stegverse-sdk[\"']\s*$")
        self.assertRegex(text, r"(?m)^version\s*=\s*[\"']1\.3\.0[\"']\s*$")
        self.assertNotRegex(text, r"(?m)^version\s*=\s*[\"']1\.2\.0(?:\.dev0)?[\"']\s*$")
        self.assertNotRegex(text, r"(?m)^version\s*=\s*[\"']1\.1\.0[\"']\s*$")
        self.assertNotRegex(text, r"(?m)^version\s*=\s*[\"']1\.0\.13[\"']\s*$")

    def test_version_json_identifies_1_3_0_release_candidate(self):
        version = json.loads((ROOT / "VERSION.json").read_text(encoding="utf-8"))
        self.assertEqual(version["component_version"], "1.3.0")
        self.assertEqual(version["version_stage"], "RELEASE_CANDIDATE")
        self.assertEqual(version["release_candidate"]["target_tag"], "v1.3.0")
        self.assertEqual(
            version["release_candidate"]["source_candidate_commit"],
            "3cd3198375b687e73f06071e9c16e18d8a1c527c",
        )
        self.assertEqual(
            version["release_candidate"]["source_candidate_tree"],
            "31630c52fc0c34759ab81a3bbb710a70223ba86c",
        )
        self.assertEqual(version["release_candidate"]["four_stage_manifest_only_state"], "PASS")
        self.assertEqual(version["release_candidate"]["tag_publication"], "READY_PENDING_TV_TVC_EXECUTION")
        self.assertEqual(version["development_line"]["version"], "1.4.0.dev0")

    def test_hgai_is_hypothetical_example_not_integration_claim(self):
        version = json.loads((ROOT / "VERSION.json").read_text(encoding="utf-8"))
        hgai = version["hypothetical_examples"]["HGAI"]
        self.assertEqual(hgai["status"], "HYPOTHETICAL_ECOSYSTEM_EXAMPLE")
        self.assertFalse(hgai["integration_claim"])

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

    def test_release_handoff_identifies_current_1_3_0_candidate(self):
        text = (ROOT / "PRODUCTION_RELEASE_SET_MIRROR_HANDOFF.md").read_text(encoding="utf-8")
        self.assertIn("current_public_package_candidate: 1.3.0", text)
        self.assertIn("current_public_tag_candidate: v1.3.0", text)
        self.assertIn("HGAI_STATUS: HYPOTHETICAL_ECOSYSTEM_EXAMPLE", text)
        self.assertIn("MANIFESTED_CONCURRENT_WORKER_GROUPS: VALIDATED", text)
        self.assertIn("FOUR_STAGE_MANIFEST_ONLY_EXPERIMENT: PASS", text)


if __name__ == "__main__":
    unittest.main()
