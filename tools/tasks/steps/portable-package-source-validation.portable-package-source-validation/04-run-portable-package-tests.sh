set -euo pipefail
python -m pytest tests/test_portable_packages.py tests/test_portable_dual_archive.py -q
