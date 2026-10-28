set -eu
test -z "${GITHUB_TOKEN:-}"
test -z "${GH_TOKEN:-}"
echo 'MCP_SOURCE_VALIDATION_PASS'
echo 'Canonical governed integration is assigned to tasks/SDK-MCP-CANONICAL-VALIDATION-009.json.'
echo 'The hosted runner must not receive a GitHub/private-repository token merely to materialize the private Master Records production package.'
echo 'This validation job has no runtime, release, credential, or production activation authority.'
