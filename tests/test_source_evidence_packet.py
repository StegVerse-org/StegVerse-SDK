from copy import deepcopy

from stegverse.source_evidence_packet import (
    build_source_evidence_packet, verify_source_evidence_packet,
)


def test_source_packet_deterministic_and_non_authorizing():
    manifest = {"payload": {"value": 7}}
    requirements = [
        {"requirement_id": "math", "capability_id": "native_source_math"},
        {"requirement_id": "diagnostic", "capability_id": "ecosystem_diagnostic"},
    ]
    packet = build_source_evidence_packet(manifest, requirements)
    assert packet == build_source_evidence_packet(manifest, requirements)
    assert packet["lineage_verified"] is True
    assert packet["non_allow_results"] == ()
    assert packet["execution_authorized"] is False
    assert packet["runtime_execution_observed"] is False
    assert packet["route_substitution_permitted"] is False
    assert packet["evidence_ceiling"] == "SOURCE_ONLY"
    assert verify_source_evidence_packet(manifest, requirements, packet)


def test_source_packet_binds_multiple_non_allow_predicates_and_corrections():
    manifest = {}
    requirements = [
        {"requirement_id": "missing", "capability_id": "native_source_math",
         "required_inputs": ["payload"]},
        {"requirement_id": "unsupported", "capability_id": "not-installed"},
        {"requirement_id": "version", "capability_id": "native_source_math",
         "version_compatible": False},
        {"requirement_id": "probe", "capability_id": "ecosystem_diagnostic",
         "authentic_runtime_evidence_required": True},
    ]
    packet = build_source_evidence_packet(manifest, requirements)
    assert [r["disposition"] for r in packet["non_allow_results"]] == [
        "MISSING_INPUT", "UNSUPPORTED", "VERSION_INCOMPATIBLE", "PROBE_REQUIRED"
    ]
    assert [r["failed_predicate"] for r in packet["non_allow_results"]] == [
        "REQUIRED_INPUT_PRESENT", "CAPABILITY_INSTALLED",
        "REQUESTED_VERSION_COMPATIBLE", "AUTHENTIC_RUNTIME_EVIDENCE_OBSERVED"
    ]
    assert all(r["permitted_correction"] for r in packet["non_allow_results"])
    assert verify_source_evidence_packet(manifest, requirements, packet)
    assert not verify_source_evidence_packet({"payload": "changed"}, requirements, packet)
    assert not verify_source_evidence_packet(manifest, list(reversed(requirements)), packet)


def test_packet_tamper_and_forged_runtime_receipt_rejected():
    manifest = {"payload": "x"}
    requirements = [{"requirement_id": "m", "capability_id": "native_source_math"}]
    packet = build_source_evidence_packet(manifest, requirements)
    for field, value in (
        ("execution_authorized", True),
        ("runtime_execution_observed", True),
        ("route_substitution_permitted", True),
        ("evidence_ceiling", "AUTHENTIC_RUNTIME"),
        ("lineage_verified", False),
        ("qualification_sha256", "0" * 64),
        ("derived_plan_sha256", "0" * 64),
        ("packet_sha256", "0" * 64),
    ):
        forged = deepcopy(packet)
        forged[field] = value
        assert not verify_source_evidence_packet(manifest, requirements, forged)
    forged = deepcopy(packet)
    forged["intr_receipt"] = {"disposition": "ALLOW"}
    assert not verify_source_evidence_packet(manifest, requirements, forged)
