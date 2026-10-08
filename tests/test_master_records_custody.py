"""Deprecated aliases in stegverse.master_records_custody forward to the new module.

Pinned consumers still import the old path; see
MASTER-RECORDS-BULK-SEMANTIC-REMEDIATION-002.
"""
import importlib
import sys
import warnings

import pytest

from stegverse import master_records_organization_record as current
from stegverse.universal_entry_events import build_continuation_event


def _legacy_module():
    sys.modules.pop("stegverse.master_records_custody", None)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        module = importlib.import_module("stegverse.master_records_custody")
    assert any(issubclass(w.category, DeprecationWarning) for w in caught)
    return module


def _events():
    envelope = {
        "origin": {"entry_point": "sdk", "session_id": "session-1", "message_id": "message-1"},
        "continuity": {"transition_id": "transition-1", "run_id": "run-1"},
    }
    first = build_continuation_event(
        event_type="routing", envelope=envelope, payload={"selected_lanes": ["conversation"]}
    )
    return [first]


def test_legacy_class_names_are_the_new_classes():
    legacy = _legacy_module()
    assert legacy.MasterRecordsCustodyClient is current.MasterRecordsOrganizationRecordClient
    assert legacy.MasterRecordsCustodyError is current.MasterRecordsOrganizationRecordError
    assert legacy.verify_reconstruction is current.verify_reconstruction


def test_legacy_functions_warn_and_forward():
    legacy = _legacy_module()
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        submission = legacy.build_custody_submission(_events())
        with pytest.raises(current.MasterRecordsOrganizationRecordError):
            legacy.validate_custody_receipt(submission, {"schema": "unknown"})
    assert [w.category for w in caught] == [DeprecationWarning, DeprecationWarning]
    assert submission == current.build_organization_record_request(_events())


def test_legacy_error_name_still_catches_new_errors():
    legacy = _legacy_module()
    with pytest.raises(legacy.MasterRecordsCustodyError):
        current.build_organization_record_request([])
