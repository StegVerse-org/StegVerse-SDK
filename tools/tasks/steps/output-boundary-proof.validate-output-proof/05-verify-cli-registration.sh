set -eu
cd /tmp/source
python - <<'PY'
import pathlib
text = pathlib.Path('pyproject.toml').read_text()
assert 'stegverse-output-proof = "stegverse.output_boundary_cli:main"' in text
from stegverse.sdk_surfaces import get_sdk_surface
surface = get_sdk_surface('output-boundary-proof')
assert surface is not None
assert surface['authority_effect'] == 'NONE'
print('OUTPUT_BOUNDARY_SDK_SURFACE_REGISTERED')
PY
