python - <<'PY'
import json
from pathlib import Path
s=json.loads(Path('evidence/elan/2026-09-11-observed-silence-test/14-summary.json').read_text())
assert s['event_3_representation'] == 'OBSERVABLE_NON_EMISSION_STATE_TRANSITION'
assert s['event_3_intent'] == 'UNDETERMINED'
assert s['event_3_semantic_interpretation'] == 'UNRESOLVED'
assert s['event_3_in_missing_inputs'] is False
assert s['boundary_consumed'] is True
assert s['governance_state'] == 'ALLOW'
assert s['governance_reason'] == 'ok'
assert s['executor_invoked'] is True
assert s['route_transition_count'] == 10
assert s['chain_verified'] is True
assert s['custody_status'] == 'RECORDED'
assert s['replay_deterministic_match'] is True
assert s['reconstruction_chain_verified'] is True
assert s['result_returned'] is True
PY
