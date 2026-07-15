from copy import deepcopy

import pytest

from stegverse.ecosystem_catalog import (
    EcosystemCatalogError,
    build_catalog,
    validate_catalog,
)
from stegverse.universal_entry_events import (
    UniversalEntryEventError,
    build_dispatch_event_chain,
    validate_event_chain,
)


def projection(record_id="site-handoff", **overrides):
    value = {
        "record_id": record_id,
        "repository": "StegVerse-Labs/Site",
        "source": "docs/SITE_MIRROR_HANDOFF.md",
        "record_type": "handoff",
        "title": "Site handoff",
        "text": "Universal entry transport remains pending.",
        "authoritative": True,
        "lifecycle_state": "CURRENT",
        "observed_at": "2026-07-14T20:00:00Z",
        "supersedes": [],
        "tags": ["site", "universal-entry"],
        "receipt_ref": None,
    }
    value.update(overrides)
    return value


def envelope():
    return {
        "origin": {
            "entry_point": "site_chat",
            "session_id": "session-1",
            "message_id": "message-1",
        },
        "continuity": {
            "transition_id": "transition-1",
            "run_id": "run-1",
        },
    }


def governed_return():
    return {
        "status": "routed",
        "selected_lanes": ["ecosystem_query", "external_llm", "conversation"],
        "unavailable_lanes": [],
        "routing_receipt": {"receipt_id": "routing-1"},
        "dispatch_receipt": {"receipt_id": "dispatch-1"},
        "lane_results": [
            {
                "lane": "ecosystem_query",
                "status": "completed",
                "sources": ["StegVerse-Labs/Site/docs/SITE_MIRROR_HANDOFF.md"],
                "evidence_count": 1,
            },
            {
                "lane": "external_llm",
                "status": "completed",
                "provider": "openai",
                "model": "example-model",
                "usage": {"input_units": 10, "output_units": 20},
                "provider_receipt": "provider-1",
            },
            {
                "lane": "conversation",
                "status": "completed",
                "synthesis": True,
                "source_count": 1,
                "sources": ["StegVerse-Labs/Site/docs/SITE_MIRROR_HANDOFF.md"],
            },
        ],
    }


def test_catalog_is_deterministic_and_read_only():
    records = [projection(), projection("sdk-status", repository="StegVerse-org/StegVerse-SDK", record_type="status")]
    first = build_catalog(records, built_at="2026-07-14T21:00:00Z", source_set_id="set-1")
    second = build_catalog(reversed(records), built_at="2026-07-14T21:00:00Z", source_set_id="set-1")
    assert first == second
    assert first["read_only"] is True
    assert first["authorizing"] is False
    assert validate_catalog(first) == first


def test_catalog_excludes_non_authoritative_and_terminal_records():
    catalog = build_catalog(
        [
            projection("good"),
            projection("untrusted", authoritative=False),
            projection("old", lifecycle_state="SUPERSEDED"),
        ],
        built_at="2026-07-14T21:00:00Z",
        source_set_id="set-1",
    )
    assert [item["record_id"] for item in catalog["records"]] == ["good"]


def test_catalog_rejects_duplicate_identity_and_tamper():
    with pytest.raises(EcosystemCatalogError):
        build_catalog([projection(), projection()], built_at="2026-07-14T21:00:00Z", source_set_id="set-1")
    catalog = build_catalog([projection()], built_at="2026-07-14T21:00:00Z", source_set_id="set-1")
    tampered = deepcopy(catalog)
    tampered["records"][0]["text"] = "changed"
    with pytest.raises(EcosystemCatalogError):
        validate_catalog(tampered)


def test_dispatch_event_chain_preserves_order_and_identity():
    events = build_dispatch_event_chain(envelope(), governed_return())
    assert [event["event_type"] for event in events] == [
        "routing", "retrieval", "provider_usage", "synthesis"
    ]
    assert events[0]["prior_event_id"] is None
    assert events[1]["prior_event_id"] == events[0]["event_id"]
    assert all(event["transition_id"] == "transition-1" for event in events)
    assert validate_event_chain(events) == events


def test_event_chain_rejects_discontinuity_authority_and_tamper():
    events = build_dispatch_event_chain(envelope(), governed_return())
    broken = deepcopy(events)
    broken[1]["prior_event_id"] = "wrong"
    with pytest.raises(UniversalEntryEventError):
        validate_event_chain(broken)
    escalated = deepcopy(events)
    escalated[0]["authorizing"] = True
    with pytest.raises(UniversalEntryEventError):
        validate_event_chain(escalated)
    tampered = deepcopy(events)
    tampered[-1]["payload"]["source_count"] = 99
    with pytest.raises(UniversalEntryEventError):
        validate_event_chain(tampered)
