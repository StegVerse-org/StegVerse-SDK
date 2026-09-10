import pytest

from stegverse.security_posture import SecurityPostureError
from stegverse.security_posture_stack import select_posture_stack


def test_automatic_floor_is_distinct_from_selected_posture():
    result = select_posture_stack(data_class="PII", selected_tier="HIGHEST")
    assert result["automatic_posture"]["tier"] == "HIGH"
    assert result["selected_posture"]["tier"] == "HIGHEST"
    assert result["effective_posture"]["tier"] == "HIGHEST"
    assert result["selected_posture"]["selection_present"] is True


def test_no_selection_defaults_to_automatic_floor_without_claiming_explicit_selection():
    result = select_posture_stack(data_class="PII")
    assert result["automatic_posture"]["tier"] == "HIGH"
    assert result["selected_posture"]["tier"] == "HIGH"
    assert result["selected_posture"]["selection_present"] is False
    assert result["effective_posture"]["tier"] == "HIGH"


def test_selection_below_automatic_floor_fails_closed():
    with pytest.raises(SecurityPostureError, match="below_automatic_floor"):
        select_posture_stack(data_class="ePHI", selected_tier="HIGH")


def test_kv_skap_automatic_floor_cannot_be_weakened():
    result = select_posture_stack(channel="KV-SKAP")
    assert result["automatic_posture"]["tier"] == "HIGHEST"
    assert result["selectable_tiers"] == ["HIGHEST"]
    assert result["downgrade_below_automatic_floor_allowed"] is False
