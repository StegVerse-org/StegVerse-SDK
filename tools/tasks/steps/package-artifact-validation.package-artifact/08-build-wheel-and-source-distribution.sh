set -eu
cd /tmp/source
python -m build
test "$(find dist -maxdepth 1 -name '*.whl' | wc -l)" -eq 1
test "$(find dist -maxdepth 1 -name '*.tar.gz' | wc -l)" -eq 1
