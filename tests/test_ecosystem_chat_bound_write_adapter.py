from tests.test_ecosystem_chat_intake_minimal import payload
from stegverse.ecosystem_chat_bound_write_adapter import DestinationBoundWriteAdapter
from stegverse.ecosystem_chat_destination_binding import build_destination_binding
from stegverse.ecosystem_chat_local_issuer import LocalGovernedEcosystemChatIssuer
from stegverse.ecosystem_chat_local_write_adapter import LocalEcosystemChatWriteAdapter
from stegverse.ecosystem_chat_pipeline import run_ecosystem_chat_pipeline


def test_bound_write_adapter_blocks_without_ready_destination():
    result = run_ecosystem_chat_pipeline(
        payload(),
        issuer=LocalGovernedEcosystemChatIssuer(),
        write_adapter=DestinationBoundWriteAdapter(
            build_destination_binding().to_dict(),
            LocalEcosystemChatWriteAdapter(),
        ),
    )

    assert result["write_result"]["write_complete"] is False
    assert result["write_result"]["write_id"] is None
    assert result["write_result"]["adapter_name"] == "DESTINATION_BOUND_WRITE_ADAPTER"
    assert result["write_result"]["errors"]


def test_bound_write_adapter_delegates_with_ready_destination():
    binding = build_destination_binding(
        {
            "destination_name": "master-records/ecosystem-chat",
            "destination_type": "master-records",
        }
    ).to_dict()
    result = run_ecosystem_chat_pipeline(
        payload(),
        issuer=LocalGovernedEcosystemChatIssuer(),
        write_adapter=DestinationBoundWriteAdapter(binding, LocalEcosystemChatWriteAdapter()),
    )

    assert result["write_result"]["write_complete"] is True
    assert result["write_result"]["write_id"].startswith("master-records/ecosystem-chat:ecw-local-")
    assert result["write_result"]["adapter_name"] == "DESTINATION_BOUND_WRITE_ADAPTER"
    assert result["write_result"]["receipt_id"] == result["issuer_result"]["receipt_id"]
    assert result["write_result"]["errors"] == []
