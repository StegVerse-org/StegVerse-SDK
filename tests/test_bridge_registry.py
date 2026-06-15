from __future__ import annotations

import pytest

from stegverse.bridge_registry import (
    bridge_ids,
    bridge_registry_snapshot,
    get_dynamic_bridge,
    list_dynamic_bridges,
    require_dynamic_bridge,
)


def test_bridge_ids_include_registered_paths():
    assert bridge_ids() == ["generic_tester_packet", "llm_output", "math_artifact"]


def test_list_dynamic_bridges_returns_descriptors():
    bridges = list_dynamic_bridges()
    ids = {bridge["id"] for bridge in bridges}

    assert ids == {"generic_tester_packet", "llm_output", "math_artifact"}
    assert all("module" in bridge for bridge in bridges)
    assert all("evaluator" in bridge for bridge in bridges)
    assert all("result_schema" in bridge for bridge in bridges)


def test_get_dynamic_bridge_returns_copy():
    bridge = get_dynamic_bridge("llm_output")
    assert bridge is not None
    assert bridge["discipline_id"] == "ai_llm_systems"

    bridge["discipline_id"] = "mutated"
    fresh = get_dynamic_bridge("llm_output")
    assert fresh["discipline_id"] == "ai_llm_systems"


def test_require_dynamic_bridge_raises_for_unknown():
    with pytest.raises(KeyError):
        require_dynamic_bridge("missing_bridge")


def test_bridge_registry_snapshot_is_copy():
    snapshot = bridge_registry_snapshot()
    snapshot["math_artifact"]["discipline_id"] = "mutated"

    fresh = bridge_registry_snapshot()
    assert fresh["math_artifact"]["discipline_id"] == "mathematics_formal_methods"
