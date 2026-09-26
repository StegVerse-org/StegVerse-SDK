import pytest

from stegverse.worker_cost_evidence import COMPONENTS, SCHEMA, qualify_worker_cost


def packet():
    return {
        "schema": SCHEMA, "workflow_id": "fixture-not-runtime",
        "components": {name: {
            "amount_minor_units": 10, "currency": "USD",
            "classification": "MEASURED", "original_evidence_sha256": "a" * 64,
        } for name in COMPONENTS},
    }


def test_complete_source_claim_never_promotes_to_verified_cost():
    result = qualify_worker_cost(packet())
    assert result["source_declarations_complete"] is True
    assert result["independently_verified"] is False
    assert result["measured_total_minor_units"] is None
    assert result["benchmark_promotion_authorized"] is False
    assert result["next_action"] == "INDEPENDENT_ORIGINAL_EVIDENCE_RETRIEVAL"


@pytest.mark.parametrize("component", COMPONENTS)
def test_each_missing_component_fails_closed(component):
    p = packet()
    del p["components"][component]
    with pytest.raises(ValueError, match="exactly six"):
        qualify_worker_cost(p)


@pytest.mark.parametrize("mutation", [
    {"classification": "ESTIMATED"},
    {"original_evidence_sha256": "unavailable"},
    {"amount_minor_units": -1},
    {"amount_minor_units": True},
    {"currency": "US"},
])
def test_unqualified_component_prevents_promotion(mutation):
    p = packet()
    p["components"]["provider"].update(mutation)
    result = qualify_worker_cost(p)
    assert result["source_declarations_complete"] is False
    assert result["measured_total_minor_units"] is None
    assert result["next_action"] == "REMEDIATE_MISSING_COMPONENT_EVIDENCE"


def test_rejects_schema_and_workflow_identity():
    p = packet()
    p["schema"] = "wrong"
    with pytest.raises(ValueError):
        qualify_worker_cost(p)
    p = packet()
    p["workflow_id"] = ""
    with pytest.raises(ValueError):
        qualify_worker_cost(p)


def test_digest_deterministic():
    assert qualify_worker_cost(packet())["qualification_sha256"] == qualify_worker_cost(packet())["qualification_sha256"]
