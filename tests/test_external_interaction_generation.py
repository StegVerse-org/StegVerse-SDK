"""A generation of an external-organization interaction declares its own identity.

The first-generation contract left four things implicit in whichever runtime
consumed it: the far side's organization and service, the transition the
request references, and the prefix its transport packet is named with.
`StegVerse-org/.github` held them as module constants, so the consuming runtime
was the only place a second question could be asked from -- and asking one meant
editing a runtime, which is processing selected by something other than the
admitted manifest.

These cases cover the generic contract that replaces those constants. Nothing is
defaulted: a manifest that omits a declaration is refused rather than completed
against a constant.

They also cover the chain. Each generation stays a frozen one-shot -- no
standing query, because a durable standing coupling is what the
least-stable-micronode policy denies -- and a generation beyond the first
declares the one it continues by the digest of that manifest, the digest of the
result that was reviewed before augmenting, and the oscillator count at which it
was observed. Order comes from that count, never from a host clock reading.

Source validation only. Nothing here transports, mints a receipt or grants
authority.
"""
from __future__ import annotations

import pytest

from stegverse.external_interlock_bootstrap import (
    GENERATION_MANIFEST_SCHEMA,
    REQUEST_SCHEMA,
    build_external_interaction_generation_manifest,
    build_external_interaction_generation_request,
    canonical_sha256,
    non_prescriptive_knowledge_policy,
    successor_predecessor_binding,
    validate_external_interaction_generation_manifest,
    validate_external_interaction_generation_request,
)

DECLARATION = {
    "manifest_id": "SDK-TASK-REGISTRY-DISCLOSURE-001",
    "experiment_id": "TASK-REGISTRY-DISCLOSURE-001",
    "operation": "REQUEST_CURRENT_TASK_REGISTRY",
    "objective": "Return the current task registry generation and the artifacts the current task names.",
    "source_organization_id": "StegVerse-SDK-Evaluator",
    "target_entity_id": "StegVerse-org",
    "target_organization": "StegVerse-org",
    "target_service": "stegverse-org.llm-adapter",
    "transition_reference": "svorg.task-registry.disclosure.v1",
    "packet_id_prefix": "taskreg-disclosure-",
}


def manifest(**overrides):
    declaration = {**DECLARATION, "generation": 1, "predecessor": None}
    declaration.update(overrides)
    return build_external_interaction_generation_manifest(**declaration)


def request(**overrides):
    declaration = {**DECLARATION, "generation": 1, "predecessor": None}
    declaration.update(overrides)
    return build_external_interaction_generation_request(
        authority_ref="TV/TVC:test", **declaration)


def binding_from(first, result=None, epoch=4096):
    return successor_predecessor_binding(
        predecessor_manifest=first, predecessor_result=result or {}, heartbeat_epoch=epoch)


# --- every identity is declared ------------------------------------------------

def test_a_built_manifest_carries_every_declaration_and_its_digest():
    m = manifest()
    assert m["schema"] == GENERATION_MANIFEST_SCHEMA
    assert m["target"]["organization"] == "StegVerse-org"
    assert m["target"]["service"] == "stegverse-org.llm-adapter"
    assert m["transition_reference"] == "svorg.task-registry.disclosure.v1"
    assert m["packet_id_prefix"] == "taskreg-disclosure-"
    body = dict(m)
    assert body.pop("manifest_sha256") == canonical_sha256(body)


def test_the_builder_emits_only_what_its_own_validator_accepts():
    validate_external_interaction_generation_manifest(manifest())


@pytest.mark.parametrize("field", [
    "manifest_id", "experiment_id", "operation", "objective",
    "transition_reference", "packet_id_prefix",
])
def test_an_omitted_declaration_is_refused_rather_than_defaulted(field):
    with pytest.raises(ValueError):
        manifest(**{field: "   "})


@pytest.mark.parametrize("field", ["target_entity_id", "target_organization", "target_service"])
def test_an_omitted_far_side_declaration_is_refused(field):
    with pytest.raises(ValueError):
        manifest(**{field: ""})


def test_a_tampered_declaration_fails_the_digest():
    m = manifest()
    m["target"]["service"] = "stegverse-org.boundary-diagnostic"
    with pytest.raises(ValueError):
        validate_external_interaction_generation_manifest(m)


def test_the_knowledge_policy_cannot_become_prescriptive():
    m = manifest()
    m["knowledge_policy"]["prescribe_formalism"] = True
    m["manifest_sha256"] = canonical_sha256(
        {k: v for k, v in m.items() if k != "manifest_sha256"})
    with pytest.raises(ValueError):
        validate_external_interaction_generation_manifest(m)


def test_the_neutral_policy_declares_every_key_false():
    policy = non_prescriptive_knowledge_policy()
    assert policy
    assert all(value is False for value in policy.values())


def test_authority_is_never_transferred_by_a_declaration():
    m = manifest()
    assert m["authority_transfer"] is False
    assert m["authority_effect_resolution"] == "DERIVED_FROM_APPLICABLE_TRANSITION_ELEMENTS"


def test_a_first_generation_manifest_is_not_accepted_as_a_generation_manifest():
    """The frozen first contract is finished, not a degraded form of this one."""
    m = manifest()
    m["schema"] = "stegverse.external_organization.interaction_manifest.v1"
    with pytest.raises(ValueError):
        validate_external_interaction_generation_manifest(m)


# --- the chain of generations --------------------------------------------------

def test_a_first_generation_declares_no_predecessor():
    assert manifest()["predecessor"] is None


def test_a_first_generation_declaring_a_predecessor_is_refused():
    with pytest.raises(ValueError):
        manifest(generation=1, predecessor={
            "generation": 0, "manifest_sha256": "a" * 64,
            "result_sha256": "b" * 64, "heartbeat_epoch": 32})


def test_a_later_generation_must_declare_the_one_it_continues():
    with pytest.raises(ValueError):
        manifest(generation=2, predecessor=None)


def test_an_absent_predecessor_key_is_not_read_as_a_first_generation():
    """An unstated chain position is refused; reading it as first is defaulting."""
    m = manifest()
    del m["predecessor"]
    with pytest.raises(ValueError):
        validate_external_interaction_generation_manifest(m)


def test_a_reviewed_result_binds_the_successor_to_what_was_actually_read():
    first = manifest()
    result = {"state": "RESPONSE_PERSISTED", "registry_generation": 7}
    binding = binding_from(first, result)
    assert binding == {"generation": 1,
                       "manifest_sha256": first["manifest_sha256"],
                       "result_sha256": canonical_sha256(result),
                       "heartbeat_epoch": 4096}
    second = manifest(generation=2, predecessor=binding,
                      manifest_id="SDK-TASK-REGISTRY-DISCLOSURE-002")
    assert second["predecessor"]["manifest_sha256"] == first["manifest_sha256"]
    assert second["predecessor"]["result_sha256"] == canonical_sha256(result)


def test_a_successor_binding_refuses_a_predecessor_whose_digest_does_not_hold():
    first = manifest()
    first["objective"] = "something else"
    with pytest.raises(ValueError):
        binding_from(first)


def test_a_generation_claiming_the_wrong_predecessor_generation_is_refused():
    binding = binding_from(manifest())
    binding["generation"] = 5
    with pytest.raises(ValueError):
        manifest(generation=2, predecessor=binding)


@pytest.mark.parametrize("field", ["manifest_sha256", "result_sha256"])
def test_a_predecessor_reference_that_is_not_a_digest_is_refused(field):
    binding = binding_from(manifest())
    binding[field] = "not-a-digest"
    with pytest.raises(ValueError):
        manifest(generation=2, predecessor=binding)


def test_order_comes_from_an_oscillator_count_not_a_clock_reading():
    binding = binding_from(manifest())
    binding["heartbeat_epoch"] = 0
    with pytest.raises(ValueError):
        manifest(generation=2, predecessor=binding)


def test_a_predecessor_carrying_an_unknown_field_is_refused():
    binding = binding_from(manifest())
    binding["observed_at"] = "2026-10-02T00:00:00Z"
    with pytest.raises(ValueError):
        manifest(generation=2, predecessor=binding)


def test_a_generation_below_one_is_refused():
    with pytest.raises(ValueError):
        manifest(generation=0, predecessor=None)


def test_a_boolean_is_not_a_generation():
    with pytest.raises(ValueError):
        manifest(generation=True, predecessor=None)


# --- the request envelope is unchanged ----------------------------------------

def test_only_the_manifest_is_versioned_because_only_it_generalized():
    envelope = request()
    assert envelope["schema_version"] == REQUEST_SCHEMA
    assert envelope["payload"]["manifest"]["schema"] == GENERATION_MANIFEST_SCHEMA


def test_the_request_binds_the_exact_manifest_it_carries():
    envelope = validate_external_interaction_generation_request(request())
    m = envelope["payload"]["manifest"]
    assert envelope["bindings"]["manifest_sha256"] == m["manifest_sha256"]
    assert envelope["bindings"]["experiment_id"] == m["experiment_id"]
    assert envelope["bindings"]["target_entity_id"] == m["target"]["entity_id"]


def test_the_request_claims_no_delivery_and_mints_no_receipt():
    envelope = request()
    assert envelope["authority_transfer"] is False
    assert envelope["sdk_mints_intr_receipt"] is False
    assert envelope["sdk_claims_delivery"] is False


def test_an_operation_the_manifest_did_not_declare_is_refused():
    envelope = request()
    envelope["operation"] = "REQUEST_SOMETHING_ELSE"
    with pytest.raises(ValueError):
        validate_external_interaction_generation_request(envelope)


def test_a_rebound_manifest_digest_is_refused():
    envelope = request()
    envelope["bindings"]["manifest_sha256"] = "c" * 64
    with pytest.raises(ValueError):
        validate_external_interaction_generation_request(envelope)


def test_a_request_without_an_authority_reference_is_refused():
    with pytest.raises(ValueError):
        build_external_interaction_generation_request(
            authority_ref="  ", **{**DECLARATION, "generation": 1, "predecessor": None})
