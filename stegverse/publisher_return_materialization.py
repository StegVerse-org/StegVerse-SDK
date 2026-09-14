"""Retain exact canonical SDK Publisher-return bindings for downstream egress.

This module is a narrow materialization/export seam around the existing
``assemble_publisher_return`` implementation. It does not invoke Publisher,
LLM Adapter, Interlock/InTr, a far-side transition, or MIR and grants no
authority. Caller-supplied inputs remain responsible for their own provenance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from .publisher_return_binding import (
    READY_STATE,
    SDK_RETURN_BINDING_SCHEMA,
    PublisherReturnBindingError,
    assemble_publisher_return,
    verify_publisher_return_binding,
)

MATERIALIZATION_RECEIPT_SCHEMA = "stegverse.sdk.publisher-return-materialization-receipt/v1"


class PublisherReturnMaterializationError(ValueError):
    pass


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _load_json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise PublisherReturnMaterializationError(f"{label} file not found: {path}") from exc
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PublisherReturnMaterializationError(f"{label} JSON invalid: {path}") from exc
    if not isinstance(value, dict):
        raise PublisherReturnMaterializationError(f"{label} must be a JSON object")
    return value


def _write_exact(path: Path, payload: bytes, *, overwrite: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = "wb" if overwrite else "xb"
    try:
        with path.open(mode) as handle:
            handle.write(payload)
    except FileExistsError as exc:
        raise PublisherReturnMaterializationError(
            f"refusing to overwrite existing SDK return artifact: {path}"
        ) from exc


def materialize_publisher_return_binding(
    *,
    manifest: Mapping[str, Any],
    manifest_receipt_id: str,
    publisher_return_bytes: bytes,
    output_path: str | Path,
    downstream_completion_capsule: Mapping[str, Any] | None = None,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Assemble and retain exact SDK-return bytes without promoting egress.

    The returned receipt describes only exact-byte retention. It does not claim
    that the supplied Publisher return or completion capsule came from a live or
    authentic MIR execution.
    """
    binding = assemble_publisher_return(
        manifest=manifest,
        manifest_receipt_id=manifest_receipt_id,
        publisher_return_bytes=publisher_return_bytes,
        downstream_completion_capsule=downstream_completion_capsule,
    )
    verify_publisher_return_binding(binding)
    payload = canonical_json_bytes(binding)
    path = Path(output_path)
    _write_exact(path, payload, overwrite=overwrite)

    observed = path.read_bytes()
    if observed != payload:
        raise PublisherReturnMaterializationError("retained SDK return bytes changed after write")

    return {
        "schema": MATERIALIZATION_RECEIPT_SCHEMA,
        "output_path": str(path),
        "output_sha256": sha256_bytes(observed),
        "output_bytes": len(observed),
        "binding_schema": binding.get("schema"),
        "binding_sha256": binding.get("binding_sha256"),
        "communication_state": binding.get("communication_state"),
        "sdk_return_binding_observed": binding.get("sdk_return_binding_observed") is True,
        "final_stegverse_transition_observed": binding.get("final_stegverse_transition_observed") is True,
        "interlock_intr_egress_observed": binding.get("interlock_intr_egress_observed") is True,
        "far_side_transition_observed": binding.get("far_side_transition_observed") is True,
        "authentic_external_mir_endpoint_substitution_observed": (
            binding.get("authentic_external_mir_endpoint_substitution_observed") is True
        ),
        "communication_complete": binding.get("communication_complete") is True,
        "input_runtime_provenance_claimed": False,
        "authentic_mir_provenance_claimed": False,
        "authority_effect": "NONE",
    }


def materialize_from_files(
    *,
    manifest_path: str | Path,
    manifest_receipt_id: str,
    publisher_return_path: str | Path,
    output_path: str | Path,
    downstream_completion_capsule_path: str | Path | None = None,
    overwrite: bool = False,
) -> dict[str, Any]:
    manifest = _load_json_object(Path(manifest_path), "manifest")
    try:
        publisher_return_bytes = Path(publisher_return_path).read_bytes()
    except OSError as exc:
        raise PublisherReturnMaterializationError(
            f"Publisher return bytes unavailable: {publisher_return_path}"
        ) from exc
    capsule = None
    if downstream_completion_capsule_path is not None:
        capsule = _load_json_object(Path(downstream_completion_capsule_path), "downstream completion capsule")
    return materialize_publisher_return_binding(
        manifest=manifest,
        manifest_receipt_id=manifest_receipt_id,
        publisher_return_bytes=publisher_return_bytes,
        downstream_completion_capsule=capsule,
        output_path=output_path,
        overwrite=overwrite,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Retain exact canonical SDK Publisher-return binding bytes without executing egress."
    )
    parser.add_argument("--manifest", required=True, help="Original admitted manifest JSON path")
    parser.add_argument("--manifest-receipt-id", required=True, help="Original manifest receipt ID")
    parser.add_argument("--publisher-return", required=True, help="Exact canonical Publisher return bytes path")
    parser.add_argument(
        "--completion-capsule",
        help="Original SDK downstream completion capsule JSON path; required by MIR round-trip returns",
    )
    parser.add_argument("--output", required=True, help="Path for exact SDK return binding bytes")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Explicitly replace an existing output path; default is fail closed",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        receipt = materialize_from_files(
            manifest_path=args.manifest,
            manifest_receipt_id=args.manifest_receipt_id,
            publisher_return_path=args.publisher_return,
            output_path=args.output,
            downstream_completion_capsule_path=args.completion_capsule,
            overwrite=args.overwrite,
        )
    except (PublisherReturnBindingError, PublisherReturnMaterializationError) as exc:
        parser.exit(2, f"SDK return materialization failed: {exc}\n")
    print(canonical_json_bytes(receipt).decode("utf-8"))
    return 0


__all__ = [
    "MATERIALIZATION_RECEIPT_SCHEMA",
    "PublisherReturnMaterializationError",
    "canonical_json_bytes",
    "materialize_publisher_return_binding",
    "materialize_from_files",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
