from __future__ import annotations

import pytest

from stegverse.governance_tightness import (
    TIGHTNESS_SCHEMA,
    apply_tightness_to_ingestion_packet,
    label_for_scale,
    resolve_tightness,
    resolve_tightness_dict,
    scale_for_label,
)


def test_label_for_scale_ranges():
    assert label_for_scale(0) == "observe"
    assert label_for_scale(35) == "assist"
    assert label_for_scale(55) == "balanced"
    assert label_for_scale(75) == "strict"
    assert label_for_scale(95) == "fail_closed"


def test_scale_for_label_aliases():
    assert scale_for_label("open") == 10
    assert scale_for_label("review-light") == 35
    assert scale_for_label("default") == 55
    assert scale_for_label("high") == 75
    assert scale_for_label("fail closed") == 95


def test_unknown_label_fails():
    with pytest.raises(ValueError):
        scale_for_label("unknown")


def test_resolve_tightness_default_profile():
    profile = resolve_tightness()

    assert profile.schema == TIGHTNESS_SCHEMA
    assert profile.label == "balanced"
    assert profile.scale == 55
    assert profile.require_receipt is True
    assert profile.require_replay is True
    assert profile.allow_cross_repo_write is True
    assert profile.allow_cross_org_write is False


def test_resolve_tightness_fail_closed_profile():
    profile = resolve_tightness("fail_closed")

    assert profile.label == "fail_closed"
    assert profile.scale == 95
    assert profile.require_human_review is True
    assert profile.allow_cross_repo_write is False
    assert profile.allow_cross_org_write is False
    assert profile.default_route == "fail_closed"


def test_resolve_tightness_from_mapping():
    assert resolve_tightness({"scale": 40}).label == "assist"
    assert resolve_tightness({"label": "strict"}).label == "strict"


def test_resolve_tightness_dict_shape():
    profile = resolve_tightness_dict(10)

    assert profile["schema"] == TIGHTNESS_SCHEMA
    assert profile["label"] == "observe"
    assert profile["require_receipt"] is False
    assert profile["allow_cross_org_write"] is True


def test_apply_tightness_to_ingestion_packet_does_not_mutate_original():
    packet = {"schema": "example.ingestion.packet.v1", "target_repo": "StegVerse-Labs/Site"}
    output = apply_tightness_to_ingestion_packet(packet, "strict")

    assert "governance_tightness" not in packet
    assert output["governance_tightness"]["label"] == "strict"
    assert output["target_repo"] == "StegVerse-Labs/Site"
