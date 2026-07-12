from stegverse.entry_point_roles import (
    EntryPointRoleError,
    get_entry_point_role,
    list_entry_point_roles,
    validate_entry_point_role,
)


def test_registry_contains_primary_entry_points() -> None:
    roles = {item["entry_point_id"]: item for item in list_entry_point_roles()}
    assert set(roles) == {"sdk", "llm_adapter", "ecosystem_chat"}
    assert "governed_coding" in roles["ecosystem_chat"]["interaction_types"]
    assert "raw_data_governance_test" in roles["sdk"]["interaction_types"]
    assert "provider_output_normalization" in roles["llm_adapter"]["interaction_types"]


def test_roles_preserve_usage_and_session_lineage() -> None:
    for role in list_entry_point_roles():
        assert role["usage_reporting"]["metric_owner_required"] is True
        assert role["usage_reporting"]["measurement_id_required"] is True
        assert role["session_continuity"]["preserves_session_id"] is True
        assert role["session_continuity"]["preserves_transition_lineage"] is True
        assert len(role["role_sha256"]) == 64


def test_authority_self_grant_is_rejected() -> None:
    role = get_entry_point_role("sdk")
    role.pop("role_sha256")
    role["authority_boundaries"]["acceptance_is_authority"] = True
    try:
        validate_entry_point_role(role)
    except EntryPointRoleError:
        return
    raise AssertionError("role self-grant should fail closed")
