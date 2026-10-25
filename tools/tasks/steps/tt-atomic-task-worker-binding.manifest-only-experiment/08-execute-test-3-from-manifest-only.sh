stegverse run-manifest --manifest /tmp/test3.manifest.json --output /tmp/test3.result.json \
  --attempt-id "$(cat /tmp/readiness-attempt.txt)" \
  --readiness-evidence /tmp/test3.readiness-evidence.json --readiness-keys /tmp/readiness-keys.json
python - <<'PY'
import json
r=json.load(open('/tmp/test3.result.json'))
assert r['schema'] == 'stegverse.sdk.manifest-transition-handoff/v1'
assert r['disposition'] == 'ALLOW'
assert r['evaluation_boundary'] == 'SDK_MANIFEST_HANDOFF'
assert r['destination_resolution_source'] == 'CANONICAL_CONNECTOR_CAPABILITY_OVERLAY'
assert r['transport_performed_by_sdk'] is False
assert r['receiver_contacted'] is False
assert r['intr_admission_observed'] is False
assert r['far_side_transition_observed'] is False
assert r['consequence_committed'] is False
print('MANIFEST_ONLY_TEST3_GOVERNED_HANDOFF_BOUNDARY_PASS')
PY
