python - <<'PY' | tee -a /tmp/experiment-stage-results.log
import json
for path in ['/tmp/test1.result.json','/tmp/test2.result.json','/tmp/test3.result.json','/tmp/task4.result.json']:
    r=json.load(open(path))
    assert r['schema']=='stegverse.sdk.manifest-transition-handoff/v1'
    assert r['disposition']=='ALLOW'
    assert r['evaluation_boundary']=='SDK_MANIFEST_HANDOFF'
    print('FOUR_STAGE_GENERIC_GOVERNED_BOUNDARY_PASS')
PY
