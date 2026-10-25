set -eu
test -z "${GITHUB_TOKEN:-}"
test -z "${GH_TOKEN:-}"
cd /tmp/source
python -m unittest \
  tests.test_mcp_production_artifact.MCPProductionArtifactUnitTests \
  tests.test_mcp_request_boundary.MCPRequestBoundaryTests -v
