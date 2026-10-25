set -eu
cd /tmp/source
python -m pip install -e . pytest
python -m pytest -q \
  tests/test_sdk_usage_observability.py \
  tests/test_cli_sdk_usage_observability.py \
  tests/test_governed_operations.py
