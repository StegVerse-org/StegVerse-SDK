set -eu
python - <<'PY'
import json
from pathlib import Path

result = json.loads(Path('/tmp/elan-sdk-submission.json').read_text())
assert result['schema'] == 'stegverse.sdk.external-framework-submission.v1'
assert result['status'] == 'SUBMISSION_READY'
assert result['execution_performed'] is False
assert result['manifest_receipt_id'] is None
manifest = result['manifest']
assert manifest['payload']['test_id'] == 'elan-emotional-ambiguity-silence-test-001'
assert manifest['extensions']['source_data_class'] == 'elan.relational-state.v1'
assert manifest['extensions']['evaluation_declaration']
assert 'evaluation_declaration' not in manifest['extensions']['stegverse_governance_request']
assert manifest['processing']['capability'] == 'governance'
assert manifest['processing']['route_id'] == 'stegverse.route.canonical-governed.v1'
assert manifest['return_projection']['mode'] == 'ALL'

# Current canonical source resolves the existing organization boundary.
# This remains SDK-local handoff evidence and does not prove receiver observation.
assert result['evidence_class'] == 'SDK_LOCAL_MANIFEST_HANDOFF'
# SDK#368: the handoff exists only because the draft qualified READY on
# supplied invocation-bound evidence; readiness never claims runtime ALLOW.
assert result['executable'] is True
assert result['readiness_qualification']['qualification'] == 'READY'
assert result['readiness_qualification']['runtime_allow_claimed'] is False
handoff = result['handoff']
assert handoff['state'] == 'MANIFESTED_FOR_INTERLOCK_INTR_HANDOFF'
assert handoff['disposition'] == 'ALLOW'
assert handoff['evaluation_boundary'] == 'SDK_MANIFEST_HANDOFF'
assert handoff['destination_resolution_source'] == 'CANONICAL_CONNECTOR_CAPABILITY_OVERLAY'
assert result['manifest_declared_destination']['profile_id'] == 'sdk-manifest-ingress'
assert handoff['receiver_availability_required'] is False
assert handoff['awaits_external_machine'] is False
assert handoff['receiver_contacted'] is False
assert handoff['organization_receipt_observed'] is False
print('EXTERNAL_FRAMEWORK_PUBLIC_SUBMISSION_VALIDATION_PASS')
PY
