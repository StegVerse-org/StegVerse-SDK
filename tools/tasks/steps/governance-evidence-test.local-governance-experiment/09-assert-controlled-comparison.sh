python - <<'PY'
import json
from pathlib import Path
baseline=json.loads(Path('evidence/elan/2026-09-10-governance-test/15-summary.json').read_text())
silence=json.loads(Path('evidence/elan/2026-09-11-observed-silence-test/14-summary.json').read_text())
assert baseline['governance_state'] == 'DENY'
assert baseline['governance_reason'] == 'signal.inputs_incomplete'
assert silence['governance_state'] == 'ALLOW'
assert silence['governance_reason'] == 'ok'
PY
