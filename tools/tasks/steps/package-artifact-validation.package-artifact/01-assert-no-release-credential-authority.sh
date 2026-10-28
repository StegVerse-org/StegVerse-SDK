set -eu
test -z "${GITHUB_TOKEN:-}"
test -z "${GH_TOKEN:-}"
test -z "${PYPI_API_TOKEN:-}"
echo 'PACKAGE_VALIDATION_CREDENTIAL_BOUNDARY_PASS'
