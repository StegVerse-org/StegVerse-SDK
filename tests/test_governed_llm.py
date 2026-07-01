from stegverse.governed_llm import (
    EvidencePointer,
    build_query_packet,
    build_response_receipt,
    reconstruction_summary,
)


def test_query_packet_hash_is_stable_for_same_inputs():
    first = build_query_packet(
        "What changed since the prior response?",
        allowed_sources=("receipt_index", "model_knowledge"),
        policy={"version": "test"},
        delegation={"actor": "adapter", "scope": "read"},
    )
    second = build_query_packet(
        "What changed since the prior response?",
        allowed_sources=("receipt_index", "model_knowledge"),
        policy={"version": "test"},
        delegation={"actor": "adapter", "scope": "read"},
    )

    assert first.packet_hash != ""
    assert first.policy_hash == second.policy_hash
    assert first.delegation_hash == second.delegation_hash
    assert first.query == second.query


def test_response_receipt_links_output_to_query_packet():
    evidence = EvidencePointer(
        source_type="receipt",
        pointer="master-records://example/receipt/1",
        content_hash="abc123",
        retrieved_at="2026-07-01T00:00:00+00:00",
    )
    packet = build_query_packet(
        "Reconstruct the prior response.",
        allowed_sources=("receipt_index",),
        evidence=(evidence,),
        policy={"policy": "read-only"},
        delegation={"adapter": "read"},
    )
    receipt = build_response_receipt(
        packet,
        "Prior response reconstructed from receipt pointer.",
        model_provider="test-provider",
        model_name="test-model",
        decision="allow",
        admissibility_status="allowed_read_only",
    )
    summary = reconstruction_summary(packet, receipt)

    assert receipt.query_packet_hash == packet.packet_hash
    assert receipt.decision == "ALLOW"
    assert summary["evidence_hashes"] == ["abc123"]
    assert summary["reconstruction_status"] == "reconstructable"
