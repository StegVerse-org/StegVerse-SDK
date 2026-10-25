set -eu
cd /tmp/source
python -m compileall -q \
  stegverse/mcp_reference_server.py \
  stegverse/mcp_transport.py \
  stegverse/mcp_governance.py \
  stegverse/mcp_navigation.py \
  stegverse/mcp_cli.py \
  stegverse/sovereign_validation_runtime.py \
  stegverse/sdk_surfaces.py \
  tests/test_mcp_production_artifact.py \
  tests/test_mcp_request_boundary.py
