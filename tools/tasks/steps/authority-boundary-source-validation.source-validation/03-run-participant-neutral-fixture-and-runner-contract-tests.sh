set -eu
cd /tmp/source
python -m pip install --disable-pip-version-check -q pytest
python experiments/authority_boundary_preservation/validate_fixture.py
python -m pytest -q \
  tests/test_authority_boundary_preservation_experiment.py \
  tests/test_authority_boundary_sovereign_runner.py
