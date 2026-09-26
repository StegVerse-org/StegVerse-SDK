"""Provider-neutral, non-authorizing source observation validation.

This checks *declared* attribution and chronology before an evaluator submits
source-native observations through an existing installed SDK processor. It does
not authenticate a provider, invoke an API, make a governance decision, or
substitute for custody / Interlock/InTr.
"""
from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
import hashlib
import json
from typing import Any

PROFILE = "stegverse.source-observation.v1"
OUTCOMES = frozenset({
    "NO_INVOCATION", "COMPLETED_EMPTY_RESPONSE", "TEXT_ELLIPSIS",
    "TEXT_RESPONSE", "REFUSAL_TEXT", "API_ERROR",
    "CLIENT_TIMEOUT", "UNKNOWN_COMPLETION",
})
PROVIDER_OUTPUTS = frozenset({
    "COMPLETED_EMPTY_RESPONSE", "TEXT_ELLIPSIS", "TEXT_RESPONSE",
    "REFUSAL_TEXT",
})
CLIENT_NONRESULTS = frozenset({"NO_INVOCATION", "CLIENT_TIMEOUT", "UNKNOWN_COMPLETION"})
ALLOWED_TOP = frozenset({"profile", "experiment_id", "events"})
ALLOWED_EVENT = frozenset({
    "event_id", "condition_id", "predecessor_id", "source_class",
    "request_sent", "outcome", "prompt", "raw_output", "client_started_at",
    "client_ended_at", "provider_request_id", "api_status",
    "annotation", "evidence_refs",
})


class SourceObservationError(ValueError):
    """One precise, correctable local input violation (not an InTr DENY)."""

    def __init__(self, code: str, event_id: str = ""):
        self.code = code
        self.event_id = event_id
        super().__init__(f"{code}" + (f":{event_id}" if event_id else ""))


def _text(v: Any) -> bool:
    return isinstance(v, str) and bool(v.strip())


def _hash(v: Any) -> str:
    return hashlib.sha256(
        json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def validate_source_observation(value: Any) -> dict[str, Any]:
    """Validate the original object unchanged; never add missing model output."""
    if not isinstance(value, Mapping):
        raise SourceObservationError("SOURCE_OBSERVATION_OBJECT_REQUIRED")
    if value.get("profile") != PROFILE:
        raise SourceObservationError("UNSUPPORTED_SOURCE_OBSERVATION_PROFILE")
    if set(value) - ALLOWED_TOP:
        raise SourceObservationError("UNKNOWN_SOURCE_OBSERVATION_FIELDS")
    if not _text(value.get("experiment_id")):
        raise SourceObservationError("EXPERIMENT_ID_REQUIRED")
    events = value.get("events")
    if not isinstance(events, list) or not events:
        raise SourceObservationError("SOURCE_EVENTS_REQUIRED")
    seen: set[str] = set()
    for event in events:
        if not isinstance(event, Mapping):
            raise SourceObservationError("SOURCE_EVENT_OBJECT_REQUIRED")
        if set(event) - ALLOWED_EVENT:
            raise SourceObservationError("UNKNOWN_SOURCE_EVENT_FIELDS")
        eid = event.get("event_id")
        if not _text(eid):
            raise SourceObservationError("SOURCE_EVENT_ID_REQUIRED")
        if eid in seen:
            raise SourceObservationError("DUPLICATE_SOURCE_EVENT_ID", eid)
        predecessor = event.get("predecessor_id")
        if predecessor is not None and predecessor not in seen:
            raise SourceObservationError("PREDECESSOR_NOT_PREVIOUSLY_RECORDED", eid)
        seen.add(eid)
        outcome = event.get("outcome")
        if outcome not in OUTCOMES:
            raise SourceObservationError("UNSUPPORTED_SOURCE_OUTCOME", eid)
        if event.get("source_class") not in {"CLIENT", "PROVIDER"}:
            raise SourceObservationError("SOURCE_CLASS_REQUIRED", eid)
        if not isinstance(event.get("request_sent"), bool):
            raise SourceObservationError("REQUEST_SENT_BOOLEAN_REQUIRED", eid)
        if not _text(event.get("condition_id")):
            raise SourceObservationError("CONDITION_ID_REQUIRED", eid)
        if not _text(event.get("client_started_at")):
            raise SourceObservationError("CLIENT_START_TIMESTAMP_REQUIRED", eid)
        end = event.get("client_ended_at")
        if end is not None and not _text(end):
            raise SourceObservationError("INVALID_CLIENT_END_TIMESTAMP", eid)
        refs = event.get("evidence_refs", [])
        if not isinstance(refs, list) or any(not _text(x) for x in refs):
            raise SourceObservationError("INVALID_SOURCE_EVIDENCE_REFS", eid)
        if event.get("annotation") is not None and not _text(event["annotation"]):
            raise SourceObservationError("INVALID_HUMAN_ANNOTATION", eid)
        if outcome == "NO_INVOCATION":
            if event["request_sent"] or event["source_class"] != "CLIENT":
                raise SourceObservationError("NO_INVOCATION_MUST_BE_CLIENT_ONLY", eid)
            if any(x in event for x in ("raw_output", "provider_request_id", "api_status", "prompt")):
                raise SourceObservationError("NO_INVOCATION_CANNOT_HAVE_PROVIDER_FIELDS", eid)
            if end is None:
                raise SourceObservationError("NO_INVOCATION_WINDOW_END_REQUIRED", eid)
        else:
            if not event["request_sent"] or not _text(event.get("prompt")):
                raise SourceObservationError("INVOKED_OUTCOME_REQUIRES_EXACT_PROMPT", eid)
            if outcome in PROVIDER_OUTPUTS:
                if event["source_class"] != "PROVIDER" or not isinstance(event.get("raw_output"), str):
                    raise SourceObservationError("PROVIDER_OUTPUT_BYTES_REQUIRED", eid)
                out = event["raw_output"]
                if outcome == "COMPLETED_EMPTY_RESPONSE" and out != "":
                    raise SourceObservationError("EMPTY_RESPONSE_MUST_BE_EMPTY", eid)
                if outcome == "TEXT_ELLIPSIS" and out != "...":
                    raise SourceObservationError("ELLIPSIS_MUST_MATCH_EXACT_OUTPUT", eid)
                if outcome in {"TEXT_RESPONSE", "REFUSAL_TEXT"} and not out:
                    raise SourceObservationError("TEXT_RESPONSE_MUST_BE_NONEMPTY", eid)
            elif outcome in CLIENT_NONRESULTS:
                if event["source_class"] != "CLIENT" or "raw_output" in event:
                    raise SourceObservationError("CLIENT_NONRESULT_CANNOT_CONTAIN_MODEL_OUTPUT", eid)
            elif outcome == "API_ERROR":
                if event["source_class"] != "PROVIDER" or "raw_output" in event:
                    raise SourceObservationError("API_ERROR_CANNOT_CONTAIN_MODEL_OUTPUT", eid)
    return deepcopy(dict(value))


def preflight_source_observation(value: Any) -> dict[str, Any]:
    """Local source-shape readiness, not governance authority or API authenticity."""
    try:
        validated = validate_source_observation(value)
    except SourceObservationError as exc:
        return {
            "profile": PROFILE, "status": "DENY", "transition": "SDK_SOURCE_OBSERVATION_PREFLIGHT",
            "reason_code": exc.code, "event_id": exc.event_id,
            "correctable": True, "authority_effect": "NONE",
            "native_source_authenticated": False, "governed_result": False,
        }
    return {
        "profile": PROFILE, "status": "READY_FOR_MANIFEST",
        "transition": "SDK_SOURCE_OBSERVATION_PREFLIGHT",
        "source_sha256": _hash(validated), "event_count": len(validated["events"]),
        "outcome_classes": sorted({x["outcome"] for x in validated["events"]}),
        "authority_effect": "NONE", "native_source_authenticated": False,
        "governed_result": False,
    }


def main(argv: list[str] | None = None) -> int:
    import argparse
    from pathlib import Path
    p = argparse.ArgumentParser(prog="stegverse-source-preflight")
    p.add_argument("--input", required=True)
    p.add_argument("--output")
    a = p.parse_args(argv)
    raw = json.loads(Path(a.input).read_text(encoding="utf-8"))
    result = preflight_source_observation(raw)
    content = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if a.output:
        Path(a.output).write_text(content, encoding="utf-8")
    else:
        print(content, end="")
    return 0 if result["status"] == "READY_FOR_MANIFEST" else 2


if __name__ == "__main__":
    raise SystemExit(main())
