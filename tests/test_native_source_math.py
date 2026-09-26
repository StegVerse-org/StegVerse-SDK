"""Tests for generic installed-source mathematics; never package CHF private code."""
from __future__ import annotations

import base64
import hashlib
import inspect
import json
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

from stegverse.governance_navigation import canonical_sha256
from stegverse.manifest_execution import execute_manifest
from stegverse.native_source_math import execute_manifest as native_execute
from stegverse.route_resolution import NATIVE_SOURCE_MATH_ROUTE_ID, PUBLISHED_ROUTES


def _sha(value):
    return "sha256:" + hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def fixture_original_source(document, original_specimen_bytes=None):
    result = {
        "source_only": True,
        "observed_sha256": "sha256:" + hashlib.sha256(original_specimen_bytes).hexdigest(),
        "native_value": document["supplied_value"] * 2,
    }
    result["result_sha256"] = _sha(result)
    return result


class Distribution:
    version = "0.1.0"
    metadata = {"Name": "installed-native-source-fixture"}


class EntryPoint:
    name = "evaluate"

    def __init__(self):
        self.dist = Distribution()

    def load(self):
        return fixture_original_source


def sample_manifest():
    original = b'{"synthetic":"source-v0"}\n'
    source = Path(inspect.getsourcefile(fixture_original_source)).read_bytes()
    blob = hashlib.sha1(
        b"blob " + str(len(source)).encode() + b"\0" + source
    ).hexdigest()
    route = PUBLISHED_ROUTES[NATIVE_SOURCE_MATH_ROUTE_ID]
    payload = {
        "profile": "stegverse.native-source-math.v1",
        "source_distribution": "installed-native-source-fixture",
        "source_version": "0.1.0",
        "source_entry_point": "evaluate",
        "source_git_blob_sha1": blob,
        "source_revision": "fixture-source-commit-not-attested",
        "original_specimen_b64": base64.b64encode(original).decode(),
        "native_input": {"supplied_value": 4, "specimen_sha256": "sha256:" + hashlib.sha256(original).hexdigest()},
    }
    return {
        "manifest_profile": "stegverse.ingress-manifest.v1",
        "manifest_profile_version": "1",
        "source_framework": "fixture-native-math",
        "source_output_id": "fixture-001",
        "created_at": "2026-09-26T00:00:00Z",
        "payload": payload,
        "hashes": {"payload_sha256": canonical_sha256(payload)},
        "declared_intent": "Run pinned installed native mathematical function",
        "requested_consequence": "Source-only mathematical evidence",
        "processing": {"capability": "native_source_math", "route_id": NATIVE_SOURCE_MATH_ROUTE_ID},
        "extensions": {
            "stegverse_route": {
                key: route[key] for key in (
                    "route_id", "lane_class", "routing_surface", "containment",
                    "sandbox_required", "external_consequence_enabled"
                )
            }
        },
    }


class GenericNativeMath(unittest.TestCase):
    def test_uninstalled_owner_source_fails_closed(self):
        with patch("stegverse.native_source_math.metadata.entry_points", return_value=[]):
            with self.assertRaisesRegex(ValueError, "NOT_INSTALLED"):
                execute_manifest(sample_manifest())

    def test_installed_native_result_and_manifest_lineage_exact(self):
        manifest = sample_manifest()
        with patch("stegverse.native_source_math.metadata.entry_points", return_value=[EntryPoint()]):
            raw = native_execute(manifest)
            manifest["payload"]["expected_native_result_sha256"] = raw["native_result_sha256_verified"]
            manifest["hashes"]["payload_sha256"] = canonical_sha256(manifest["payload"])
            output = execute_manifest(manifest)
            raw2 = native_execute(manifest)
        self.assertEqual(output["native_result"], raw2["native_result"])
        self.assertEqual(output["native_result_sha256_verified"], output["native_result"]["result_sha256"])
        self.assertEqual(output["processor_result_sha256"], canonical_sha256(raw2))
        self.assertEqual(output["manifest_lineage"]["processor_result_sha256"], canonical_sha256(raw2))
        self.assertEqual(output["manifest_lineage"]["run_manifest_request"]["route_id"], NATIVE_SOURCE_MATH_ROUTE_ID)
        self.assertEqual(output["request_sha256"], canonical_sha256(output["manifest_lineage"]["run_manifest_request"]))
        self.assertFalse(output["governed_runtime_observed"])

    def test_forged_specimen_fails_before_original_function(self):
        manifest = sample_manifest()
        manifest["payload"]["original_specimen_b64"] = base64.b64encode(b"forged").decode()
        manifest["hashes"]["payload_sha256"] = canonical_sha256(manifest["payload"])
        with patch("stegverse.native_source_math.metadata.entry_points", return_value=[EntryPoint()]):
            with self.assertRaisesRegex(ValueError, "ORIGINAL_SPECIMEN_SHA256_MISMATCH"):
                execute_manifest(manifest)

    def test_installed_source_blob_and_digest_tamper_denied(self):
        manifest = sample_manifest()
        manifest["payload"]["source_git_blob_sha1"] = "0" * 40
        manifest["hashes"]["payload_sha256"] = canonical_sha256(manifest["payload"])
        with patch("stegverse.native_source_math.metadata.entry_points", return_value=[EntryPoint()]):
            with self.assertRaisesRegex(ValueError, "SOURCE_BLOB_MISMATCH"):
                execute_manifest(manifest)
        manifest = sample_manifest()
        manifest["payload"]["expected_native_result_sha256"] = "sha256:" + "0" * 64
        manifest["hashes"]["payload_sha256"] = canonical_sha256(manifest["payload"])
        with patch("stegverse.native_source_math.metadata.entry_points", return_value=[EntryPoint()]):
            with self.assertRaisesRegex(ValueError, "EXPECTED_NATIVE_RESULT_HASH_MISMATCH"):
                execute_manifest(manifest)

    def test_route_substitution_and_unsupported_packages_fail_closed(self):
        manifest = sample_manifest()
        manifest["processing"]["route_id"] = "stegverse.route.canonical-governed.v1"
        with self.assertRaisesRegex(ValueError, "route_id must match"):
            execute_manifest(manifest)
        manifest = sample_manifest()
        manifest["payload"]["source_distribution"] = "unknown-package"
        manifest["hashes"]["payload_sha256"] = canonical_sha256(manifest["payload"])
        with patch("stegverse.native_source_math.metadata.entry_points", return_value=[EntryPoint()]):
            with self.assertRaisesRegex(ValueError, "NOT_INSTALLED"):
                execute_manifest(manifest)


if __name__ == "__main__":
    unittest.main()
