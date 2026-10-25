set -eu
cd /tmp/source
python - <<'PY'
import json
from datetime import datetime, timedelta, timezone
from stegverse.external_framework_runner import prepare_external_framework_manifest
from tests.test_manifest_readiness_gate import ATTEMPT, KEY, KEY_ID, _all_ready
load = lambda path: json.load(open(path, encoding='utf-8'))
draft = prepare_external_framework_manifest(
    data=load('inspection/examples/elan-relational-state-test1.json'),
    source_framework='ELAN',
    source_output_id='elan-emotional-ambiguity-silence-test-001',
    processor_request=load('inspection/examples/elan-governance-request.example.json'),
    evaluation_declaration=load('inspection/examples/elan-evaluation-declaration-test1.json'),
    data_class='elan.relational-state.v1',
    return_depth='full-trace',
    created_at='2026-10-10T00:00:00Z',
)
evidence = _all_ready(draft, at=datetime.now(timezone.utc) - timedelta(seconds=5))
json.dump(evidence, open('/tmp/elan-readiness-evidence.json', 'w'), indent=2, sort_keys=True)
json.dump({KEY_ID: KEY}, open('/tmp/readiness-keys.json', 'w'))
open('/tmp/readiness-attempt.txt', 'w').write(ATTEMPT)
print('FIXTURE_READINESS_EVIDENCE_SIGNED_NOT_LIVE_OBSERVATION')
PY
