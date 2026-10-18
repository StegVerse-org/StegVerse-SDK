"""The Experiment 3 organization transition request is reproducible from the SDK alone."""
import contextlib
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts.build_mir_sv_exp3_manifest import build_exp3_manifest
import scripts.build_capability_boundary_experiment_org_request as org_request
from scripts.build_capability_boundary_experiment_org_request import (
    CANONICAL_MANIFEST_SHA256, MANIFEST_FILE_SHA256, REQUEST_FILE_SHA256, REQUEST_PATH, WIRE_MANIFEST_SHA256,
    build_exp3_org_request, main, manifest_file_bytes, request_file_bytes)
from stegverse.manifest_state_transition_runtime import derive_execution_request

SIX_FIELDS = {"failure_code", "failed_predicate", "required_evidence_or_repair", "retry_entrypoint",
              "owning_existing_goal", "next_attempt"}


def organization_boundary():
    """A boundary shaped like StegVerse-org/.github resident-runtime/organization_manifest_ingress.py
    boundary(), which reads org-runtime/interlock-intr.json (org 40a5d23): its schema, owner and
    the sdk-manifest-ingress binding the SDK resolves, copied from that document."""
    return {
        "schema": "stegverse.organization-interlock-intr-boundary/v1",
        "organization": "StegVerse-org",
        "owner_repository": "StegVerse-org/.github",
        "ingress": {"capability_endpoint_bindings": [{
            "profile_id": "sdk-manifest-ingress",
            "profile_name": "SDK:ManifestIngress",
            "operation": "SUBMIT_MANIFEST",
            "payload_schema": "stegverse.ingress-manifest.v1",
            "capability_declaration_owner": "StegVerse-Labs/StegOS",
            "capability_binding_owner": "StegVerse-org/StegVerse-SDK",
            "receiving_operation": {
                "owner_repository": "StegVerse-org/.github",
                "operation_id": "ORGANIZATION_SDK_MANIFEST_INGRESS",
                "operation": "resident-runtime/organization_manifest_ingress.py",
                "admission": "resident-runtime/sdk_manifest_crossing.py::cross",
                "processing": "org-boundary/runtime/process_boundary.py",
                "receipt_append": "resident-runtime/aggregate_repo_transition.py::append",
                "emits": "stegverse.organization-transition-receipt/v1",
                "transport": "INTERLOCK_INTR",
                "credential_authority": "TV/TVC",
                "github_token_runtime_authority": "NONE",
            },
            "binding_role": "ORGANIZATION_RECEIVING_OPERATION_RESOLUTION",
            "authority_effect": "NONE_BINDING_ONLY",
            "grants_routing_authority": False,
            "grants_admission_authority": False,
            "grants_execution_authority": False,
            "environment_selected_ingress": False,
        }]},
    }


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

    def test_canonical_digest_is_identical_with_and_without_the_organization_boundary(self):
        # The organization ingress recomputes with derive_execution_request(manifest, boundary());
        # this script derives with no boundary. The boundary only selects the destination.
        manifest = build_exp3_org_request()["manifest"]
        without = derive_execution_request(manifest, None)
        with_boundary = derive_execution_request(manifest, organization_boundary())
        self.assertEqual(with_boundary["canonical_manifest_sha256"], without["canonical_manifest_sha256"])
        self.assertEqual(with_boundary["canonical_manifest_sha256"], CANONICAL_MANIFEST_SHA256)
        # The boundary was actually applied, not ignored.
        self.assertIsNone(without["manifest_declared_destination"])
        self.assertEqual(with_boundary["manifest_declared_destination"]["owner_repository"], "StegVerse-org/.github")

    def _main_fails_closed(self):
        stderr = io.StringIO()
        with tempfile.TemporaryDirectory() as root, contextlib.redirect_stderr(stderr):
            code = main(["--organization-root", root])
            self.assertFalse((Path(root) / REQUEST_PATH).exists())
        self.assertNotEqual(code, 0)
        record = json.loads(stderr.getvalue())
        self.assertEqual(set(record), SIX_FIELDS)
        self.assertEqual(record["retry_entrypoint"], "python -m scripts.build_capability_boundary_experiment_org_request")
        self.assertEqual(record["owning_existing_goal"], "MIR-SV-CAPABILITY-BOUNDARY-EXPERIMENT-003")
        for field in ("failed_predicate", "required_evidence_or_repair", "next_attempt"):
            self.assertTrue(record[field])
        return record

    def test_request_digest_mismatch_emits_six_field_record(self):
        with mock.patch.object(org_request, "REQUEST_FILE_SHA256", "0" * 64):
            record = self._main_fails_closed()
        self.assertEqual(record["failure_code"], "EXP3_ORG_REQUEST_DIGEST_MISMATCH")
        self.assertIn(REQUEST_FILE_SHA256, record["failed_predicate"])

    def test_canonical_digest_mismatch_emits_six_field_record(self):
        with mock.patch.object(org_request, "CANONICAL_MANIFEST_SHA256", "0" * 64):
            record = self._main_fails_closed()
        self.assertEqual(record["failure_code"], "EXP3_ORG_REQUEST_CANONICAL_MANIFEST_MISMATCH")
        self.assertIn(CANONICAL_MANIFEST_SHA256, record["failed_predicate"])


if __name__ == "__main__":
    unittest.main()
