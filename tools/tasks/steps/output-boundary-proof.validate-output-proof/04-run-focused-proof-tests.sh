set -eu
cd /tmp/source
python -m unittest tests.test_output_boundary_proof -v
