from __future__ import annotations

from scripts.verify_micro_node_adapter_fixture import main as verify_micro_node_adapter_fixture


def test_micro_node_adapter_fixture_passes() -> None:
    assert verify_micro_node_adapter_fixture() == 0
