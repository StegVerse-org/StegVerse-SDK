stegverse run-manifest \
  --manifest /tmp/sdk-test1.manifest.json \
  --attempt-id "$(cat /tmp/readiness-attempt.txt)" \
  --readiness-evidence /tmp/sdk-test1.readiness-evidence.json \
  --readiness-keys /tmp/readiness-keys.json \
  --output /tmp/sdk-test1.result.json
python - <<'PY'
import json
result = json.load(open("/tmp/sdk-test1.result.json", encoding="utf-8"))
assert result["schema"] == "stegverse.sdk.manifest-transition-handoff/v1"
assert result["disposition"] == "ALLOW"
assert result["evaluation_boundary"] == "SDK_MANIFEST_HANDOFF"
assert result["destination_resolution_source"] == "CANONICAL_CONNECTOR_CAPABILITY_OVERLAY"
assert result["transport_performed_by_sdk"] is False
assert result["receiver_contacted"] is False
assert result["intr_admission_observed"] is False
assert result["far_side_transition_observed"] is False
assert result["consequence_committed"] is False
print("TEST1_RUN_MANIFEST_REACHED_GOVERNED_HANDOFF_BOUNDARY")
PY
