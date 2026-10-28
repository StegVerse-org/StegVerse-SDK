set -eu
cd /tmp/source
pytest -q \
  tests/test_dynamic_admissibility.py \
  tests/test_dynamic_admissibility_public_api.py \
  tests/test_admissibility_bundle.py \
  tests/test_admissibility_exchange.py \
  tests/test_admissibility_receipts.py \
  tests/test_admissibility_replay.py
python - <<'PY'
import copy
from stegverse.admissibility import evaluate_admissibility_packet

base = {
    'schema': 'stegverse.governed_admissibility.tester_output.v1',
    'tester': {
        'name_or_role': 'matrix-maturity-ci',
        'discipline_id': 'education_learning',
        'domain_review_required': False,
    },
    'test_object': {
        'object_id': 'N1-CANDIDATE-001',
        'object_type': 'model_response',
        'summary': 'Candidate held constant across T0/T1.',
    },
    'route': {
        'recommended_route': ['transition_admissibility', 'receipt_replay', 'fail_closed'],
        'tests_run': ['transition_admissibility'],
        'route_deviation_reason': None,
    },
    'classification': {
        'declared_intent': 'research_summary',
        'authority_source': 'AUTH-STATIC-001',
        'evidence_posture': 'receipt_backed',
        'replay_posture': 'receipt_backed',
        'consequence_level': 'low',
        'claim_limit': 'Bounded n=1 matrix maturity validation.',
    },
    'boundary': {
        'does_not_certify_domain_correctness': True,
        'does_not_replace_domain_review': True,
        'does_not_create_proof_authority': True,
    },
}
t0 = base
t1 = copy.deepcopy(base)
t1['classification']['consequence_level'] = 'critical'
r0 = evaluate_admissibility_packet(t0, strict=True)
r1 = evaluate_admissibility_packet(t1, strict=True)
assert r0['classification']['decision'] == 'ALLOW_WITH_POSTURE'
assert r0['relation']['maturity_class'] == 'known_admissible_with_posture'
assert r1['classification']['decision'] == 'FAIL_CLOSED'
assert r1['classification']['allowed_next_state'] == 'fail_closed'
assert r1['relation']['status'] == 'unresolved'
assert r1['relation']['maturity_class'] == 'under_development'
assert r1['local_receipt_hash'] != r0['local_receipt_hash']
print('ADMISSIBILITY_MATRIX_MATURITY_N1_PASS')
PY
