"""External-framework path for the StegVerse SDK.

This module composes existing SDK primitives. It does not implement governance,
infer source-framework semantics, resolve final security posture, or grant authority.
Source-native data, evaluator preregistration, governance evidence, and posture
request inputs remain distinct.

Two lanes, and the distinction between them is the point.

``manifest_external_framework_submission`` is the SDK's job: build the manifest and
hand it to the receiving Interlock runtime at the destination the manifest itself
declares. This is the default path. Nothing is executed, transported or awaited here.

``run_external_framework`` executes locally against a local custody store and may
replay and reconstruct from it. That is an enclosed validation lane, useful for
testing a manifest before it is handed off. It is NOT the canonical lifecycle:
Interlock/InTr owns transition admission, and the Organization owns runtime reality
at its ledger root. A result from this lane says so in its own fields and may never
be promoted to canonical closure.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
from typing import Any, Callable, Mapping

from .evaluator_manifest_builder import (
    EVALUATION_DECLARATION_EXTENSION,
    build_evaluator_governance_manifest,
)
from .manifest_builder import RETURN_DEPTHS

DEFAULT_CUSTODY_DB = "./stegverse-master-records-validation.db"
DEFAULT_HOST_IDENTITY = "stegverse-sovereign-local"


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
    security_posture_request: Mapping[str, Any] | None = None,
    process: str = "governance",
    return_depth: str = "result+evidence",
    data_class: str | None = None,
    source_instance: str | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    """Build a submission-ready evaluator-safe manifest."""
    if process.strip().lower() != "governance":
        raise ValueError("external evaluator composition currently supports governance processing only")
    return build_evaluator_governance_manifest(
        data=data,
        source_framework=source_framework,
        source_output_id=source_output_id,
        governance_request=processor_request,
        evaluation_declaration=evaluation_declaration,
        security_posture_request=security_posture_request,
        return_depth=return_depth,
        data_class=data_class,
        source_instance=source_instance,
        created_at=created_at,
    )


def manifest_external_framework_submission(*, canonical_source_fetcher=None, **kwargs: Any) -> dict[str, Any]:
    """Manifest the submission and hand it to Interlock/InTr. The SDK's whole job.

    Reuse public run-manifest destination resolution from the canonical source
    reader. Completion egress never chooses the outbound destination. No receiver
    liveness check or transport is performed; the far side stays unobserved.
    """
    from .manifest_execution import execute_manifest

    manifest = prepare_external_framework_manifest(**kwargs)
    handoff = execute_manifest(manifest, canonical_source_fetcher=canonical_source_fetcher)
    return {
        "schema": "stegverse.sdk.external-framework-submission.v1",
        "status": "SUBMISSION_READY",
        "source_framework": manifest["source_framework"],
        "source_output_id": manifest["source_output_id"],
        "processing": deepcopy(manifest["processing"]),
        "return_projection": deepcopy(manifest["return_projection"]),
        "manifest": manifest,
        "handoff": handoff,
        "manifest_declared_destination": handoff.get("destination"),
        "execution_performed": False,
        "manifest_receipt_id": None,
        "posture_resolution_performed": False,
        # The far side is the Interlock's; none of it is observed from here.
        "intr_admission_observed": False,
        "far_side_transition_observed": False,
        "organization_receipt_observed": False,
        "evidence_class": "SDK_LOCAL_MANIFEST_HANDOFF",
    }


# The former name. "prepare" read as a partial step; the function was always the
# complete one. Retained so existing callers keep working.
prepare_external_framework_submission = manifest_external_framework_submission


def run_external_framework(
    *,
    data: Any,
    source_framework: str,
    source_output_id: str,
    processor_request: Mapping[str, Any],
    evaluation_declaration: Mapping[str, Any] | None = None,
    security_posture_request: Mapping[str, Any] | None = None,
    process: str = "governance",
    return_depth: str = "result+evidence",
    data_class: str | None = None,
    source_instance: str | None = None,
    created_at: str | None = None,
    custody_db: str = DEFAULT_CUSTODY_DB,
    host_identity: str = DEFAULT_HOST_IDENTITY,
    replay: bool = True,
    reconstruct: bool = True,
    intr_posture_resolver: Callable[..., Mapping[str, Any]] | None = None,
    posture_observed_at: str | None = None,
) -> dict[str, Any]:
    """Execute this manifest in the SDK's enclosed local validation lane.

    Build, posture-bind, execute against a local custody store, and optionally
    replay and reconstruct from that same store. Every one of those happens
    locally and proves only that the manifest is well formed enough to run.

    This is not the canonical lifecycle and cannot stand in for it. Interlock/InTr
    owns transition admission; the Organization owns runtime reality at its ledger
    root; master-records records released organization batch receipts. A local
    replay or reconstruction here is evidence about this lane and nothing else.
    The returned result carries that distinction in its own fields.

    To hand a submission to the receiving Interlock runtime, which is what the SDK
    is for, use ``manifest_external_framework_submission``.
    """
    from . import sovereign_validation_runtime
    from .evaluator_governance_runtime import run_evaluator_governance_manifest

    manifest = prepare_external_framework_manifest(
        data=data,
        source_framework=source_framework,
        source_output_id=source_output_id,
        processor_request=processor_request,
        evaluation_declaration=evaluation_declaration,
        security_posture_request=security_posture_request,
        process=process,
        return_depth=return_depth,
        data_class=data_class,
        source_instance=source_instance,
        created_at=created_at,
    )
    governed_result = run_evaluator_governance_manifest(
        manifest,
        custody_db=custody_db,
        host_identity=host_identity,
        intr_posture_resolver=intr_posture_resolver,
        posture_observed_at=posture_observed_at,
    )
    manifest_receipt_id = governed_result.get("manifest_receipt_id")
    if not isinstance(manifest_receipt_id, str) or not manifest_receipt_id:
        raise RuntimeError("canonical runtime did not return manifest_receipt_id")

    result: dict[str, Any] = {
        "schema": "stegverse.sdk.external-framework-run.v1",
        "status": "EXECUTED",
        "source_framework": source_framework,
        "source_output_id": source_output_id,
        "processing": deepcopy(manifest["processing"]),
        "return_projection": deepcopy(manifest["return_projection"]),
        "manifest_receipt_id": manifest_receipt_id,
        "manifest": manifest,
        "governed_result": governed_result,
        "intr_security_posture_binding": governed_result.get("intr_security_posture_binding"),
        "posture_bound_execution": governed_result.get("posture_bound_execution") is True,
        "execution_performed": True,
        # This lane is enclosed and local. Naming that here is what stops a local
        # replay from being read as canonical closure.
        "lane": "SDK_LOCAL_ENCLOSED_VALIDATION",
        "evidence_class": "SANDBOX_RUNTIME_OBSERVED",
        "canonical_lifecycle_performed": False,
        "intr_admission_observed": False,
        "far_side_transition_observed": False,
        "organization_receipt_observed": False,
        "master_records_reconstruction_observed": False,
        "custody_store_is_local": True,
        "replay_is_local_to_this_custody_store": bool(replay),
        "reconstruction_is_local_to_this_custody_store": bool(reconstruct),
        "may_be_promoted_to_canonical_closure": False,
        "authority_effect": "NONE_ENCLOSED_VALIDATION_ONLY",
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
            "Manifest source-native external-framework data through an installed "
            "StegVerse processor route and hand it to Interlock/InTr. Use "
            "--execute-enclosed to run it in the SDK's local validation lane instead."
        ),
    )
    parser.add_argument("--input", required=True, help="JSON file containing source-native data")
    parser.add_argument("--governance-request", required=True, help="complete governance processor request JSON")
    parser.add_argument("--evaluation-declaration", help="optional preregistered evaluator declaration JSON")
    parser.add_argument(
        "--security-posture-request",
        help=(
            "optional stegverse.sdk.security-posture-request.v1 JSON; the manifesting "
            "default retains it without resolution, and authoritative resolution remains "
            "Interlock/InTr's"
        ),
    )
    parser.add_argument("--source-framework", required=True)
    parser.add_argument("--source-output-id", required=True)
    parser.add_argument("--source-instance")
    parser.add_argument("--data-class")
    parser.add_argument("--process", default="governance", choices=("governance",))
    parser.add_argument("--return-depth", default="result+evidence", choices=sorted(RETURN_DEPTHS))
    parser.add_argument("--created-at")
    parser.add_argument("--posture-observed-at", help="deterministic posture observation time; default current UTC")
    parser.add_argument(
        "--execute-enclosed",
        action="store_true",
        help=(
            "run the manifest in the SDK's enclosed local validation lane against a "
            "local custody store instead of manifesting it for handoff; produces "
            "SANDBOX_RUNTIME_OBSERVED evidence that is never canonical closure"
        ),
    )
    # Manifesting is the default now, so this flag selects what already happens.
    # Retained so existing callers and pipelines keep working.
    parser.add_argument(
        "--prepare-only",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    parser.add_argument("--custody-db", default=DEFAULT_CUSTODY_DB)
    parser.add_argument("--host-identity", default=DEFAULT_HOST_IDENTITY)
    parser.add_argument("--no-replay", action="store_true")
    parser.add_argument("--no-reconstruct", action="store_true")
    parser.add_argument("--output", help="write artifact JSON; default stdout")

    args = parser.parse_args(argv)
    try:
        common = dict(
            data=_load_json(args.input),
            source_framework=args.source_framework,
            source_output_id=args.source_output_id,
            processor_request=_load_json(args.governance_request),
            evaluation_declaration=_load_json(args.evaluation_declaration) if args.evaluation_declaration else None,
            security_posture_request=_load_json(args.security_posture_request) if args.security_posture_request else None,
            process=args.process,
            return_depth=args.return_depth,
            data_class=args.data_class,
            source_instance=args.source_instance,
            created_at=args.created_at,
        )
        if args.execute_enclosed:
            result = run_external_framework(
                **common,
                custody_db=args.custody_db,
                host_identity=args.host_identity,
                replay=not args.no_replay,
                reconstruct=not args.no_reconstruct,
                posture_observed_at=args.posture_observed_at,
            )
        else:
            result = manifest_external_framework_submission(**common)
        _write_json(result, args.output)
        return 0
    except (ValueError, RuntimeError) as exc:
        parser.error(str(exc))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
