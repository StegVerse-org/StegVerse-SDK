from copy import deepcopy

from stegverse.source_evidence_packet import (
    build_source_evidence_packet, verify_source_evidence_packet,
)


def test_two_unrelated_evaluators_have_distinct_bound_source_packets():
    manifest = {"source": {"formula": "x + 1"}, "observation": {"target": "source-only"}}
    math = [{"requirement_id": "math", "capability_id": "native_source_math",
             "route_id": "stegverse.route.source-native-math.v1"}]
    diagnostic = [{"requirement_id": "diagnostic", "capability_id": "ecosystem_diagnostic",
                   "route_id": "stegverse.route.ecosystem-diagnostic.v1"}]
    a = build_source_evidence_packet(manifest, math, evaluator_id="math-evaluator")
    b = build_source_evidence_packet(manifest, diagnostic, evaluator_id="diagnostic-evaluator")
    assert a["source_manifest_sha256"] == b["source_manifest_sha256"]
    assert a["derived_plan_sha256"] != b["derived_plan_sha256"]
    assert a["source_packet_sha256"] != b["source_packet_sha256"]
    assert verify_source_evidence_packet(manifest, math, a)
    assert verify_source_evidence_packet(manifest, diagnostic, b)
    assert not verify_source_evidence_packet(manifest, diagnostic, a)
    assert all(not a[field] and not b[field] for field in (
        "execution_authorized", "authentic_intr_disposition_observed",
        "workercoordinator_claim_fence_observed",
        "organization_master_records_organization_record_observed"))


def test_multi_condition_packet_preserves_four_distinct_non_allow_predicates():
    reqs = [
        {"requirement_id": "missing", "capability_id": "native_source_math",
         "required_inputs": ["missing_source"]},
        {"requirement_id": "unsupported", "capability_id": "unknown_evaluator"},
        {"requirement_id": "version", "capability_id": "ecosystem_diagnostic",
         "version_compatible": False},
        {"requirement_id": "probe", "capability_id": "native_source_math",
         "authentic_runtime_evidence_required": True},
    ]
    packet = build_source_evidence_packet({}, reqs, evaluator_id="negative-controls")
    assert [row["qualification_disposition"] for row in packet["conditions"]] == [
        "MISSING_INPUT", "UNSUPPORTED", "VERSION_INCOMPATIBLE", "PROBE_REQUIRED"]
    assert [row["failed_predicate"] for row in packet["conditions"]] == [
        "REQUIRED_INPUT_PRESENT", "CAPABILITY_INSTALLED",
        "REQUESTED_VERSION_COMPATIBLE", "AUTHENTIC_RUNTIME_EVIDENCE_OBSERVED"]
    assert packet["source_qualification_complete"] is False
    assert all(row["bounded_adaptation"] is None for row in packet["conditions"])
    assert verify_source_evidence_packet({}, reqs, packet)


def test_packet_rejects_forged_authority_and_appended_receipts():
    manifest = {}
    reqs = [{"requirement_id": "math", "capability_id": "native_source_math"}]
    packet = build_source_evidence_packet(manifest, reqs, evaluator_id="math")
    for field in ("execution_authorized", "authentic_intr_disposition_observed",
                  "workercoordinator_claim_fence_observed",
                  "organization_master_records_organization_record_observed"):
        altered = deepcopy(packet)
        altered[field] = True
        assert not verify_source_evidence_packet(manifest, reqs, altered)
    altered = deepcopy(packet)
    altered["forged_runtime_receipt"] = {"disposition": "ALLOW"}
    assert not verify_source_evidence_packet(manifest, reqs, altered)
    altered = deepcopy(packet)
    altered["conditions"][0]["failed_predicate"] = "FORGED"
    assert not verify_source_evidence_packet(manifest, reqs, altered)


def test_packet_rejects_mutated_manifest_requirements_or_digest():
    manifest = {"payload": "a"}
    reqs = [{"requirement_id": "math", "capability_id": "native_source_math"}]
    packet = build_source_evidence_packet(manifest, reqs, evaluator_id="math")
    assert not verify_source_evidence_packet({"payload": "b"}, reqs, packet)
    assert not verify_source_evidence_packet(manifest, [
        {"requirement_id": "math", "capability_id": "ecosystem_diagnostic"}], packet)
    altered = deepcopy(packet)
    altered["source_packet_sha256"] = "0" * 64
    assert not verify_source_evidence_packet(manifest, reqs, altered)


def test_duplicate_or_empty_condition_ids_fail_closed():
    req = {"requirement_id": "duplicate", "capability_id": "native_source_math"}
    for requirements in ([], [req, req], [{"capability_id": "native_source_math"}]):
        try:
            build_source_evidence_packet({}, requirements, evaluator_id="test")
        except ValueError:
            pass
        else:
            raise AssertionError("invalid condition set accepted")


def test_legacy_source_packet_flag_name_still_verifies():
    from stegverse.organization_record_names import (
        LEGACY_SOURCE_PACKET_ORGANIZATION_RECORD_OBSERVED_FIELD,
        ORGANIZATION_RECORD_OBSERVED_FIELD,
    )
    from stegverse.source_evidence_packet import _hash

    manifest = {}
    reqs = [{"requirement_id": "math", "capability_id": "native_source_math"}]
    packet = build_source_evidence_packet(manifest, reqs, evaluator_id="math")
    legacy = {key: value for key, value in packet.items() if key != "source_packet_sha256"}
    legacy[LEGACY_SOURCE_PACKET_ORGANIZATION_RECORD_OBSERVED_FIELD] = legacy.pop(ORGANIZATION_RECORD_OBSERVED_FIELD)
    legacy["source_packet_sha256"] = _hash(legacy)
    assert verify_source_evidence_packet(manifest, reqs, legacy)
    escalated = deepcopy(legacy)
    escalated[LEGACY_SOURCE_PACKET_ORGANIZATION_RECORD_OBSERVED_FIELD] = True
    assert not verify_source_evidence_packet(manifest, reqs, escalated)
