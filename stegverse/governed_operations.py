"""Canonical SDK call sites for governed submit, replay, and reconstruction.

This module binds actual option 0/1/2 execution to SDK usage observation without
making the observation path an authority path. Operation handlers remain the
canonical StegCore/Master Records transport boundary; this adapter supplies no
credential and grants no governance, custody, replay, or consequence authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping, Protocol

from .sdk_usage_observability import record_governed_operation


class GovernedOperationError(RuntimeError):
    """Raised when an operation result cannot prove the required run identity."""


class OperationHandler(Protocol):
    def __call__(self, *args: Any, **kwargs: Any) -> Mapping[str, Any]: ...


UsageRecorder = Callable[..., Any]


def _required_text(value: Mapping[str, Any], key: str) -> str:
    result = value.get(key)
    if not isinstance(result, str) or not result.strip():
        raise GovernedOperationError(f"governed operation result missing {key}")
    return result.strip()


def _optional_text(value: Mapping[str, Any], *keys: str) -> str | None:
    for key in keys:
        result = value.get(key)
        if isinstance(result, str) and result.strip():
            return result.strip()
    return None


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise GovernedOperationError("governed operation must return a mapping")
    return value


@dataclass
class GovernedOperations:
    """Execute canonical menu options 0/1/2 and record only verified outcomes.

    Handlers are injected because transport/provider authority belongs outside
    the SDK. The default usage recorder is disclosure-safe and queues only the
    allowlisted observation projection for the TV/TVC relay.
    """

    submit_handler: OperationHandler
    replay_handler: OperationHandler
    reconstruct_handler: OperationHandler
    usage_recorder: UsageRecorder = record_governed_operation

    def submit(self, manifest_or_data: Mapping[str, Any], **kwargs: Any) -> Mapping[str, Any]:
        """Execute option 0 and record the completed governed run identity."""
        try:
            result = _as_mapping(self.submit_handler(manifest_or_data, **kwargs))
            manifest_receipt_id = _required_text(result, "manifest_receipt_id")
            transaction_id = _required_text(result, "transaction_id")
            receipt_chain_head = _required_text(result, "receipt_chain_head")
        except Exception:
            self.usage_recorder(
                "0",
                phase="FAILED",
                source="sdk-governed-operations:submit",
            )
            raise
        self.usage_recorder(
            "0",
            phase="COMPLETED",
            manifest_receipt_id=manifest_receipt_id,
            transaction_id=transaction_id,
            receipt_chain_head=receipt_chain_head,
            source="sdk-governed-operations:submit",
        )
        return result

    def replay(self, manifest_receipt_id: str, **kwargs: Any) -> Mapping[str, Any]:
        """Execute option 1 against one immutable run locator and record completion."""
        locator = manifest_receipt_id.strip().upper()
        if not locator:
            raise ValueError("manifest_receipt_id is required")
        try:
            result = _as_mapping(self.replay_handler(locator, **kwargs))
            returned_locator = _required_text(result, "original_manifest_receipt_id").upper()
            if returned_locator != locator:
                raise GovernedOperationError("replay result manifest_receipt_id mismatch")
            transaction_id = _optional_text(result, "original_transaction_id", "transaction_id")
            receipt_chain_head = _optional_text(result, "original_receipt_chain_head", "receipt_chain_head")
            if result.get("consequence_reexecuted") is not False:
                raise GovernedOperationError("replay result must prove consequence_reexecuted=false")
        except Exception:
            self.usage_recorder(
                "1",
                phase="FAILED",
                manifest_receipt_id=locator,
                consequence_reexecuted=False,
                source="sdk-governed-operations:replay",
            )
            raise
        self.usage_recorder(
            "1",
            phase="COMPLETED",
            manifest_receipt_id=locator,
            transaction_id=transaction_id,
            receipt_chain_head=receipt_chain_head,
            consequence_reexecuted=False,
            source="sdk-governed-operations:replay",
        )
        return result

    def reconstruct(self, manifest_receipt_id: str, **kwargs: Any) -> Mapping[str, Any]:
        """Execute option 2 and require proof that consequence was not re-executed."""
        locator = manifest_receipt_id.strip().upper()
        if not locator:
            raise ValueError("manifest_receipt_id is required")
        try:
            result = _as_mapping(self.reconstruct_handler(locator, **kwargs))
            returned_locator = _required_text(result, "original_manifest_receipt_id").upper()
            if returned_locator != locator:
                raise GovernedOperationError("reconstruction result manifest_receipt_id mismatch")
            transaction_id = _optional_text(result, "transaction_id")
            receipt_chain_head = _optional_text(result, "receipt_chain_head")
            if result.get("consequence_reexecuted") is not False:
                raise GovernedOperationError("reconstruction result must prove consequence_reexecuted=false")
        except Exception:
            self.usage_recorder(
                "2",
                phase="FAILED",
                manifest_receipt_id=locator,
                consequence_reexecuted=False,
                source="sdk-governed-operations:reconstruct",
            )
            raise
        self.usage_recorder(
            "2",
            phase="COMPLETED",
            manifest_receipt_id=locator,
            transaction_id=transaction_id,
            receipt_chain_head=receipt_chain_head,
            consequence_reexecuted=False,
            source="sdk-governed-operations:reconstruct",
        )
        return result
