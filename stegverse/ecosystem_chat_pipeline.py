"""End-to-end SDK pipeline summary for Ecosystem Chat."""

from __future__ import annotations

from typing import Any

from .ecosystem_chat_backend import handle_ecosystem_chat_submission
from .ecosystem_chat_receipt_engine import evaluate_ecosystem_chat_payload_for_receipt
from .ecosystem_chat_record_export import build_record_export_candidate


def run_ecosystem_chat_pipeline(payload: dict[str, Any]) -> dict[str, Any]:
    """Compose the current SDK stage outputs for one Site payload."""
    return {
        "intake": handle_ecosystem_chat_submission(payload),
        "receipt_decision": evaluate_ecosystem_chat_payload_for_receipt(payload),
        "record_export": build_record_export_candidate(payload).to_dict(),
    }
