"""Deprecated import path kept for pinned consumers.

Use ``stegverse.master_records_organization_record``. Every name here forwards to that
module (MASTER-RECORDS-BULK-SEMANTIC-REMEDIATION-002) and will be removed in a future
major release.
"""
from __future__ import annotations

import warnings
from typing import Any, Mapping, Sequence

from .master_records_organization_record import (  # noqa: F401
    LEGACY_ORGANIZATION_RECORD_RECEIPT_SCHEMA,
    LEGACY_RECEIPT_RECORDED_FIELD,
    ORGANIZATION_RECORD_RECEIPT_SCHEMA,
    ORGANIZATION_RECORD_REQUEST_SCHEMA,
    RECONSTRUCTION_SCHEMA,
    MasterRecordsOrganizationRecordClient,
    MasterRecordsOrganizationRecordError,
    _canonical,
    _digest,
    build_organization_record_request,
    validate_organization_record_receipt,
    verify_reconstruction,
)

warnings.warn(
    "stegverse.master_records_custody is deprecated; "
    "use stegverse.master_records_organization_record",
    DeprecationWarning,
    stacklevel=2,
)

# Deprecated class aliases: the same class objects, so isinstance and except clauses
# written against the old names keep working.
MasterRecordsCustodyError = MasterRecordsOrganizationRecordError
MasterRecordsCustodyClient = MasterRecordsOrganizationRecordClient


def _deprecated(old: str, new: str) -> None:
    warnings.warn(f"{old} is deprecated; use {new}", DeprecationWarning, stacklevel=3)


def build_custody_submission(events: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Deprecated alias of :func:`build_organization_record_request`."""
    _deprecated("build_custody_submission", "build_organization_record_request")
    return build_organization_record_request(events)


def validate_custody_receipt(
    submission: Mapping[str, Any], receipt: Mapping[str, Any]
) -> dict[str, Any]:
    """Deprecated alias of :func:`validate_organization_record_receipt`."""
    _deprecated("validate_custody_receipt", "validate_organization_record_receipt")
    return validate_organization_record_receipt(submission, receipt)


__all__ = [
    "MasterRecordsCustodyClient",
    "MasterRecordsCustodyError",
    "build_custody_submission",
    "validate_custody_receipt",
    "verify_reconstruction",
]
