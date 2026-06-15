from __future__ import annotations

from examples.list_dynamic_bridges import BRIDGE_REGISTRY_SCHEMA, build_payload


def test_bridge_registry_payload_shape():
    payload = build_payload()

    assert payload["schema"] == BRIDGE_REGISTRY_SCHEMA
    assert payload["bridge_ids"] == ["generic_tester_packet", "llm_output", "math_artifact"]
    assert len(payload["bridges"]) == 3


def test_bridge_registry_payload_descriptors_match_schema_contract():
    payload = build_payload()
    required = {
        "id",
        "label",
        "module",
        "evaluator",
        "summary",
        "input_schema",
        "result_schema",
        "discipline_id",
        "recommended_route",
    }

    for bridge in payload["bridges"]:
        assert required.issubset(bridge.keys())
        assert isinstance(bridge["recommended_route"], list)
        assert bridge["input_schema"].endswith(".schema.json")
        assert bridge["result_schema"].endswith(".schema.json")
