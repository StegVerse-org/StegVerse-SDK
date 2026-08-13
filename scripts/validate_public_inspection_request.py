from __future__ import annotations

import json
import sys
from pathlib import Path

FORBIDDEN_KEY_FRAGMENTS = {
    "token", "secret", "password", "private_key", "privatekey", "bearer",
    "credential", "api_key", "apikey", "github_token", "tvc_identity",
    "script", "command", "executable", "workflow", "code"
}
ALLOWED_TOP_LEVEL = {
    "schema_version", "request_id", "requester_label", "case_profile", "input",
    "return_projection", "manifest_labels", "authority_claim", "notes"
}
ALLOWED_PROFILES = {"ordinary", "longitudinal-boundary", "custom-declarative"}
ALLOWED_PROJECTIONS = {"ALL", "SELECTED", "NONE"}


def _walk(value, path="$"):
    if isinstance(value, dict):
        for key, child in value.items():
            lowered = str(key).lower()
            if any(fragment in lowered for fragment in FORBIDDEN_KEY_FRAGMENTS):
                raise ValueError(f"forbidden field at {path}.{key}")
            yield from _walk(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk(child, f"{path}[{index}]")
    elif isinstance(value, str):
        if "-----BEGIN " in value or value.lower().startswith("bearer "):
            raise ValueError(f"credential-like value at {path}")
    yield value


def validate(payload: dict) -> None:
    unknown = set(payload) - ALLOWED_TOP_LEVEL
    if unknown:
        raise ValueError(f"unknown top-level fields: {sorted(unknown)}")
    required = {"schema_version", "request_id", "case_profile", "input", "return_projection", "authority_claim"}
    missing = required - set(payload)
    if missing:
        raise ValueError(f"missing required fields: {sorted(missing)}")
    if payload["schema_version"] != "1.0":
        raise ValueError("unsupported schema_version")
    if payload["authority_claim"] is not False:
        raise ValueError("authority_claim must be false")
    if payload["case_profile"] not in ALLOWED_PROFILES:
        raise ValueError("unsupported case_profile")
    if payload["return_projection"] not in ALLOWED_PROJECTIONS:
        raise ValueError("unsupported return_projection")
    if not isinstance(payload["input"], dict):
        raise ValueError("input must be an object")
    if len(payload["input"]) > 50:
        raise ValueError("input has too many fields")
    label = payload.get("requester_label")
    if label is not None and (not isinstance(label, str) or len(label) > 120):
        raise ValueError("invalid requester_label")
    notes = payload.get("notes")
    if notes is not None and (not isinstance(notes, str) or len(notes) > 2000):
        raise ValueError("invalid notes")
    list(_walk(payload))


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: validate_public_inspection_request.py <request.json>", file=sys.stderr)
        return 2
    path = Path(argv[1])
    payload = json.loads(path.read_text(encoding="utf-8"))
    validate(payload)
    print(f"PASS {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
