python - <<'PY'
import json
from datetime import datetime, timedelta, timezone
from tests.test_manifest_readiness_gate import ATTEMPT, KEY, KEY_ID, _all_ready
manifest = json.load(open('/tmp/sdk-test1.manifest.json', encoding='utf-8'))
evidence = _all_ready(manifest, at=datetime.now(timezone.utc) - timedelta(seconds=5))
json.dump(evidence, open('/tmp/sdk-test1.readiness-evidence.json', 'w'), indent=2, sort_keys=True)
json.dump({KEY_ID: KEY}, open('/tmp/readiness-keys.json', 'w'))
open('/tmp/readiness-attempt.txt', 'w').write(ATTEMPT)
print('FIXTURE_READINESS_EVIDENCE_SIGNED_NOT_LIVE_OBSERVATION')
PY
