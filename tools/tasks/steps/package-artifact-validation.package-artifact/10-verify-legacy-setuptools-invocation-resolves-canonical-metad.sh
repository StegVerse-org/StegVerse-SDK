set -eu
cd /tmp/source
expected_name="$(python - <<'PY'
import pathlib, tomllib
print(tomllib.loads(pathlib.Path('pyproject.toml').read_text())['project']['name'])
PY
)"
expected_version="$(python - <<'PY'
import pathlib, tomllib
print(tomllib.loads(pathlib.Path('pyproject.toml').read_text())['project']['version'])
PY
)"
test "$(python setup.py --name)" = "$expected_name"
test "$(python setup.py --version)" = "$expected_version"
echo 'SETUP_PY_CANONICAL_METADATA_PASS'
