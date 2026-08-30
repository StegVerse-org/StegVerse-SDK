"""SDK thin client for canonical StegCore current-basis evaluation."""
from __future__ import annotations

from typing import Any, Mapping

PACKET_SCHEMA = "stegverse.sdk-current-basis-test.v1"
RESULT_SCHEMA = "stegverse.sdk-current-basis-result.v1"
VECTOR_SCHEMA = "stegverse.cross-framework-current-basis-vector.v0.4"
FROZEN_MANIFEST_SHA256 = "07a08496c21b31f70f6f45ef731aa5f6b2522a6fc8f67f2d0a4c2b6fceda7a3f"
FROZEN_MANIFEST_GIT_BLOB_SHA1 = "59d818a15fc7be732c97dae7d2174d8cfe9a7bab"
PRODUCTION_RUNTIME = "stegcore.current_basis.evaluate_current_basis_vector"


class CurrentBasisSDKError(RuntimeError):
    pass


def _required_text(value: Any, name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise CurrentBasisSDKError(f"{name} is required")
    return text


def evaluate_current_basis(packet: Mapping[str, Any]) -> dict[str, Any]:
    """Delegate one exact frozen v0.4 packet to canonical StegCore.

    The SDK validates the frozen identity/boundary and performs no independent
    standing or disposition calculation.
    """
    if not isinstance(packet, Mapping):
        raise CurrentBasisSDKError("current-basis packet must be an object")
    if packet.get("schema") != PACKET_SCHEMA:
        raise CurrentBasisSDKError(f"unsupported packet schema; expected {PACKET_SCHEMA}")
    if _required_text(packet.get("test_id"), "test_id") != "cross-framework-current-basis-001":
        raise CurrentBasisSDKError("unsupported test_id")
    if packet.get("manifest_sha256") != FROZEN_MANIFEST_SHA256:
        raise CurrentBasisSDKError("packet is not bound to the exact frozen v0.4 manifest SHA-256")
    if packet.get("manifest_git_blob_sha1") != FROZEN_MANIFEST_GIT_BLOB_SHA1:
        raise CurrentBasisSDKError("packet is not bound to the exact frozen v0.4 Git blob")

    vector = packet.get("vector")
    if not isinstance(vector, Mapping):
        raise CurrentBasisSDKError("vector must be an object")
    if vector.get("vector_schema") != VECTOR_SCHEMA:
        raise CurrentBasisSDKError(f"unsupported vector_schema; expected {VECTOR_SCHEMA}")

    try:
        from stegcore.current_basis import evaluate_current_basis_vector
    except ImportError as exc:
        raise CurrentBasisSDKError(
            "Canonical StegCore current-basis capability is required; the SDK provides no fallback evaluator."
        ) from exc

    result = evaluate_current_basis_vector(dict(vector))
    return {
        "schema": RESULT_SCHEMA,
        "sdk_role": "THIN_CLIENT_OF_CANONICAL_STEGCORE",
        "production_runtime": PRODUCTION_RUNTIME,
        "parallel_evaluator": False,
        "sdk_grants_authority": False,
        "sdk_reinterprets_disposition": False,
        "frozen_manifest_sha256": FROZEN_MANIFEST_SHA256,
        "frozen_manifest_git_blob_sha1": FROZEN_MANIFEST_GIT_BLOB_SHA1,
        "result": result,
    }


__all__ = [
    "PACKET_SCHEMA",
    "RESULT_SCHEMA",
    "VECTOR_SCHEMA",
    "FROZEN_MANIFEST_SHA256",
    "FROZEN_MANIFEST_GIT_BLOB_SHA1",
    "PRODUCTION_RUNTIME",
    "CurrentBasisSDKError",
    "evaluate_current_basis",
]
