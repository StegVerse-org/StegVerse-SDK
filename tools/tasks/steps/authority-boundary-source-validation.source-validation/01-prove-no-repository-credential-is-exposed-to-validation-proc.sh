set -eu
test -z "${GITHUB_TOKEN:-}"
test -z "${GH_TOKEN:-}"
echo 'credential_authority=TV/TVC'
echo 'github_token_runtime_authority=NONE'
echo 'production_activation_role=NONE'
