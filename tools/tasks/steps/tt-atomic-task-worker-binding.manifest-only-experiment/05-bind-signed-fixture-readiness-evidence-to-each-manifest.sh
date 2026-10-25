python - <<'PY'
import json
from datetime import datetime, timedelta, timezone
from tests.test_manifest_readiness_gate import ATTEMPT, KEY, KEY_ID, _all_ready
observed = datetime.now(timezone.utc) - timedelta(seconds=5)
for name in ('test1', 'test2', 'test3', 'task4'):
    manifest = json.load(open(f'/tmp/{name}.manifest.json', encoding='utf-8'))
    evidence = _all_ready(manifest, at=observed)
    json.dump(evidence, open(f'/tmp/{name}.readiness-evidence.json', 'w'), indent=2, sort_keys=True)
json.dump({KEY_ID: KEY}, open('/tmp/readiness-keys.json', 'w'))
open('/tmp/readiness-attempt.txt', 'w').write(ATTEMPT)
print('FIXTURE_READINESS_EVIDENCE_SIGNED_NOT_LIVE_OBSERVATION')
PY
