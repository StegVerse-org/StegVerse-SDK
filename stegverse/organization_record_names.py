"""Shared Master Records organization-record field names and their legacy forms.

Master Records relates to organization records and reconstruction from them. The
Organization owns custody of its runtime history and Interlock/InTr admits transitions.

Naming migration (MASTER-RECORDS-BULK-SEMANTIC-REMEDIATION-002): writers emit only the
names without the ``LEGACY_`` prefix. Readers accept both, through :func:`read_field`
and :func:`read_compatible`, so already-deployed peers keep working. Legacy names shared
across modules are defined once, here; module-specific ones sit beside their reader.
"""
from __future__ import annotations

from typing import Any, Mapping

# Organization-record status of a governed run, as reported by the SDK runtimes.
ORGANIZATION_RECORD_STATUS_FIELD = "master_records_organization_record_status"
LEGACY_ORGANIZATION_RECORD_STATUS_FIELD = "master_records_custody_status"

# Master Records wire fields on its own record API.
RECORD_STATUS_FIELD = "record_status"
LEGACY_RECORD_STATUS_FIELD = "custody_status"
RECORD_REQUESTED_FIELD = "record_requested"
LEGACY_RECORD_REQUESTED_FIELD = "custody_requested"

# The organization-record receipt a governed run carries.
ORGANIZATION_RECORD_RECEIPT_FIELD = "master_records_organization_record_receipt"
LEGACY_ORGANIZATION_RECORD_RECEIPT_FIELD = "master_records_custody_receipt"

# Requested capability / evidence-component name.
ORGANIZATION_RECORD_CAPABILITY = "master_records_organization_record"
LEGACY_ORGANIZATION_RECORD_CAPABILITY = "master_records_custody"

# Non-authority flag: "this component claims a Master Records organization record".
ORGANIZATION_RECORD_CLAIMED_FIELD = "master_records_organization_record_claimed"
LEGACY_ORGANIZATION_RECORD_CLAIMED_FIELD = "master_records_custody_claimed"

# Requirement flag on bootstrap packets.
ORGANIZATION_RECORD_REQUIRED_FIELD = "master_records_organization_record_required"
LEGACY_ORGANIZATION_RECORD_REQUIRED_FIELD = "master_records_custody_required"

# Evidence flag on dependency reviews (formerly a "closure" flag).
ORGANIZATION_RECORD_EVIDENCE_FIELD = "master_records_organization_record"
LEGACY_ORGANIZATION_RECORD_EVIDENCE_FIELD = "master_records_closure"

# Result flag: "an organization record in Master Records was observed for this result"
# (formerly a "closure observed" flag).
ORGANIZATION_RECORD_OBSERVED_FIELD = "organization_master_records_organization_record_observed"
LEGACY_ORGANIZATION_RECORD_OBSERVED_FIELD = "organization_master_records_closure_observed"
# Source-evidence packets used a second legacy spelling of the same flag.
LEGACY_SOURCE_PACKET_ORGANIZATION_RECORD_OBSERVED_FIELD = "organization_master_records_custody_observed"

# Adapter authority flag: "local persistence is a Master Records organization record".
LOCAL_PERSISTENCE_IS_ORGANIZATION_RECORD_FIELD = "local_persistence_is_master_records_organization_record"
LEGACY_LOCAL_PERSISTENCE_IS_ORGANIZATION_RECORD_FIELD = "local_persistence_is_master_records_custody"

# Result flag: "this evidence proves a Master Records organization record".
ORGANIZATION_RECORD_PROVEN_FIELD = "master_records_organization_record_proven"
LEGACY_ORGANIZATION_RECORD_PROVEN_FIELD = "master_records_custody_proven"

# Adapter result flag: "a Master Records organization record was recorded".
ORGANIZATION_RECORD_RECORDED_FIELD = "master_records_organization_record_recorded"
LEGACY_ORGANIZATION_RECORD_RECORDED_FIELD = "master_records_custody_recorded"

_MISSING = object()

# New name -> legacy name. ORGANIZATION_RECORD_EVIDENCE_FIELD shares its new name with
# ORGANIZATION_RECORD_CAPABILITY but has a different legacy name, so its reader maps it
# explicitly instead of through this table.
LEGACY_NAMES = {
    ORGANIZATION_RECORD_STATUS_FIELD: LEGACY_ORGANIZATION_RECORD_STATUS_FIELD,
    RECORD_STATUS_FIELD: LEGACY_RECORD_STATUS_FIELD,
    RECORD_REQUESTED_FIELD: LEGACY_RECORD_REQUESTED_FIELD,
    ORGANIZATION_RECORD_RECEIPT_FIELD: LEGACY_ORGANIZATION_RECORD_RECEIPT_FIELD,
    ORGANIZATION_RECORD_CAPABILITY: LEGACY_ORGANIZATION_RECORD_CAPABILITY,
    ORGANIZATION_RECORD_CLAIMED_FIELD: LEGACY_ORGANIZATION_RECORD_CLAIMED_FIELD,
    ORGANIZATION_RECORD_REQUIRED_FIELD: LEGACY_ORGANIZATION_RECORD_REQUIRED_FIELD,
    ORGANIZATION_RECORD_OBSERVED_FIELD: LEGACY_ORGANIZATION_RECORD_OBSERVED_FIELD,
    LOCAL_PERSISTENCE_IS_ORGANIZATION_RECORD_FIELD: LEGACY_LOCAL_PERSISTENCE_IS_ORGANIZATION_RECORD_FIELD,
    ORGANIZATION_RECORD_PROVEN_FIELD: LEGACY_ORGANIZATION_RECORD_PROVEN_FIELD,
    ORGANIZATION_RECORD_RECORDED_FIELD: LEGACY_ORGANIZATION_RECORD_RECORDED_FIELD,
}


def read_field(record: Mapping[str, Any], field: str, legacy_field: str, default: Any = None) -> Any:
    """Read ``field``, falling back to ``legacy_field`` for pre-migration peers."""
    value = record.get(field, _MISSING)
    if value is not _MISSING:
        return value
    return record.get(legacy_field, default)


def legacy_name_for(field: str) -> str | None:
    """The legacy name a reader must also accept for ``field``, if any."""
    return LEGACY_NAMES.get(field)


def read_compatible(record: Mapping[str, Any], field: str, default: Any = None) -> Any:
    """Read ``field``, accepting its legacy name when the migration defines one."""
    legacy = LEGACY_NAMES.get(field)
    if legacy is None:
        return record.get(field, default)
    return read_field(record, field, legacy, default)


__all__ = [
    name
    for name in dict(globals())
    if (name.isupper() and not name.startswith("_"))
    or name in {"read_field", "read_compatible", "legacy_name_for"}
]
