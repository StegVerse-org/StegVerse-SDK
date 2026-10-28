set -eu
cd /tmp/source
python -m pytest -q tests/test_elyria_framework_adapter.py
