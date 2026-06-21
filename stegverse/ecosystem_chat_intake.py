"""Site Ecosystem Chat to SDK intake validation.

This module validates the Site-generated three-layer payload:
fields, manifest, and receipt_window.

It does not issue proof receipts. Before SDK backend activation, the
response receipt_id remains None.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

ALLOWED_ROUTES = {"Site", "StegVerse-002", "formalism-tests", "Continuity", "Publisher", "Unknown"}
ALLOWED_RECEIPT_EXPECTATIONS = {"none", "sdk_intake_receipt_requested"}
ALLOWED_SUBMISSION_POSTURES = {"draft", "ready_for_submission"}
TARGET_ENTRY_POINT = "StegVerse-org/SDK"
INPUT_MODE = "text_form"
SOURCE_SURFACE = "StegVerse-Labs/Site/ecosystem-chat.html"

FIELD_KEYS = {
    "target_entry_point",
    "input_mode",
    "requested_route",
    "receipt_expectation",
    "submission_posture",
    "user_request",
    "declared_goal",
    "operator_note",
}
MANIFEST_KEYS = {
    "target_entry_point",
    "input_mode",
    "requested_route",
    "user_request",
    "declared_goal",
    "operator_note",
    "source_surface",
}
RECEIPT_WINDOW_KEYS = {
    "receipt_expectation",
    "submission_posture",
    "site_receipt_authority",
    "manifest_correct_at_submission",
    "submission_target",
    "correctness_errors",
}


@dataclass(frozen=True)
class IntakeResult:
    accepted: bool
    routed_module: str
    receipt_id: None
    next_action: str
    errors: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "accepted": self.accepted,
            "routed_module": self.routed_module,
            "receipt_id": self.receipt_id,
            "next_action": self.next_action,
            "errors": self.errors,
        }


def validate_ecosystem_chat_payload(payload: dict[str, Any]) -> IntakeResult:
    errors: list[str] = []

    if not isinstance(payload, dict):
        return _deny(["payload must be an object"])

    if set(payload) != {"fields", "manifest", "receipt_window"}:
        errors.append("payload must contain exactly fields, manifest, and receipt_window")
        return _deny(errors)

    fields = payload.get("fields")
    manifest = payload.get("manifest")
    receipt_window = payload.get("receipt_window")

    errors.extend(_validate_object("fields", fields, FIELD_KEYS))
    errors.extend(_validate_object("manifest", manifest, MANIFEST_KEYS))
    errors.extend(_validate_object("receipt_window", receipt_window, RECEIPT_WINDOW_KEYS))
    if errors:
        return _deny(errors)

    assert isinstance(fields, dict)
    assert isinstance(manifest, dict)
    assert isinstance(receipt_window, dict)

    errors.extend(_validate_fields(fields))
    errors.extend(_validate_manifest(manifest))
    errors.extend(_validate_receipt_window(receipt_window))
    errors.extend(_validate_derivation(fields, manifest, receipt_window))

    if errors:
        return _deny(errors)

    return IntakeResult(
        accepted=True,
        routed_module=manifest["requested_route"],
        receipt_id=None,
        next_action="Continue with governed SDK intake review.",
        errors=[],
    )


def _validate_object(name: str, value: Any, required_keys: set[str]) -> list[str]:
    if not isinstance(value, dict):
        return [f"{name} must be an object"]
    if set(value) != required_keys:
        return [f"{name} keys do not match required contract"]
    return []


def _validate_fields(fields: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if fields["target_entry_point"] != TARGET_ENTRY_POINT:
        errors.append("fields.target_entry_point must be StegVerse-org/SDK")
    if fields["input_mode"] != INPUT_MODE:
        errors.append("fields.input_mode must be text_form")
    if fields["requested_route"] not in ALLOWED_ROUTES:
        errors.append("fields.requested_route is not allowed")
    if fields["receipt_expectation"] not in ALLOWED_RECEIPT_EXPECTATIONS:
        errors.append("fields.receipt_expectation is not allowed")
    if fields["submission_posture"] not in ALLOWED_SUBMISSION_POSTURES:
        errors.append("fields.submission_posture is not allowed")
    if not _is_nonempty_string(fields["user_request"]):
        errors.append("fields.user_request is required")
    if not _is_nonempty_string(fields["declared_goal"]):
        errors.append("fields.declared_goal is required")
    if not isinstance(fields["operator_note"], str):
        errors.append("fields.operator_note must be a string")
    return errors


def _validate_manifest(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if manifest["target_entry_point"] != TARGET_ENTRY_POINT:
        errors.append("manifest.target_entry_point must be StegVerse-org/SDK")
    if manifest["input_mode"] != INPUT_MODE:
        errors.append("manifest.input_mode must be text_form")
    if manifest["requested_route"] not in ALLOWED_ROUTES:
        errors.append("manifest.requested_route is not allowed")
    if not _is_nonempty_string(manifest["user_request"]):
        errors.append("manifest.user_request is required")
    if not _is_nonempty_string(manifest["declared_goal"]):
        errors.append("manifest.declared_goal is required")
    if not isinstance(manifest["operator_note"], str):
        errors.append("manifest.operator_note must be a string")
    if manifest["source_surface"] != SOURCE_SURFACE:
        errors.append("manifest.source_surface is not allowed")
    return errors


def _validate_receipt_window(receipt_window: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if receipt_window["receipt_expectation"] not in ALLOWED_RECEIPT_EXPECTATIONS:
        errors.append("receipt_window.receipt_expectation is not allowed")
    if receipt_window["submission_posture"] not in ALLOWED_SUBMISSION_POSTURES:
        errors.append("receipt_window.submission_posture is not allowed")
    if receipt_window["site_receipt_authority"] is not False:
        errors.append("receipt_window.site_receipt_authority must be false")
    if not isinstance(receipt_window["manifest_correct_at_submission"], bool):
        errors.append("receipt_window.manifest_correct_at_submission must be boolean")
    if receipt_window["submission_target"] != TARGET_ENTRY_POINT:
        errors.append("receipt_window.submission_target must be StegVerse-org/SDK")
    if not isinstance(receipt_window["correctness_errors"], list):
        errors.append("receipt_window.correctness_errors must be a list")
    return errors


def _validate_derivation(
    fields: dict[str, Any],
    manifest: dict[str, Any],
    receipt_window: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    for key in ("target_entry_point", "input_mode", "requested_route", "user_request", "declared_goal", "operator_note"):
        if manifest[key] != fields[key]:
            errors.append(f"manifest.{key} must derive from fields.{key}")
    for key in ("receipt_expectation", "submission_posture"):
        if receipt_window[key] != fields[key]:
            errors.append(f"receipt_window.{key} must derive from fields.{key}")
    if receipt_window["manifest_correct_at_submission"] is not True:
        errors.append("receipt_window.manifest_correct_at_submission must be true for acceptance")
    if receipt_window["correctness_errors"]:
        errors.append("receipt_window.correctness_errors must be empty for acceptance")
    return errors


def _deny(errors: list[str]) -> IntakeResult:
    return IntakeResult(
        accepted=False,
        routed_module="StegVerse-org/SDK",
        receipt_id=None,
        next_action="Correct the payload and resubmit.",
        errors=errors,
    )


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())
