set -eu
cd /tmp/source
python -m unittest -q tests.test_llm_connection
python - <<'PY'
from stegverse.sdk_surfaces import get_sdk_surface
surface = get_sdk_surface("connect my llm")
assert surface is not None
assert surface["id"] == "connect-llm"
assert "stegverse-connect-llm" in surface["command"]
assert surface["authority_effect"] == "NONE"
print("SDK_CONNECT_LLM_SOURCE_VALIDATION_PASS")
PY
