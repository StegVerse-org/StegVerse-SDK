from stegverse.ecosystem_chat_destination_binding import (
    DESTINATION_DISABLED,
    DESTINATION_READY,
    build_destination_binding,
)


def test_destination_binding_disabled_by_default():
    binding = build_destination_binding().to_dict()

    assert binding["binding_status"] == DESTINATION_DISABLED
    assert binding["binding_hash"] is None
    assert binding["destination_name"] is None
    assert binding["destination_type"] is None
    assert binding["errors"]


def test_destination_binding_ready_with_valid_config():
    binding = build_destination_binding(
        {
            "destination_name": "master-records/ecosystem-chat",
            "destination_type": "master-records",
        }
    ).to_dict()

    assert binding["binding_status"] == DESTINATION_READY
    assert binding["binding_hash"].startswith("sha256:")
    assert binding["destination_name"] == "master-records/ecosystem-chat"
    assert binding["destination_type"] == "master-records"
    assert binding["errors"] == []


def test_destination_binding_rejects_invalid_config():
    binding = build_destination_binding({"destination_name": "", "destination_type": "unknown"}).to_dict()

    assert binding["binding_status"] == DESTINATION_DISABLED
    assert binding["binding_hash"] is None
    assert binding["errors"]


def test_destination_binding_is_deterministic():
    config = {"destination_name": "master-records/ecosystem-chat", "destination_type": "master-records"}

    first = build_destination_binding(config).to_dict()
    second = build_destination_binding(config).to_dict()

    assert first["binding_hash"] == second["binding_hash"]
