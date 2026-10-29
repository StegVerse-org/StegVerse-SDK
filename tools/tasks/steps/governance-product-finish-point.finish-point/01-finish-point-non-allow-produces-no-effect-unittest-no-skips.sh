set -o pipefail
python -m unittest tests.test_governance_product_finish_point -v 2>&1 | tee /tmp/finish-point.log
if grep -Eq 'skipped|expected failure' /tmp/finish-point.log; then
  echo "::error::a finish-point test was skipped; skips are never accepted"; exit 1
fi
