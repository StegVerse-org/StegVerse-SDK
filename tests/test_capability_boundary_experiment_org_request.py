"""The Experiment 3 organization transition request is reproducible from the SDK alone."""
import hashlib
import tempfile
import unittest
from pathlib import Path

from scripts.build_mir_sv_exp3_manifest import build_exp3_manifest
from scripts.build_capability_boundary_experiment_org_request import (
    CANONICAL_MANIFEST_SHA256, MANIFEST_FILE_SHA256, REQUEST_FILE_SHA256, REQUEST_PATH, WIRE_MANIFEST_SHA256,
    build_exp3_org_request, main, manifest_file_bytes, request_file_bytes)
from stegverse.manifest_state_transition_runtime import derive_execution_request


class Exp3OrganizationRequestTests(unittest.TestCase):
    def test_manifest_is_the_frozen_experiment_3_manifest(self):
        self.assertEqual(hashlib.sha256(manifest_file_bytes(build_exp3_manifest())).hexdigest(), MANIFEST_FILE_SHA256)

    def test_wire_and_canonical_digests(self):
        derived = derive_execution_request(build_exp3_org_request()["manifest"])
        self.assertEqual(derived["wire_manifest_sha256"], WIRE_MANIFEST_SHA256)
        self.assertEqual(derived["canonical_manifest_sha256"], CANONICAL_MANIFEST_SHA256)

    def test_request_binds_the_canonical_digest_not_the_wire_digest(self):
        request = build_exp3_org_request()
        self.assertEqual(request["expected_canonical_manifest_sha256"], CANONICAL_MANIFEST_SHA256)
        self.assertNotEqual(request["expected_canonical_manifest_sha256"], WIRE_MANIFEST_SHA256)
        # The organization workflow requires exactly one manifest form plus goal and standing.
        self.assertIn("manifest", request)
        self.assertNotIn("build_manifest", request)
        self.assertTrue(request["owning_existing_goal"] and request["standing"])
        self.assertIn("predecessor", request["standing"])

    def test_request_file_bytes_are_deterministic(self):
        self.assertEqual(hashlib.sha256(request_file_bytes(build_exp3_org_request())).hexdigest(), REQUEST_FILE_SHA256)

    def test_main_writes_the_request_at_the_committed_request_path(self):
        with tempfile.TemporaryDirectory() as root:
            self.assertEqual(main(["--organization-root", root]), 0)
            written = (Path(root) / REQUEST_PATH).read_bytes()
        self.assertEqual(hashlib.sha256(written).hexdigest(), REQUEST_FILE_SHA256)
        self.assertTrue(REQUEST_PATH.startswith(".stegverse/transition-requests/"))


if __name__ == "__main__":
    unittest.main()
