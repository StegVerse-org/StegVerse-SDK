"""Transport helpers for governed-vs-recursive comparison packages.

The SDK prepares requests, submits them to an explicitly configured endpoint,
and validates returned envelopes. Transport does not grant runtime authority.
"""

from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional

import requests

from .llm_route_comparison import (
    ComparisonRequest,
    ComparisonValidationError,
    RouteResult,
    build_comparison_package,
    build_comparison_receipt,
    stable_hash,
)

TRANSPORT_SCHEMA_VERSION = "1.0.0"


class ComparisonTransportError(RuntimeError):
    """Raised when transport or returned-envelope validation fails."""


def _json_mapping(value: Any, *, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ComparisonTransportError(f"{label} must be a JSON object")
    return value


def build_transport_envelope(request: ComparisonRequest) -> Dict[str, Any]:
    """Wrap a validated comparison package for transport."""

    package = build_comparison_package(request)
    envelope: Dict[str, Any] = {
        "transport_schema_version": TRANSPORT_SCHEMA_VERSION,
        "message_type": "LLM_ROUTE_COMPARISON_REQUEST",
        "comparison_id": request.comparison_id,
        "package": package,
        "invariants": {
            "transport_is_execution_authority": False,
            "transport_is_admissibility": False,
            "receiver_must_return_same_comparison_id": True,
        },
    }
    envelope["envelope_sha256"] = stable_hash(envelope)
    return envelope


def validate_return_envelope(
    request: ComparisonRequest,
    envelope: Mapping[str, Any],
) -> Dict[str, Any]:
    """Validate an executor response and emit the canonical comparison receipt."""

    if envelope.get("message_type") != "LLM_ROUTE_COMPARISON_RESULT":
        raise ComparisonTransportError("unexpected comparison result message_type")
    if envelope.get("comparison_id") != request.comparison_id:
        raise ComparisonTransportError("comparison_id changed across transport")

    raw_results = envelope.get("route_results")
    if not isinstance(raw_results, list):
        raise ComparisonTransportError("route_results must be a list")

    results = []
    for raw in raw_results:
        item = _json_mapping(raw, label="route result")
        results.append(
            RouteResult(
                route_id=str(item.get("route_id", "")),
                task_identity=str(item.get("task_identity", "")),
                output_sha256=str(item.get("output_sha256", "")),
                metrics=_json_mapping(item.get("metrics", {}), label="metrics"),
                admissibility_result=str(item.get("admissibility_result", "")),
                receipt_refs=list(item.get("receipt_refs", [])),
                warnings=list(item.get("warnings", [])),
            )
        )

    return build_comparison_receipt(request, results)


def submit_comparison(
    request: ComparisonRequest,
    endpoint: str,
    *,
    timeout_seconds: float = 60.0,
    headers: Optional[Mapping[str, str]] = None,
) -> Dict[str, Any]:
    """POST a comparison envelope and validate the returned result envelope."""

    if not endpoint.startswith(("http://", "https://")):
        raise ComparisonTransportError("endpoint must use http:// or https://")

    try:
        response = requests.post(
            endpoint,
            json=build_transport_envelope(request),
            headers=dict(headers or {}),
            timeout=timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        raise ComparisonTransportError(f"comparison transport failed: {exc}") from exc
    except ValueError as exc:
        raise ComparisonTransportError("comparison endpoint returned invalid JSON") from exc

    return validate_return_envelope(request, _json_mapping(payload, label="response"))


def export_json(payload: Mapping[str, Any], destination: str | Path) -> Path:
    """Write canonical, stable JSON for package or receipt exchange."""

    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return path


def import_json(source: str | Path) -> Dict[str, Any]:
    """Load a JSON object from disk."""

    path = Path(source)
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ComparisonTransportError(f"unable to load JSON from {path}: {exc}") from exc
    return dict(_json_mapping(value, label="imported JSON"))
