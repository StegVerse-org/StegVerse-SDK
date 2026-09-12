"""User/framework-facing builder for canonical StegVerse ingress manifests.

The builder is a construction and validation convenience layer only. It does not
perform governance, diagnostics, infer missing processor evidence, grant authority,
or alter the semantic meaning of a caller's source-native payload.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Mapping

from .ecosystem_diagnostic_runtime import REQUEST_EXTENSION, validate_diagnostic_request
from .governance_navigation import INGRESS_PROFILE, canonical_sha256
from .manifest_contract import validate_ingress_manifest
from .route_resolution import (
    CANONICAL_PRODUCTION_ROUTE_ID,
    ECOSYSTEM_DIAGNOSTIC_ROUTE_ID,
    PUBLISHED_ROUTES,
)

PROCESSOR_ROUTES = {
    "governance": CANONICAL_PRODUCTION_ROUTE_ID,
    "ecosystem_diagnostic": ECOSYSTEM_DIAGNOSTIC_ROUTE_ID,
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
        "transition_classes": ["ingestion", "governance", "consequence", "return_ingestion", "custody"],
    },
    "full-trace": {"mode": "ALL", "transition_classes": []},
    "locator-only": {"mode": "NONE", "transition_classes": []},
}

DIAGNOSTIC_RETURN_DEPTHS = {
    "result-only": {"mode": "SELECTED", "transition_classes": ["diagnostic"]},
    "result+evidence": {"mode": "SELECTED", "transition_classes": ["ingestion", "diagnostic", "custody"]},
    "full-trace": {"mode": "ALL", "transition_classes": []},
    "locator-only": {"mode": "NONE", "transition_classes": []},
}


def available_processors() -> tuple[str, ...]:
    installed = []
    for name, route_id in PROCESSOR_ROUTES.items():
        route = PUBLISHED_ROUTES.get(route_id) or {}
        if route.get("runtime_installed") is True and route.get("processor_capability") == name:
            installed.append(name)
    return tuple(sorted(installed))


def _route_declaration(process: str) -> dict[str, Any]:
    normalized = process.strip().lower()
    route_id = PROCESSOR_ROUTES.get(normalized)
    if route_id is None:
        raise ValueError(
            f"unsupported processing capability {process!r}; installed choices: "
            + ", ".join(available_processors())
        )
    published = PUBLISHED_ROUTES.get(route_id)
    if not published or published.get("runtime_installed") is not True:
        raise ValueError(f"processing capability {normalized!r} has no installed runtime route")
    if published.get("processor_capability") != normalized:
        raise ValueError(f"route {route_id!r} is not bound to processing capability {normalized!r}")
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
        raise ValueError("processor_request is missing required governance fields: " + ", ".join(missing))
    candidate = value.get("candidate")
    if not isinstance(candidate, Mapping):
        raise ValueError("processor_request.candidate must be an object")
    return deepcopy(dict(value))


def _projection_for(process: str, depth_key: str) -> dict[str, Any]:
    source = DIAGNOSTIC_RETURN_DEPTHS if process == "ecosystem_diagnostic" else RETURN_DEPTHS
    if depth_key not in source:
        raise ValueError(f"unsupported return_depth {depth_key!r}; choices: " + ", ".join(sorted(source)))
    return deepcopy(source[depth_key])


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
    if not isinstance(source_framework, str) or not source_framework.strip():
        raise ValueError("source_framework is required")
    if not isinstance(source_output_id, str) or not source_output_id.strip():
        raise ValueError("source_output_id is required")

    normalized_process = process.strip().lower()
    route = _route_declaration(normalized_process)
    extensions: dict[str, Any] = {"stegverse_route": route}
    candidate = None
    hashes: dict[str, Any] = {"payload_sha256": canonical_sha256(data)}

    if normalized_process == "governance":
        normalized_request = _validate_governance_request(processor_request)
        candidate = deepcopy(dict(normalized_request["candidate"]))
        hashes["candidate_sha256"] = canonical_sha256(candidate)
        extensions["stegverse_governance_request"] = normalized_request
    elif normalized_process == "ecosystem_diagnostic":
        normalized_request = validate_diagnostic_request(processor_request)
        extensions[REQUEST_EXTENSION] = normalized_request
    else:
        raise ValueError(f"processing capability {normalized_process!r} has no builder binding")

    depth_key = return_depth.strip().lower()
    return_projection = _projection_for(normalized_process, depth_key)
    timestamp = created_at or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    processing = {"capability": normalized_process, "route_id": route["route_id"]}
    extensions["manifest_builder"] = {
        "profile": "stegverse.manifest-builder.v1",
        "processing_capability": normalized_process,
        "route_id": route["route_id"],
        "return_depth": depth_key,
        "source_semantic_custody": "EXTERNAL",
        "builder_grants_authority": False,
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
        "processing": processing,
        "declared_intent": declared_intent
        or f"Process source-native manifested data through installed {normalized_process} processing.",
        "requested_consequence": requested_consequence
        or "Return the requested StegVerse processing artifact; no caller-authored authority is created.",
        "context_refs": list(context_refs or []),
        "canonicalization_profile": "steggate.jcs.v1",
        "hashes": hashes,
        "attestation": None,
        "extensions": extensions,
        "return_projection": return_projection,
        "manifest_labels": dict(manifest_labels or {"mode": "NONE"}),
    }
    if candidate is not None:
        manifest["candidate"] = candidate

    validate_ingress_manifest(manifest)
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
    parser = argparse.ArgumentParser(prog="stegverse manifest", description="Build canonical StegVerse ingress manifests from source-native data.")
    sub = parser.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build", help="build and validate a canonical ingress manifest")
    build.add_argument("--input", required=True, help="JSON file containing source-native data")
    build.add_argument("--processor-request", help="JSON file containing the complete selected processor request")
    build.add_argument("--governance-request", help="legacy alias for --processor-request when --process=governance")
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
            request_path = args.processor_request or args.governance_request
            if not request_path:
                raise ValueError("--processor-request is required (or --governance-request for governance compatibility)")
            if args.process != "governance" and args.governance_request and not args.processor_request:
                raise ValueError("non-governance processing requires --processor-request")
            manifest = build_manifest(
                data=_load_json(args.input),
                source_framework=args.source_framework,
                source_output_id=args.source_output_id,
                source_instance=args.source_instance,
                data_class=args.data_class,
                processor_request=_load_json(request_path),
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
