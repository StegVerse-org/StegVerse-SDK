from copy import deepcopy

from stegverse.manifest_plan import derive_execution_plan, verify_plan_lineage


def test_plan_binds_manifest_requirements_and_is_non_authorizing():
    manifest = {"payload": {"value": 7}}
    reqs = [{"requirement_id": "m1", "capability_id": "native_source_math"}]
    plan = derive_execution_plan(manifest, reqs)

    assert plan["execution_authorized"] is False
    assert plan["runtime_execution_observed"] is False
    assert plan["route_substitution_permitted"] is False
    assert plan["source_evidence_ceiling"] == "SOURCE_DERIVED_PLAN_ONLY"
    assert verify_plan_lineage(manifest, reqs, plan) is True


def test_supported_requirement_derives_bounded_exact_route_adaptation():
    plan = derive_execution_plan(
        {"payload": "x"},
        [{"requirement_id": "m2", "capability_id": "native_source_math"}],
    )
    step = plan["steps"][0]
    assert step["qualification_disposition"] == "SUPPORTED"
    assert step["adaptation"]["kind"] == "EXACT_DECLARED_CAPABILITY"
    assert step["adaptation"]["bounded"] is True
    assert step["adaptation"]["route_id"] == "stegverse.route.source-native-math.v1"


def test_non_allow_requirement_does_not_synthesize_adaptation():
    plan = derive_execution_plan(
        {},
        [{"requirement_id": "m3", "capability_id": "not-installed"}],
    )
    step = plan["steps"][0]
    assert step["qualification_disposition"] == "UNSUPPORTED"
    assert step["failed_predicate"] == "CAPABILITY_INSTALLED"
    assert step["adaptation"] is None


def test_probe_required_preserves_runtime_observation_boundary():
    plan = derive_execution_plan(
        {},
        [{
            "requirement_id": "m4",
            "capability_id": "native_source_math",
            "authentic_runtime_evidence_required": True,
        }],
    )
    step = plan["steps"][0]
    assert step["qualification_disposition"] == "PROBE_REQUIRED"
    assert step["runtime_probe_required"] is True
    assert plan["runtime_execution_observed"] is False


def test_manifest_mutation_breaks_lineage():
    manifest = {"payload": "a"}
    reqs = [{"requirement_id": "m5", "capability_id": "native_source_math"}]
    plan = derive_execution_plan(manifest, reqs)
    mutated = {"payload": "b"}
    assert verify_plan_lineage(mutated, reqs, plan) is False


def test_requirements_mutation_breaks_lineage():
    manifest = {"payload": "a"}
    reqs = [{"requirement_id": "m6", "capability_id": "native_source_math"}]
    plan = derive_execution_plan(manifest, reqs)
    changed = [{"requirement_id": "m6", "capability_id": "governance"}]
    assert verify_plan_lineage(manifest, changed, plan) is False


def test_plan_tampering_breaks_lineage():
    manifest = {"payload": "a"}
    reqs = [{"requirement_id": "m7", "capability_id": "native_source_math"}]
    plan = derive_execution_plan(manifest, reqs)
    tampered = deepcopy(plan)
    tampered["steps"] = tuple()
    assert verify_plan_lineage(manifest, reqs, tampered) is False


def test_top_level_plan_tampering_breaks_lineage_without_digest_change():
    manifest = {"payload": "a"}
    reqs = [{"requirement_id": "m8", "capability_id": "native_source_math"}]
    plan = derive_execution_plan(manifest, reqs)
    for field, replacement in (
        ("execution_authorized", True),
        ("runtime_execution_observed", True),
        ("route_substitution_permitted", True),
        ("source_evidence_ceiling", "AUTHENTIC_RUNTIME"),
        ("schema", "forged-schema"),
    ):
        tampered = deepcopy(plan)
        tampered[field] = replacement
        assert tampered["derived_plan_sha256"] == plan["derived_plan_sha256"]
        assert verify_plan_lineage(manifest, reqs, tampered) is False


def test_added_top_level_plan_field_breaks_lineage():
    manifest = {"payload": "a"}
    reqs = [{"requirement_id": "m9", "capability_id": "native_source_math"}]
    plan = derive_execution_plan(manifest, reqs)
    tampered = deepcopy(plan)
    tampered["forged_runtime_receipt"] = {"disposition": "ALLOW"}
    assert verify_plan_lineage(manifest, reqs, tampered) is False
