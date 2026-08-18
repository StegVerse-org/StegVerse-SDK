"""Neutral public-inspection adapter for the ordinary SDK governance path."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from .governance_navigation import build_raw_submission_descriptor

REQUEST_SCHEMA_VERSION = "1.0"
REQUEST_PROFILES = {"ordinary", "longitudinal-boundary", "custom-declarative"}
RETURN_PROJECTIONS = {"ALL", "SELECTED", "NONE"}
LANE_CLASSES = {"PRODUCTION_VALIDATION", "ENCLOSED_DEMO_TEST"}
SUPPORTED_EVALUATION_CAPABILITIES = {
    "commit_time_admissibility",
    "bounded_consequence",
    "master_records_custody",
    "replay",
    "reconstruction",
}
SUPPORTED_EVIDENCE_CLASSES = {
    "governance_decision",
    "execution_observation",
    "manifest_receipt",
    "route_receipts",
    "exact_run_custody",
    "replay",
    "reconstruction",
}
FORBIDDEN_KEY_FRAGMENTS = {
    "token", "secret", "password", "private_key", "privatekey", "bearer",
    "credential", "api_key", "apikey", "github_token", "tvc_identity",
    "script", "command", "executable", "workflow", "code",
}
ALLOWED_TOP_LEVEL = {
    "schema_version", "request_id", "requester_label", "case_profile",
    "evaluation_declaration", "execution_provenance", "input", "return_projection",
    "manifest_labels", "authority_claim", "notes",
}


class PublicInspectionRequestError(ValueError):
    pass


def _walk(value: Any, path: str = "$") -> None:
    if isinstance(value, Mapping):
        for raw_key, child in value.items():
            lowered = str(raw_key).lower()
            if any(fragment in lowered for fragment in FORBIDDEN_KEY_FRAGMENTS):
                raise PublicInspectionRequestError(f"forbidden field at {path}.{raw_key}")
            _walk(child, f"{path}.{raw_key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _walk(child, f"{path}[{index}]")
    elif isinstance(value, str):
        if "-----BEGIN " in value or value.lower().startswith("bearer "):
            raise PublicInspectionRequestError(f"credential-like value at {path}")


def _bounded_text(value: Any, field: str, maximum: int, *, required: bool = False) -> str | None:
    if value is None and not required:
        return None
    if not isinstance(value, str) or (required and not value.strip()) or len(value) > maximum:
        raise PublicInspectionRequestError(f"invalid {field}")
    return value


def _validate_string_set(value: Any, field: str, supported: set[str], maximum: int) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or len(value) > maximum or len(value) != len(set(value)):
        raise PublicInspectionRequestError(f"invalid {field}")
    unsupported = [item for item in value if not isinstance(item, str) or item not in supported]
    if unsupported:
        raise PublicInspectionRequestError(
            f"unsupported {field}: " + ", ".join(str(item) for item in unsupported)
        )
    return list(value)


def _validate_evaluation_declaration(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise PublicInspectionRequestError("evaluation_declaration must be an object")
    allowed = {
        "what", "how", "why", "expected_observation", "requested_capabilities",
        "requested_evidence",
    }
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise PublicInspectionRequestError("unknown evaluation_declaration fields: " + ", ".join(unknown))
    missing = sorted({"what", "how", "why"} - set(value))
    if missing:
        raise PublicInspectionRequestError("missing evaluation_declaration fields: " + ", ".join(missing))
    return {
        "what": _bounded_text(value.get("what"), "evaluation_declaration.what", 1000, required=True),
        "how": _bounded_text(value.get("how"), "evaluation_declaration.how", 1000, required=True),
        "why": _bounded_text(value.get("why"), "evaluation_declaration.why", 1000, required=True),
        "expected_observation": _bounded_text(
            value.get("expected_observation"), "evaluation_declaration.expected_observation", 1000
        ),
        "requested_capabilities": _validate_string_set(
            value.get("requested_capabilities"),
            "evaluation_declaration.requested_capabilities",
            SUPPORTED_EVALUATION_CAPABILITIES,
            5,
        ),
        "requested_evidence": _validate_string_set(
            value.get("requested_evidence"),
            "evaluation_declaration.requested_evidence",
            SUPPORTED_EVIDENCE_CLASSES,
            7,
        ),
    }


def _validate_sha256_hex(value: Any, field: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value.lower()):
        raise PublicInspectionRequestError(f"invalid {field}")
    return value.lower()


def _validate_execution_provenance(value: Any) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise PublicInspectionRequestError("execution_provenance must be an object")
    allowed = {
        "route_id", "route_declaration_hash", "state_binding_hash",
        "lane_class", "routing_surface", "containment", "sandbox_required",
        "sandbox_tier", "origin_surface", "external_consequence_enabled",
        "execution_host_class", "execution_host_identity", "third_party_host_required",
    }
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise PublicInspectionRequestError("unknown execution_provenance fields: " + ", ".join(unknown))
    required = {"lane_class", "routing_surface", "containment", "sandbox_required", "external_consequence_enabled"}
    missing = sorted(required - set(value))
    if missing:
        raise PublicInspectionRequestError("missing execution_provenance fields: " + ", ".join(missing))
    lane = value.get("lane_class")
    if lane not in LANE_CLASSES:
        raise PublicInspectionRequestError("unsupported execution_provenance.lane_class")
    route_id = value.get("route_id")
    if route_id is not None and (not isinstance(route_id, str) or not route_id.strip() or len(route_id) > 200):
        raise PublicInspectionRequestError("invalid execution_provenance.route_id")
    _validate_sha256_hex(value.get("route_declaration_hash"), "execution_provenance.route_declaration_hash")
    _validate_sha256_hex(value.get("state_binding_hash"), "execution_provenance.state_binding_hash")
    if not isinstance(value.get("sandbox_required"), bool) or not isinstance(value.get("external_consequence_enabled"), bool):
        raise PublicInspectionRequestError("execution_provenance boolean fields are invalid")
    if value.get("external_consequence_enabled") is not False:
        raise PublicInspectionRequestError("public inspection validation cannot enable external consequence")
    if lane == "PRODUCTION_VALIDATION":
        if value.get("routing_surface") != "CANONICAL_PRODUCTION":
            raise PublicInspectionRequestError("PRODUCTION_VALIDATION requires CANONICAL_PRODUCTION routing")
        if value.get("containment") != "PRODUCTION_ROUTE_BOUNDED_CONSEQUENCE":
            raise PublicInspectionRequestError("PRODUCTION_VALIDATION containment is invalid")
    else:
        if value.get("routing_surface") != "DEMO_TEST_REPOSITORY":
            raise PublicInspectionRequestError("ENCLOSED_DEMO_TEST requires DEMO_TEST_REPOSITORY routing")
        if value.get("containment") != "DEMO_REPOSITORY_CONTAINED" or value.get("sandbox_required") is not True:
            raise PublicInspectionRequestError("ENCLOSED_DEMO_TEST containment is invalid")
    normalized = dict(value)
    if normalized.get("route_declaration_hash") is not None:
        normalized["route_declaration_hash"] = str(normalized["route_declaration_hash"]).lower()
    if normalized.get("state_binding_hash") is not None:
        normalized["state_binding_hash"] = str(normalized["state_binding_hash"]).lower()
    return normalized


def validate_public_inspection_request(request: Mapping[str, Any]) -> dict[str, Any]:
    unknown = sorted(set(request) - ALLOWED_TOP_LEVEL)
    if unknown:
        raise PublicInspectionRequestError("unknown request fields: " + ", ".join(unknown))
    required = {
        "schema_version", "request_id", "case_profile", "execution_provenance",
        "input", "return_projection", "authority_claim",
    }
    missing = sorted(required - set(request))
    if missing:
        raise PublicInspectionRequestError("missing required fields: " + ", ".join(missing))
    if request.get("schema_version") != REQUEST_SCHEMA_VERSION:
        raise PublicInspectionRequestError("schema_version must be 1.0")
    request_id = request.get("request_id")
    if not isinstance(request_id, str) or not (3 <= len(request_id) <= 80):
        raise PublicInspectionRequestError("request_id must be a 3-80 character string")
    if not all(ch.isalnum() or ch in "._-" for ch in request_id):
        raise PublicInspectionRequestError("request_id contains unsupported characters")
    label = request.get("requester_label")
    if label is not None and (not isinstance(label, str) or len(label) > 120):
        raise PublicInspectionRequestError("invalid requester_label")
    if request.get("case_profile") not in REQUEST_PROFILES:
        raise PublicInspectionRequestError("unsupported case_profile")
    declaration = _validate_evaluation_declaration(request.get("evaluation_declaration"))
    provenance = _validate_execution_provenance(request.get("execution_provenance"))
    input_data = request.get("input")
    if not isinstance(input_data, Mapping):
        raise PublicInspectionRequestError("input must be an object")
    if len(input_data) > 50:
        raise PublicInspectionRequestError("input has too many fields")
    if request.get("return_projection") not in RETURN_PROJECTIONS:
        raise PublicInspectionRequestError("unsupported return_projection")
    labels = request.get("manifest_labels", False)
    if not isinstance(labels, bool):
        raise PublicInspectionRequestError("manifest_labels must be boolean")
    if request.get("authority_claim") is not False:
        raise PublicInspectionRequestError("authority_claim must be false")
    notes = request.get("notes")
    if notes is not None and (not isinstance(notes, str) or len(notes) > 2000):
        raise PublicInspectionRequestError("invalid notes")
    _walk(request)
    normalized = dict(request)
    normalized["evaluation_declaration"] = declaration
    normalized["execution_provenance"] = provenance
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
        "evaluation_declaration": normalized["evaluation_declaration"],
        "execution_provenance": normalized["execution_provenance"],
        "ordinary_governance_option": "0A",
        "submission_descriptor": descriptor,
        "payload": dict(normalized["input"]),
        "notes": normalized["notes"],
        "testing_contract": {
            "configuration_not_augmentation": True,
            "route_augmentation_permitted": False,
            "evaluator_identity_is_decision_input": False,
            "declared_expected_observation_is_decision_input": False,
            "unsupported_capability_behavior": "REJECT_BEFORE_EXECUTION",
        },
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
    parser = argparse.ArgumentParser(prog="python -m stegverse.public_inspection")
    parser.add_argument("request")
    args = parser.parse_args(argv)
    try:
        prepared = prepare_public_inspection_submission(load_public_inspection_request(args.request))
    except PublicInspectionRequestError as exc:
        print(f"ERROR: {exc}")
        return 2
    print(json.dumps(prepared, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
