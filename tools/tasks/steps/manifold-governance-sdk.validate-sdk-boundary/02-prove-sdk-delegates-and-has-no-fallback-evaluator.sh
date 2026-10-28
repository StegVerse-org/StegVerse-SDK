set -eu
python -m unittest tests.test_manifold_governance_sdk_boundary -v
python -m py_compile stegverse/manifold_governance.py stegverse/sdk_surfaces.py stegverse/cli.py
python - <<'PY'
from pathlib import Path
source=Path('stegverse/manifold_governance.py').read_text()
assert 'stegcore.manifold_governance import PopulationTransition, govern_manifold_action' in source
assert 'PRODUCTION_RUNTIME = "stegcore.manifold_governance.govern_manifold_action"' in source
assert 'no fallback or parallel evaluator' in source
print('SDK_MANIFOLD_DELEGATION_BOUNDARY_PASS')
PY
