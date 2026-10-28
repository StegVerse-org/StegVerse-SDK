set -eu
test -z "${GITHUB_TOKEN:-}"
test -z "${GH_TOKEN:-}"
test -z "${TV_IDENTITY_KEY:-}"
test -z "${TVC_SECRET:-}"
echo 'EXECUTION_BOUNDARY_CREDENTIAL_BOUNDARY_PASS'
