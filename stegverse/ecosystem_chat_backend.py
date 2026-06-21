"""Backend-style handler for Site Ecosystem Chat SDK intake.

This file provides a stable callable boundary for a future web service.
It validates the Site payload and returns the bounded SDK response shape.
It does not issue proof receipts.
"""

from __future__ import annotations

from typing import Any

from .ecosystem_chat_intake import validate_ecosystem_chat_payload


def handle_ecosystem_chat_submission(payload: dict[str, Any]) -> dict[str, Any]:
    """Validate and return the SDK backend response shape.

    This function is intentionally transport-free. A Flask/FastAPI/worker endpoint
    can call it without changing the Site-side payload contract.
    """
    return validate_ecosystem_chat_payload(payload).to_dict()
