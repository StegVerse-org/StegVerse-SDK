from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "release.yml"
HANDOFF = ROOT / "docs" / "PYPI_TRUSTED_PUBLISHING_MIRROR_HANDOFF.md"


class PyPITrustedPublishingContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = WORKFLOW.read_text(encoding="utf-8")
        cls.handoff = HANDOFF.read_text(encoding="utf-8")

    def test_exact_trusted_publisher_identity(self) -> None:
        self.assertIn("name: Publish SDK to PyPI (Trusted Publisher)", self.text)
        self.assertIn("types: [published]", self.text)
        self.assertIn("name: pypi", self.text)
        self.assertIn("pypa/gh-action-pypi-publish@release/v1", self.text)
        self.assertIn("PyPI project: stegverse-sdk", self.handoff)
        self.assertIn("PyPI trusted workflow: .github/workflows/release.yml", self.handoff)
        self.assertIn("GitHub environment: pypi", self.handoff)

    def test_oidc_permission_is_publish_job_only(self) -> None:
        self.assertEqual(self.text.count("id-token: write"), 1)
        build_section, publish_section = self.text.split("  publish-pypi:", 1)
        self.assertNotIn("id-token: write", build_section)
        self.assertIn("id-token: write", publish_section)
        self.assertIn("permissions: {}", build_section)

    def test_no_repository_mutation_or_static_publish_secret(self) -> None:
        prohibited = (
            "contents: write",
            "packages: write",
            "actions: write",
            "pull-requests: write",
            "PYPI_API_TOKEN: ${{",
            "PYPI_TOKEN: ${{",
            "password:",
            "git push",
            "gh release create",
            "create-release",
            "softprops/action-gh-release",
        )
        for marker in prohibited:
            self.assertNotIn(marker, self.text)

    def test_release_identity_is_tag_bound_and_version_checked(self) -> None:
        self.assertIn("github.event.release.tag_name", self.text)
        self.assertIn("^v[0-9]+\\.[0-9]+\\.[0-9]+$", self.text)
        self.assertIn("TAG_PACKAGE_VERSION_MATCH", self.text)
        self.assertIn("project']['version']", self.text)
        self.assertIn("archive/refs/tags/${RELEASE_TAG}.tar.gz", self.text)

    def test_exact_artifact_set_is_verified_before_publish(self) -> None:
        self.assertIn("python -m twine check dist/*", self.text)
        self.assertIn("sha256sum dist/* | sort | tee dist/SHA256SUMS", self.text)
        self.assertIn("sha256sum -c SHA256SUMS", self.text)
        self.assertIn("rm dist/SHA256SUMS", self.text)
        self.assertIn("find dist -maxdepth 1 -type f -name '*.whl'", self.text)
        self.assertIn("find dist -maxdepth 1 -type f -name '*.tar.gz'", self.text)

    def test_no_stegverse_runtime_authority_is_introduced(self) -> None:
        prohibited_runtime_markers = (
            "heartbeat_runtime",
            "WorkerCoordinator",
            "G18",
            "TVC_SECRET",
            "TV_IDENTITY_KEY",
            "vault://",
        )
        for marker in prohibited_runtime_markers:
            self.assertNotIn(marker, self.text)
        self.assertIn("StegVerse runtime authority -> NONE", self.handoff)

    def test_workflow_does_not_accept_manual_or_push_release_trigger(self) -> None:
        # Publication must follow an already-published exact release; source pushes
        # and workflow_dispatch are validation/administrative surfaces, not publish authority.
        on_block = self.text.split("permissions:", 1)[0]
        self.assertNotRegex(on_block, re.compile(r"(?m)^\s*push:"))
        self.assertNotIn("workflow_dispatch:", on_block)


if __name__ == "__main__":
    unittest.main()
