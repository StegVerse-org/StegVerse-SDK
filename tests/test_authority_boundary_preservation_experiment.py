from pathlib import Path
import importlib.util


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "experiments"
    / "authority_boundary_preservation"
    / "validate_fixture.py"
)

spec = importlib.util.spec_from_file_location("authority_boundary_validator", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


def test_authority_boundary_preservation_fixture():
    result = module.validate_fixture()
    final_state = result["final_state"]

    assert result["status"] == "AUTHORITY_BOUNDARY_PRESERVED"
    assert final_state["visibility_public"] is True
    assert final_state["review_permitted"] is True
    assert final_state["understanding_acknowledged"] is True

    for field in (
        "agreement",
        "validation",
        "endorsement",
        "acceptance",
        "claim_authority",
        "publication_authority",
        "attribution_authority",
        "public_association_authority",
        "delegation_authority",
    ):
        assert final_state[field] is False

    replay = result["ordered_events"][3]
    reconstruction = result["ordered_events"][4]
    assert replay["consequence_reexecution"] is False
    assert reconstruction["consequence_reexecution"] is False
    assert replay["authority_widening"] is False
    assert reconstruction["authority_widening"] is False
