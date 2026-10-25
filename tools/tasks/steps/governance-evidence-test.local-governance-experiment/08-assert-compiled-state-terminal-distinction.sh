python - <<'PY'
import json
from pathlib import Path
s=json.loads(Path('evidence/elan/2026-09-11-compiled-state-governance-matrix/03-summary.json').read_text())
assert s['upstream_parameters_reinterpreted'] is False
no_signal=s['no_signal']
silence=s['observed_silence']
assert no_signal['event_3']['predecessor_event'] == 2
assert no_signal['missing_inputs'] == ['event_3:no_signal']
assert no_signal['governance_state'] == 'DENY'
assert no_signal['governance_reason'] == 'signal.inputs_incomplete'
assert silence['event_3']['predecessor_event'] == 2
assert silence['event_3']['state_transition']['from_event'] == 2
assert silence['event_3']['state_transition']['to'] == 'NON_EMISSION_OBSERVED'
assert silence['event_3']['state_transition']['trigger'] == 'OBSERVATION_WINDOW_CLOSED_WITHOUT_EMISSION'
assert silence['missing_inputs'] == []
assert silence['governance_state'] == 'ALLOW'
assert silence['governance_reason'] == 'ok'
PY
