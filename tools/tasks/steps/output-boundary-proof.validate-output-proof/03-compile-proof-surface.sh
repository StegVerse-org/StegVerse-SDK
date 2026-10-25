set -eu
cd /tmp/source
python -m py_compile \
  stegverse/output_boundary_proof.py \
  stegverse/output_boundary_cli.py \
  stegverse/sdk_surfaces.py \
  tests/test_output_boundary_proof.py
