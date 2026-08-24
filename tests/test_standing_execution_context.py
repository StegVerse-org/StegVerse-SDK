import inspect

from stegverse.interlock_transition import canonical_hash as interlock_hash
from stegverse.sovereign_validation_runtime import run_sovereign_validation
from stegverse.standing_execution_context import build_standing_execution_context
from tests.test_portable_governance_verifier import _bundle


def test_pre_steggate_bundle_builds_non_authorizing_standing_context():
    bundle = _bundle()
    context = build_standing_execution_context(bundle)
    assert context["standing_required"] is True
    evidence = context["standing_evidence"]
    assert evidence["required"] is True
    assert evidence["expected_interlock"]["package_id"] == bundle["package_id"]
    assert evidence["expected_interlock"]["transition_id"] == bundle["transition_id"]
    assert evidence["expected_interlock"]["run_id"] == bundle["run_id"]
    assert evidence["expected_interlock"]["participant_id"] == "reference-participant"
    assert evidence["expected_interlock"]["ingress_interlock_hash"] == interlock_hash(bundle["ingress_interlock"])
    assert evidence["spe_envelope"] == bundle["spe_envelope"]
    assert evidence["spe_receipt"] == bundle["spe_receipt"]
    assert evidence["steggate_bridge"] == bundle["steggate_bridge"]
    assert context["authority"]["sdk_authority"] == "NONE"
    assert context["authority"]["execution_authorized"] is False


def test_sovereign_runtime_exposes_standing_context_parameter_and_passes_it_to_canonical_transaction():
    signature = inspect.signature(run_sovereign_validation)
    assert "declared_execution_context" in signature.parameters
    source = inspect.getsource(run_sovereign_validation)
    assert "declared_execution_context=declared_execution_context" in source
    assert '"declared_execution_context_consumed_by_canonical_runtime"' in source
