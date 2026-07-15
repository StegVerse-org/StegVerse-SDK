import json
from pathlib import Path

from stegverse.universal_entry_dispatch import dispatch_universal_entry
from stegverse.universal_entry_handlers import build_default_handler_registry


FIXTURE = Path("examples/universal_entry/entry_point_parity.json")


def load_fixture():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def make_envelope(entry_point, fixture):
    return {
        "schema": "stegverse.universal_entry_envelope.v0.1",
        "origin": {
            "entry_point": entry_point,
            "actor_id": None,
            "node_id": f"node.{entry_point}",
            "session_id": f"session.{entry_point}",
            "message_id": f"message.{entry_point}.0001",
        },
        "request": fixture["request"],
        "routing": fixture["routing"],
        "authority": {
            "class": "none",
            "delegation_ref": None,
            "policy_refs": [],
            "execution_authority_granted": False,
        },
        "receipt": {
            "required": False,
            "expected_types": [],
            "prior_receipt_refs": [],
        },
        "continuity": {
            "transition_id": f"transition.{entry_point}.0001",
            "run_id": f"run.{entry_point}.0001",
            "parent_message_id": None,
            "manifest_hash": None,
            "replay_required": False,
        },
    }


def test_all_declared_entry_points_share_route_and_engine_semantics():
    fixture = load_fixture()

    def retrieve(query, context):
        return [
            {
                "text": "Site preparation is complete; live activation evidence remains pending.",
                "source": "StegVerse-Labs/Site/docs/SITE_MIRROR_HANDOFF.md",
            }
        ]

    handlers = build_default_handler_registry(ecosystem_retriever=retrieve)
    observed = []
    for entry_point in fixture["entry_points"]:
        result = dispatch_universal_entry(
            make_envelope(entry_point, fixture),
            {"capabilities": fixture["capabilities"]},
            handlers,
        )
        observed.append(
            {
                "entry_point": entry_point,
                "status": result["status"],
                "selected_lanes": result["selected_lanes"],
                "dispatch_order": [item["lane"] for item in result["lane_results"]],
                "response": result["response"],
                "authority": result["authority"],
            }
        )

    baseline = {key: value for key, value in observed[0].items() if key != "entry_point"}
    for record in observed[1:]:
        assert {key: value for key, value in record.items() if key != "entry_point"} == baseline

    expected = fixture["expected"]
    assert baseline["status"] == expected["status"]
    assert baseline["selected_lanes"] == expected["selected_lanes"]
    assert baseline["dispatch_order"] == expected["dispatch_order"]
    assert baseline["authority"] == {
        "execution_authority_granted": expected["execution_authority_granted"],
        "admissibility_determined": expected["admissibility_determined"],
        "custody_transferred": expected["custody_transferred"],
    }


def test_entry_point_identity_remains_preserved_in_each_routing_receipt():
    fixture = load_fixture()

    def retrieve(query, context):
        return [{"text": "status", "source": "source"}]

    handlers = build_default_handler_registry(ecosystem_retriever=retrieve)
    receipt_ids = set()
    for entry_point in fixture["entry_points"]:
        result = dispatch_universal_entry(
            make_envelope(entry_point, fixture),
            {"capabilities": fixture["capabilities"]},
            handlers,
        )
        routing_receipt = result["routing_receipt"]
        assert routing_receipt["origin_entry_point"] == entry_point
        receipt_ids.add(routing_receipt["receipt_id"])

    assert len(receipt_ids) == len(fixture["entry_points"])
