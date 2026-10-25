python - <<'PY'
from pathlib import Path
text = Path('stegverse/active_probe_execution.py').read_text()
assert 'authority_effect' in text
assert 'NONE' in text
consumer = Path('stegverse/workspace_resource_consumer.py').read_text()
assert 'readiness_before_probe' in consumer
assert 'active_probe_evidence' in consumer
assert 'intr_receipt_minted' in consumer
print('WORKSPACE_ACTIVE_PROBE=PASS')
PY
