python - <<'PY'
import json
from pathlib import Path
p=Path('evidence/elan/2026-09-16-cross-evaluation')
s=json.loads((p/'16-summary.json').read_text())
c=json.loads((p/'15-cross-evaluation.json').read_text())
assert s['a3_a4_separate_transitions'] is True
assert c['elan_native_resolution']['a3_a4_separate_boundaries_exposed'] is False
assert c['stegverse_native_resolution']['a3_separate_transition'] is True
assert c['stegverse_native_resolution']['a4_separate_transition'] is True
assert c['stegverse_native_resolution']['a3_semantic_interpretation'] == 'UNRESOLVED'
assert c['stegverse_native_resolution']['a4_semantic_interpretation'] == 'UNRESOLVED'
assert c['earliest_representation_divergence']['origin'] == 'OBSERVATION_BOUNDARY_AND_STATE_TRANSITION_RESOLUTION'
assert s['governance_state'] == 'ALLOW'
assert s['governance_reason'] == 'ok'
assert s['boundary_consumed'] is True
assert s['executor_invoked'] is True
assert s['chain_verified'] is True
assert s['custody_status'] == 'RECORDED'
assert s['replay_deterministic_match'] is True
assert s['reconstruction_chain_verified'] is True
assert s['result_returned'] is True
assert s['native_architectures_normalized'] is False
PY
