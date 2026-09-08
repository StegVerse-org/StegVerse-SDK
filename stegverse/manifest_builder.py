"""User/framework-facing builder for canonical StegVerse ingress manifests.

The builder is a construction and validation convenience layer only. It does not
perform governance, infer missing governance evidence, grant authority, or alter
the semantic meaning of a caller's source-native payload.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Mapping

from .governance_navigation import (
    INGRESS_PROFILE,
    canonical_sha256,
    validate_external_manifest,
)
from .route_resolution import (
    CANONICAL_PRODUCTION_ROUTE_ID,
    PUBLISHED_ROUTES,
)

PROCESSOR_ROUTES = {
    "governance": CANONICAL_PRODUCTION_ROUTE_ID,
}

GOVERNANCE_REQUEST_FIELDS = (
    "candidate",
    "judgment",
    "signal",
    "execution",
    "capability",
    "continuity",
    "approval",
    "permission_present",
)

RETURN_DEPTHS = {
    "result-only": {"mode": "SELECTED", "transition_classes": ["governance"]},
    "result+evidence": {
        "mode": "SELECTED",
        "transition_classes": [
            "ingestion",
            "governance",
            "consequence",
            "return_ingestion",
            "custody",
        ],
    },
    "full-trace": {"mode": "ALL", "transition_classes": []},
    "locator-only": {"mode": "NONE", "transition_classes": []},
}


def available_processors() -> tuple[str, ...]:
    """Return processor names whose declared route is currently installed."""
    installed = []
    for name, route_id in PROCESSOR_ROUTES.items():
        route = PUBLISHED_ROUTES.get(route_id) or {}
        if route.get("runtime_installed") is True:
            installed.append(name)
    return tuple(sorted(installed))


def _route_declaration(process: str) -> dict[str, Any]:
    normalized = process.strip().lower()
    route_id = PROCESSOR_ROUTES.get(normalized)
    if route_id is None:
        raise ValueError(
            f"unsupported processing class {process!r}; installed choices: "
            + ", ".join(available_processors())
        )
    published = PUBLISHED_ROUTES.get(route_id)
    if not published or published.get("runtime_installed") is not True:
        raise ValueError(f"processing class {normalized!r} has no installed runtime route")
    return {
        "route_id": published["route_id"],
        "lane_class": published["lane_class"],
        "routing_surface": published["routing_surface"],
        "containment": published["containment"],
        "sandbox_required": published["sandbox_required"],
        "external_consequence_enabled": published["external_consequence_enabled"],
    }


def _validate_governance_request(value: Mapping[str, Any] | None) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(
            "governance processing requires a complete processor_request object; "
            "the Manifest Builder does not synthesize governance evidence"
        )
    missing = [field for field in GOVERNANCE_REQUEST_FIELDS if field not in value]
    if missing:
        raise ValueError(
            "processor_request is missing required governance fields: " + ", ".join(missing)
        )
    candidate = value.get("candidate")
    if not isinstance(candidate, Mapping):
        raise ValueError("processor_request.candidate must be an object")
    return deepcopy(dict(value))


def build_manifest(
    *,
    data: Any,
    source_framework: str,
    source_output_id: str,
    processor_request: Mapping[str, Any],
    process: str = "governance",
    return_depth: str = "result+evidence",
    data_class: str | None = None,
    source_instance: str | None = None,
    created_at: str | None = None,
    context_refs: list[str] | None = None,
    declared_intent: str | None = None,
    requested_consequence: str | None = None,
    manifest_labels: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a validated `stegverse.ingress-manifest.v1` object.

    `data` remains the source-native payload. `processor_request` is separate and
    must already contain the complete processor-specific evidence required by the
    selected processing class. No missing judgment, signal, execution, capability,
    continuity, approval, or permission state is inferred by this function.
    """
    if not isinstance(source_framework, str) or not source_framework.strip():
        raise ValueError("source_framework is required")
    if not isinstance(source_output_id, str) or not source_output_id.strip():
        raise ValueError("source_output_id is required")

    normalized_process = process.strip().lower()
    if normalized_process != "governance":
        # Keep this explicit as new processors are registered rather than silently
        # reusing governance semantics for foreign processing classes.
        _route_declaration(normalized_process)
        raise ValueError(f"processing class {normalized_process!r} has no builder binding")

    governance_request = _validate_governance_request(processor_request)
    candidate = deepcopy(dict(governance_request["candidate"]))

    depth_key = return_depth.strip().lower()
    if depth_key not in RETURN_DEPTHS:
        raise ValueError(
            f"unsupported return_depth {return_depth!r}; choices: "
            + ", ".join(sorted(RETURN_DEPTHS))
        )

    timestamp = created_at or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    route = _route_declaration(normalized_process)
    extensions: dict[str, Any] = {
        "stegverse_route": route,
        "stegverse_governance_request": governance_request,
        "manifest_builder": {
            "profile": "stegverse.manifest-builder.v1",
            "processing_class": normalized_process,
            "return_depth": depth_key,
            "source_semantic_custody": "EXTERNAL",
            "builder_grants_authority": False,
        },
    }
    if data_class is not None:
        if not isinstance(data_class, str) or not data_class.strip():
            raise ValueError("data_class must be a non-empty string when supplied")
        extensions["source_data_class"] = data_class.strip()

    manifest: dict[str, Any] = {
        "manifest_profile": INGRESS_PROFILE,
        "manifest_profile_version": "1",
        "source_framework": source_framework.strip(),
        "source_instance": source_instance,
        "source_output_id": source_output_id.strip(),
        "created_at": timestamp,
        "freshness": {},
        "payload": deepcopy(data),
        "candidate": candidate,
        "declared_intent": declared_intent
        or f"Process source-native manifested data through installed {normalized_process} processing.",
        "requested_consequence": requested_consequence
        or "Return the requested StegVerse processing artifact; no caller-authored authority is created.",
        "context_refs": list(context_refs or []),
        "canonicalization_profile": "steggate.jcs.v1",
        "hashes": {
            "payload_sha256": canonical_sha256(data),
            "candidate_sha256": canonical_sha256(candidate),
        },
        "attestation": None,
        "extensions": extensions,
        "return_projection": deepcopy(RETURN_DEPTHS[depth_key]),
        "manifest_labels": dict(manifest_labels or {"mode": "NONE"}),
    }

    # Validate using the same canonical 0B validator that execution will use.
    # Discard its enriched internal representation and return the external ingress
    # object, which remains valid for later 0B submission.
    validate_external_manifest(manifest)
    return manifest


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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="stegverse manifest",
        description="Build canonical StegVerse ingress manifests from source-native data.",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build", help="build and validate a canonical ingress manifest")
    build.add_argument("--input", required=True, help="JSON file containing source-native data")
    build.add_argument(
        "--governance-request",
        required=True,
        help="JSON file containing the complete processor-specific governance request",
    )
    build.add_argument("--source-framework", required=True)
    build.add_argument("--source-output-id", required=True)
    build.add_argument("--source-instance")
    build.add_argument("--data-class")
    build.add_argument("--process", default="governance", choices=sorted(PROCESSOR_ROUTES))
    build.add_argument("--return-depth", default="result+evidence", choices=sorted(RETURN_DEPTHS))
    build.add_argument("--created-at")
    build.add_argument("--output", help="write manifest JSON to this path; default stdout")

    args = parser.parse_args(argv)
    if args.command == "build":
        try:
            manifest = build_manifest(
                data=_load_json(args.input),
                source_framework=args.source_framework,
                source_output_id=args.source_output_id,
                source_instance=args.source_instance,
                data_class=args.data_class,
                processor_request=_load_json(args.governance_request),
                process=args.process,
                return_depth=args.return_depth,
                created_at=args.created_at,
            )
            _write_json(manifest, args.output)
            return 0
        except ValueError as exc:
            parser.error(str(exc))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
