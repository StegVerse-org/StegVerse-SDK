set -eu
cd /tmp/source
python -m unittest -v \
  tests.test_package_version_identity \
  tests.test_pypi_trusted_publishing_contract
