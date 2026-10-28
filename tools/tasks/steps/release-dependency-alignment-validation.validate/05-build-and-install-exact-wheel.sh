set -eu
cd /tmp/source
python -m build --wheel
python -m venv /tmp/alignment-venv
/tmp/alignment-venv/bin/python -m pip install --disable-pip-version-check --no-input dist/*.whl
