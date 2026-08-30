import builtins
import sys
import types
import unittest
from unittest import mock

from stegverse.current_basis import (
    FROZEN_MANIFEST_GIT_BLOB_SHA1,
    FROZEN_MANIFEST_SHA256,
    PRODUCTION_RUNTIME,
    CurrentBasisSDKError,
    evaluate_current_basis,
)


def packet():
    return {
        "schema": "stegverse.sdk-current-basis-test.v1",
        "test_id": "cross-framework-current-basis-001",
        "manifest_sha256": FROZEN_MANIFEST_SHA256,
        "manifest_git_blob_sha1": FROZEN_MANIFEST_GIT_BLOB_SHA1,
        "vector": {
            "vector_schema": "stegverse.cross-framework-current-basis-vector.v0.4",
        },
    }


class CurrentBasisSDKTests(unittest.TestCase):
    def test_sdk_is_thin_client_of_canonical_stegcore(self):
        fake_package = types.ModuleType("stegcore")
        fake_module = types.ModuleType("stegcore.current_basis")
        calls = []

        def evaluate_current_basis_vector(vector):
            calls.append(vector)
            return {
                "schema": "stegcore.current-basis-evaluation.v1",
                "evaluation": {"disposition": "FAIL_CLOSED"},
            }

        fake_module.evaluate_current_basis_vector = evaluate_current_basis_vector
        with mock.patch.dict(
            sys.modules,
            {"stegcore": fake_package, "stegcore.current_basis": fake_module},
            clear=False,
        ):
            result = evaluate_current_basis(packet())

        self.assertEqual(result["production_runtime"], PRODUCTION_RUNTIME)
        self.assertFalse(result["parallel_evaluator"])
        self.assertFalse(result["sdk_grants_authority"])
        self.assertFalse(result["sdk_reinterprets_disposition"])
        self.assertEqual(result["result"]["evaluation"]["disposition"], "FAIL_CLOSED")
        self.assertEqual(len(calls), 1)

    def test_wrong_frozen_hash_fails_before_stegcore_import(self):
        value = packet()
        value["manifest_sha256"] = "0" * 64
        with self.assertRaisesRegex(CurrentBasisSDKError, "exact frozen v0.4"):
            evaluate_current_basis(value)

    def test_no_stegcore_fallback(self):
        value = packet()
        original_import = builtins.__import__

        def blocked_import(name, *args, **kwargs):
            if name.startswith("stegcore"):
                raise ImportError("blocked")
            return original_import(name, *args, **kwargs)

        with mock.patch.dict(sys.modules, {"stegcore": None, "stegcore.current_basis": None}, clear=False):
            with mock.patch("builtins.__import__", side_effect=blocked_import):
                with self.assertRaisesRegex(CurrentBasisSDKError, "no fallback evaluator"):
                    evaluate_current_basis(value)


if __name__ == "__main__":
    unittest.main()
