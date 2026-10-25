python - <<'PY' | tee /tmp/connector-capability-overlay.json
import json
from pathlib import Path
from stegverse.connector_capability_overlay import reconcile_overlay
from stegverse.evaluator_review_intr import REQUEST_SCHEMA
from stegverse.publisher_return_binding import PUBLISHER_RETURN_SCHEMA
from stegverse.review_publisher_transfer import TRANSFER_SCHEMA
payload = json.loads(Path(
    "data/universal-intr-connector-sdk-profiles.baseline.json"
).read_text(encoding="utf-8"))
registry = {
    "schema": payload["canonical_registry"]["registry_schema"],
    "state": payload["canonical_registry"]["registry_state"],
    "profiles": payload["profiles"],
}
report = reconcile_overlay(registry, bound_payload_schemas=(
    REQUEST_SCHEMA, TRANSFER_SCHEMA, PUBLISHER_RETURN_SCHEMA))
assert report["disposition"] == "ALLOW", report
assert report["failures"] == [], report
assert report["undeclared_sdk_subsystems"] == [], report
assert report["authority_effect"] == "NONE_SOURCE_RECONCILIATION_ONLY"
print(json.dumps(report, indent=2, sort_keys=True))
PY
