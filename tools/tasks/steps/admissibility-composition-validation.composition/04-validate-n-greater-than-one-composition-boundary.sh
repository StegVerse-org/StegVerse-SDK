set -eu
cd /tmp/source
pytest -q \
  tests/test_admissibility_composition.py \
  tests/test_dynamic_admissibility.py \
  tests/test_admissibility_bundle.py \
  tests/test_admissibility_exchange.py
python - <<'PY'
from stegverse.admissibility import evaluate_admissibility_packet
from stegverse.admissibility_composition import evaluate_admissibility_composition

def component(object_id):
    return evaluate_admissibility_packet({
        'schema': 'stegverse.governed_admissibility.tester_output.v1',
        'tester': {'name_or_role': 'n2-ci', 'discipline_id': 'education_learning', 'domain_review_required': False},
        'test_object': {'object_id': object_id, 'object_type': 'model_response', 'summary': 'Individually admissible component.'},
        'route': {'recommended_route': ['transition_admissibility', 'receipt_replay', 'fail_closed'], 'tests_run': ['transition_admissibility'], 'route_deviation_reason': None},
        'classification': {
            'declared_intent': 'research_summary',
            'authority_source': 'AUTH-STATIC-001',
            'evidence_posture': 'receipt_backed',
            'replay_posture': 'receipt_backed',
            'consequence_level': 'low',
            'claim_limit': 'n2 composition CI fixture.',
        },
        'boundary': {
            'does_not_certify_domain_correctness': True,
            'does_not_replace_domain_review': True,
            'does_not_create_proof_authority': True,
        },
    }, strict=True)

a = component('A')
b = component('B')
assert a['classification']['decision'] == 'ALLOW_WITH_POSTURE'
assert b['classification']['decision'] == 'ALLOW_WITH_POSTURE'
joint = evaluate_admissibility_composition([a, b], composition_id='A+B', joint_consequence_level='critical')
assert joint['all_components_individually_admissible'] is True
assert joint['classification']['decision'] == 'FAIL_CLOSED'
assert joint['relation']['status'] == 'unresolved'
assert joint['relation']['basis'] == 'no_explicit_composition_admissibility_relation'
assert joint['separability']['component_admissibility_implies_composition_admissibility'] is False
print('ADMISSIBILITY_COMPOSITION_N2_NONSEPARABILITY_PASS')
PY
