set -eu
cd /tmp/source
python - <<'PY'
from pathlib import Path
paths = [Path('stegverse/output_boundary_proof.py'), Path('stegverse/output_boundary_cli.py')]
forbidden = ('OPENAI_' + 'API_KEY', 'ANTHROPIC_' + 'API_KEY', 'DEEPSEEK_' + 'API_KEY')
for path in paths:
    text = path.read_text()
    for marker in forbidden:
        assert marker not in text, f'{marker} forbidden in {path}'
print('OUTPUT_BOUNDARY_PROVIDER_CREDENTIAL_DEPENDENCY_NONE')
PY
