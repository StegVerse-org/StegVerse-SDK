"""Execute one validated manifest through its published installed SDK route."""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
from pathlib import Path
from typing import Any, Mapping

from .manifest_contract import validate_ingress_manifest
from .route_resolution import route_from_manifest


_GOVERNED_WORKER_ROUTING_SURFACE = "STEGAGENTS_GOVERNED_RUNTIME"
_LOCAL_SEMANTIC_WORKER_BINDINGS = {
    "stegverse.purpose_bound_worker_processor.execute_manifest",
    "stegverse.atomic_task_worker_processor.execute_manifest",
}
_RESULT_LINEAGE_SCHEMA = "stegverse.sdk.run-manifest-lineage.v1"
_RUN_MANIFEST_REQUEST_SCHEMA = "stegverse.sdk.run-manifest-request.v1"
_RESERVED_LINEAGE_FIELDS = {
    "canonical_manifest_sha256",
    "request_sha256",
    "processor_result_sha256",
    "manifest_lineage",
}


def _canonical_sha256(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _run_manifest_request(
    canonical: Mapping[str, Any], route: Mapping[str, Any], binding: str
) -> dict[str, Any]:
    return {
        "schema": _RUN_MANIFEST_REQUEST_SCHEMA,
        "canonical_manifest_sha256": canonical["canonical_manifest_sha256"],
        "processing_capability": route["processor_capability"],
        "route_id": route["route_id"],
        "route_declaration_hash": route["route_declaration_hash"],
        "runtime_binding": binding,
        "source_framework": canonical["source_framework"],
        "source_instance": canonical.get("source_instance"),
        "source_output_id": canonical["source_output_id"],
        "authority_effect": "NONE_DISPATCH_BINDING_ONLY",
    }


def _bind_result_lineage(
    *,
    canonical: Mapping[str, Any],
    route: Mapping[str, Any],
    binding: str,
    processor_result: Mapping[str, Any],
) -> dict[str, Any]:
    raw_result = dict(processor_result)
    request = _run_manifest_request(canonical, route, binding)
    request_sha256 = _canonical_sha256(request)
    processor_result_sha256 = _canonical_sha256(raw_result)

    conflicting = sorted(_RESERVED_LINEAGE_FIELDS.intersection(raw_result))
    preserved_processor_request_sha256 = None
    if "canonical_manifest_sha256" in conflicting:
        if raw_result.get("canonical_manifest_sha256") != canonical["canonical_manifest_sha256"]:
            raise ValueError("processor result conflicts with canonical_manifest_sha256")
        conflicting.remove("canonical_manifest_sha256")
    if "request_sha256" in conflicting:
        preserved_processor_request_sha256 = raw_result.get("request_sha256")
        conflicting.remove("request_sha256")
    if conflicting:
        raise ValueError("processor result uses reserved run-manifest lineage fields: " + ", ".join(conflicting))

    bound = dict(raw_result)
    if preserved_processor_request_sha256 is not None:
        bound["processor_request_sha256"] = preserved_processor_request_sha256
    bound["canonical_manifest_sha256"] = canonical["canonical_manifest_sha256"]
    bound["request_sha256"] = request_sha256
    bound["processor_result_sha256"] = processor_result_sha256
    bound["manifest_lineage"] = {
        "schema": _RESULT_LINEAGE_SCHEMA,
        "canonical_manifest_sha256": canonical["canonical_manifest_sha256"],
        "request_sha256": request_sha256,
        "processor_result_sha256": processor_result_sha256,
        "run_manifest_request": request,
        "processor_request_sha256": preserved_processor_request_sha256,
    }
    return bound


def _require_nonterminal_local_semantic_boundary(route: Mapping[str, Any], binding: str) -> None:
    """Prevent SDK-local semantic demonstrations from satisfying governed completion.

    Worker routes are declared against the existing StegAgents governed runtime.
    The local semantic processors remain useful as deterministic source/contract
    fixtures, but they are not WorkerCoordinator/InTr/Master Records execution and
    therefore cannot be the terminal implementation behind public run-manifest.
    """
    if (
        route.get("routing_surface") == _GOVERNED_WORKER_ROUTING_SURFACE
        and binding in _LOCAL_SEMANTIC_WORKER_BINDINGS
    ):
        raise ValueError(
            "AUTHENTIC_GOVERNED_RUNTIME_BINDING_REQUIRED: "
            "SDK-local semantic worker processor cannot satisfy run-manifest completion"
        )


def execute_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    canonical = validate_ingress_manifest(manifest)
    route = route_from_manifest(canonical)
    binding = route.get("runtime_binding")
    if not isinstance(binding, str) or "." not in binding:
        raise ValueError("installed route does not expose an executable runtime binding")
    _require_nonterminal_local_semantic_boundary(route, binding)
    module_name, function_name = binding.rsplit(".", 1)
    if not module_name.startswith("stegverse."):
        raise ValueError("runtime binding must resolve inside the installed StegVerse SDK")
    module = importlib.import_module(module_name)
    function = getattr(module, function_name, None)
    if not callable(function):
        raise ValueError(f"installed runtime binding is not callable: {binding}")
    result = function(manifest)
    if not isinstance(result, Mapping):
        raise ValueError("manifest processor returned a non-object result")
    return _bind_result_lineage(
        canonical=canonical,
        route=route,
        binding=binding,
        processor_result=result,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="stegverse run-manifest",
        description="Execute one canonical SDK manifest through its declared installed processor route.",
    )
    parser.add_argument("--manifest", required=True, help="canonical manifest JSON produced by Manifest Builder")
    parser.add_argument("--output", help="write result JSON; default stdout")
    args = parser.parse_args(argv)
    try:
        manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
        result = execute_manifest(manifest)
    except (OSError, json.JSONDecodeError, ValueError, ImportError, AttributeError) as exc:
        parser.error(str(exc))
    text = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
