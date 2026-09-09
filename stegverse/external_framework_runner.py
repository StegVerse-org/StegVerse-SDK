"""One-command external-framework execution path for the StegVerse SDK.

This module composes existing SDK primitives. It does not implement governance,
infer source-framework semantics, or grant authority. Source-native data remains
external semantic custody; processor-specific governance evidence remains a
separate explicit input.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
from typing import Any, Mapping

from .manifest_builder import RETURN_DEPTHS, build_manifest
from .manifest_contract import validate_ingress_manifest

DEFAULT_CUSTODY_DB = "./stegverse-master-records-validation.db"
DEFAULT_HOST_IDENTITY = "stegverse-sovereign-local"
EVALUATION_DECLARATION_EXTENSION = "evaluation_declaration"


def _load_json(path: str) -> Any:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: {exc}") from exc


def _write_json(value: Any, path: str | None) -> None:
    text = json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if path:
        Path(path).write_text(text, encoding="utf-8")
    else:
        print(text, end="")


def prepare_external_framework_manifest(
    *,
    data: Any,
    source_framework: str,
    source_output_id: str,
    processor_request: Mapping[str, Any],
    evaluation_declaration: Mapping[str, Any] | None = None,
    process: str = "governance",
    return_depth: str = "result+evidence",
    data_class: str | None = None,
    source_instance: str | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    """Build a submission-ready manifest and retain preregistration metadata.

    ``evaluation_declaration`` is retained as manifest evidence metadata under
    ``extensions``. It is deliberately not inserted into the governance request
    and therefore is not an input to the StegGate decision model.
    """
    manifest = build_manifest(
        data=data,
        source_framework=source_framework,
        source_output_id=source_output_id,
        processor_request=processor_request,
        process=process,
        return_depth=return_depth,
        data_class=data_class,
        source_instance=source_instance,
        created_at=created_at,
    )
    if evaluation_declaration is not None:
        if not isinstance(evaluation_declaration, Mapping):
            raise ValueError("evaluation_declaration must be an object when supplied")
        manifest["extensions"][EVALUATION_DECLARATION_EXTENSION] = deepcopy(
            dict(evaluation_declaration)
        )
        validate_ingress_manifest(manifest)
    return manifest


def run_external_framework(
    *,
    data: Any,
    source_framework: str,
    source_output_id: str,
    processor_request: Mapping[str, Any],
    evaluation_declaration: Mapping[str, Any] | None = None,
    process: str = "governance",
    return_depth: str = "result+evidence",
    data_class: str | None = None,
    source_instance: str | None = None,
    created_at: str | None = None,
    custody_db: str = DEFAULT_CUSTODY_DB,
    host_identity: str = DEFAULT_HOST_IDENTITY,
    replay: bool = True,
    reconstruct: bool = True,
) -> dict[str, Any]:
    """Build, submit, and optionally replay/reconstruct one external-framework run."""
    from .governance_ingress_runtime import run_external_manifest
    from . import sovereign_validation_runtime

    manifest = prepare_external_framework_manifest(
        data=data,
        source_framework=source_framework,
        source_output_id=source_output_id,
        processor_request=processor_request,
        evaluation_declaration=evaluation_declaration,
        process=process,
        return_depth=return_depth,
        data_class=data_class,
        source_instance=source_instance,
        created_at=created_at,
    )
    governed_result = run_external_manifest(
        manifest,
        custody_db=custody_db,
        host_identity=host_identity,
    )
    manifest_receipt_id = governed_result.get("manifest_receipt_id")
    if not isinstance(manifest_receipt_id, str) or not manifest_receipt_id:
        raise RuntimeError("canonical runtime did not return manifest_receipt_id")

    result: dict[str, Any] = {
        "schema": "stegverse.sdk.external-framework-run.v1",
        "source_framework": source_framework,
        "source_output_id": source_output_id,
        "processing": deepcopy(manifest["processing"]),
        "return_projection": deepcopy(manifest["return_projection"]),
        "manifest_receipt_id": manifest_receipt_id,
        "manifest": manifest,
        "governed_result": governed_result,
    }
    if replay:
        result["replay"] = sovereign_validation_runtime.replay_sovereign(
            manifest_receipt_id, custody_db=custody_db
        )
    if reconstruct:
        result["reconstruction"] = sovereign_validation_runtime.reconstruct_sovereign(
            manifest_receipt_id, custody_db=custody_db
        )
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="stegverse external-run",
        description=(
            "Build and execute a source-native external-framework manifest through "
            "an installed StegVerse processor route."
        ),
    )
    parser.add_argument("--input", required=True, help="JSON file containing source-native data")
    parser.add_argument(
        "--governance-request",
        required=True,
        help="JSON file containing the complete governance processor request",
    )
    parser.add_argument(
        "--evaluation-declaration",
        help="optional preregistered evaluator declaration retained as evidence metadata",
    )
    parser.add_argument("--source-framework", required=True)
    parser.add_argument("--source-output-id", required=True)
    parser.add_argument("--source-instance")
    parser.add_argument("--data-class")
    parser.add_argument("--process", default="governance", choices=("governance",))
    parser.add_argument("--return-depth", default="result+evidence", choices=sorted(RETURN_DEPTHS))
    parser.add_argument("--created-at")
    parser.add_argument("--custody-db", default=DEFAULT_CUSTODY_DB)
    parser.add_argument("--host-identity", default=DEFAULT_HOST_IDENTITY)
    parser.add_argument("--no-replay", action="store_true")
    parser.add_argument("--no-reconstruct", action="store_true")
    parser.add_argument("--output", help="write complete run artifact to this path; default stdout")

    args = parser.parse_args(argv)
    try:
        declaration = (
            _load_json(args.evaluation_declaration)
            if args.evaluation_declaration
            else None
        )
        result = run_external_framework(
            data=_load_json(args.input),
            source_framework=args.source_framework,
            source_output_id=args.source_output_id,
            processor_request=_load_json(args.governance_request),
            evaluation_declaration=declaration,
            process=args.process,
            return_depth=args.return_depth,
            data_class=args.data_class,
            source_instance=args.source_instance,
            created_at=args.created_at,
            custody_db=args.custody_db,
            host_identity=args.host_identity,
            replay=not args.no_replay,
            reconstruct=not args.no_reconstruct,
        )
        _write_json(result, args.output)
        return 0
    except (ValueError, RuntimeError) as exc:
        parser.error(str(exc))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
