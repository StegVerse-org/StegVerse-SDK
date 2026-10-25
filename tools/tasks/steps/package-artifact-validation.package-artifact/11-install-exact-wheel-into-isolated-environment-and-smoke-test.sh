set -eu
cd /tmp/source
expected_version="$(python - <<'PY'
import pathlib, tomllib
print(tomllib.loads(pathlib.Path('pyproject.toml').read_text())['project']['version'])
PY
)"
python -m venv /tmp/sdk-wheel-venv
/tmp/sdk-wheel-venv/bin/python -m pip install --disable-pip-version-check --no-input dist/*.whl
/tmp/sdk-wheel-venv/bin/python - <<'PY' "$expected_version"
import importlib.metadata
import sys
import stegverse
assert importlib.metadata.version('stegverse-sdk') == sys.argv[1]
print('SDK_WHEEL_IMPORT_PASS', sys.argv[1])
PY
/tmp/sdk-wheel-venv/bin/stegverse --help >/tmp/stegverse-help.txt
test -s /tmp/stegverse-help.txt
/tmp/sdk-wheel-venv/bin/stegverse-verify-governance --help >/tmp/stegverse-verify-help.txt
test -s /tmp/stegverse-verify-help.txt
/tmp/sdk-wheel-venv/bin/stegverse-governance-exchange --help >/tmp/stegverse-exchange-help.txt
test -s /tmp/stegverse-exchange-help.txt
echo 'SDK_WHEEL_CONSOLE_SMOKE_PASS'
