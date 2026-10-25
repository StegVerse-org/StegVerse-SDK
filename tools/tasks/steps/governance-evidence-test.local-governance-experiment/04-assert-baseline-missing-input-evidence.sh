python - <<'PY'
import json
from pathlib import Path
s=json.loads(Path('evidence/elan/2026-09-10-governance-test/15-summary.json').read_text())
assert s['boundary_consumed'] is True
assert s['governance_state'] == 'DENY'
assert s['governance_reason'] == 'signal.inputs_incomplete'
assert s['executor_invoked'] is False
assert s['route_transition_count'] == 10
assert s['chain_verified'] is True
assert s['custody_status'] == 'RECORDED'
assert s['replay_deterministic_match'] is True
assert s['reconstruction_chain_verified'] is True
assert s['result_returned'] is True
PY
