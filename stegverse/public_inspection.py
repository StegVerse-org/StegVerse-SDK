"""Neutral public-inspection request adapter for the ordinary SDK governance path.

A public pull request is only a visible request/discussion carrier. This module
validates the bounded declarative request and converts it into the same raw-data
submission descriptor used by option 0A. It does not execute the request, grant
authority, select credentials, or claim Master Records custody.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from .governance_navigation import build_raw_submission_descriptor

REQUEST_SCHEMA_VERSION = "1.0"
REQUEST_PROFILES = {"ordinary", "longitudinal-boundary", "custom-declarative"}
RETURN_PROJECTIONS = {"ALL", "SELECTED", "NONE"}
_FORBIDDEN_KEY_PARTS = (
    "token", "secret", "password", "private_key", "privatekey", "api_key",
    "apikey", "credential", "bearer", "command", "shell", "executable",
    "workflow", "github_token", "tvc", "trustvault",
)


class PublicInspectionRequestError(ValueError):
    """Raised when a public inspection request violates the bounded contract."""


def _walk_forbidden(value: Any, path: str = "$") -> None:
    if isinstance(value, Mapping):
        for raw_key, child in value.items():
            key = str(raw_key).lower().replace("-", "_")
            if any(part in key for part in _FORBIDDEN_KEY_PARTS):
                raise PublicInspectionRequestError(
                    f"forbidden credential/executable-style field at {path}.{raw_key}"
                )
            _walk_forbidden(child, f"{path}.{raw_key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _walk_forbidden(child, f"{path}[{index}]")


def validate_public_inspection_request(request: Mapping[str, Any]) -> dict[str, Any]:
    allowed = {
        "schema_version", "request_id", "requester_label", "case_profile",
        "input", "return_projection", "manifest_labels", "authority_claim", "notes",
    }
    unknown = sorted(set(request) - allowed)
    if unknown:
        raise PublicInspectionRequestError("unknown request fields: " + ", ".join(unknown))
    if request.get("schema_version") != REQUEST_SCHEMA_VERSION:
        raise PublicInspectionRequestError("schema_version must be 1.0")
    request_id = request.get("request_id")
    if not isinstance(request_id, str) or not (3 <= len(request_id) <= 80):
        raise PublicInspectionRequestError("request_id must be a 3-80 character string")
    if not all(ch.isalnum() or ch in "._-" for ch in request_id):
        raise PublicInspectionRequestError("request_id contains unsupported characters")
    label = request.get("requester_label")
    if label is not None and (not isinstance(label, str) or len(label) > 120):
        raise PublicInspectionRequestError("requester_label must be a string no longer than 120 characters")
    if request.get("case_profile") not in REQUEST_PROFILES:
        raise PublicInspectionRequestError("unsupported case_profile")
    input_data = request.get("input")
    if not isinstance(input_data, Mapping):
        raise PublicInspectionRequestError("input must be an object")
    if len(input_data) > 50:
        raise PublicInspectionRequestError("input may contain at most 50 top-level properties")
    if request.get("return_projection") not in RETURN_PROJECTIONS:
        raise PublicInspectionRequestError("return_projection must be ALL, SELECTED, or NONE")
    labels = request.get("manifest_labels", False)
    if not isinstance(labels, bool):
        raise PublicInspectionRequestError("manifest_labels must be boolean")
    if request.get("authority_claim") is not False:
        raise PublicInspectionRequestError("authority_claim must be false")
    notes = request.get("notes")
    if notes is not None and (not isinstance(notes, str) or len(notes) > 2000):
        raise PublicInspectionRequestError("notes must be a string no longer than 2000 characters")
    _walk_forbidden(input_data)
    normalized = dict(request)
    normalized.setdefault("manifest_labels", False)
    normalized.setdefault("requester_label", None)
    normalized.setdefault("notes", None)
    return normalized


def prepare_public_inspection_submission(request: Mapping[str, Any]) -> dict[str, Any]:
    normalized = validate_public_inspection_request(request)
    request_id = normalized["request_id"]
    descriptor = build_raw_submission_descriptor(
        source="stegverse-sdk:public-inspection",
        subject=f"public-inspection:{request_id}",
        return_projection={"mode": normalized["return_projection"]},
        manifest_labels={"mode": "ALL" if normalized["manifest_labels"] else "NONE"},
    )
    return {
        "schema": "stegverse.public-inspection-submission.v1",
        "request_id": request_id,
        "requester_label": normalized["requester_label"],
        "case_profile": normalized["case_profile"],
        "ordinary_governance_option": "0A",
        "submission_descriptor": descriptor,
        "payload": dict(normalized["input"]),
        "notes": normalized["notes"],
        "public_pr_is_submission_record_only": True,
        "trusted_processor_required": True,
        "runtime_processing_status": "NOT_RUN",
        "master_records_custody_status": "NOT_CLAIMED",
        "manifest_receipt_id": None,
        "authority_claim": False,
        "github_grants_runtime_authority": False,
    }


def load_public_inspection_request(path: str | Path) -> dict[str, Any]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError as exc:
        raise PublicInspectionRequestError(f"unable to read request: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise PublicInspectionRequestError(f"request is not valid JSON: {exc}") from exc
    if not isinstance(value, Mapping):
        raise PublicInspectionRequestError("request must contain a JSON object")
    return validate_public_inspection_request(value)


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        prog="python -m stegverse.public_inspection",
        description="Validate and prepare a public inspection request for ordinary option 0A governance",
    )
    parser.add_argument("request", help="path to a public inspection request JSON document")
    args = parser.parse_args(argv)
    try:
        request = load_public_inspection_request(args.request)
        prepared = prepare_public_inspection_submission(request)
    except PublicInspectionRequestError as exc:
        print(f"ERROR: {exc}")
        return 2
    print(json.dumps(prepared, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
