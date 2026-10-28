python - <<'PY'
from pathlib import Path
text = Path('stegverse/tvc_provider_probe_bridge.py').read_text()
assert 'credential_authority' in text
assert 'TV/TVC' in text
assert 'provider_operation_authority_transferred' in text
assert 'authority_effect' in text
assert 'NONE' in text
assert 'issue(' not in text
assert 'oauth' in text.lower()
print('WORKSPACE_TVC_PROVIDER_PROBE_BRIDGE=PASS')
PY
