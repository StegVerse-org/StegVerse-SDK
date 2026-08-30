import importlib
import sys
import types

import pytest

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


def test_sdk_is_thin_client_of_canonical_stegcore(monkeypatch):
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
    monkeypatch.setitem(sys.modules, "stegcore", fake_package)
    monkeypatch.setitem(sys.modules, "stegcore.current_basis", fake_module)

    result = evaluate_current_basis(packet())
    assert result["production_runtime"] == PRODUCTION_RUNTIME
    assert result["parallel_evaluator"] is False
    assert result["sdk_grants_authority"] is False
    assert result["sdk_reinterprets_disposition"] is False
    assert result["result"]["evaluation"]["disposition"] == "FAIL_CLOSED"
    assert len(calls) == 1


def test_wrong_frozen_hash_fails_before_stegcore_import():
    value = packet()
    value["manifest_sha256"] = "0" * 64
    with pytest.raises(CurrentBasisSDKError, match="exact frozen v0.4"):
        evaluate_current_basis(value)


def test_no_stegcore_fallback(monkeypatch):
    value = packet()
    monkeypatch.delitem(sys.modules, "stegcore.current_basis", raising=False)
    monkeypatch.delitem(sys.modules, "stegcore", raising=False)

    real_import = __import__

    def blocked_import(name, *args, **kwargs):
        if name.startswith("stegcore"):
            raise ImportError("blocked")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", blocked_import)
    with pytest.raises(CurrentBasisSDKError, match="no fallback evaluator"):
        evaluate_current_basis(value)
