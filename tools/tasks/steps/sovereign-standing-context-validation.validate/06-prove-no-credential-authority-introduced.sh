cd /tmp/source
python - <<'PY'
from pathlib import Path
text = '\n'.join(Path(p).read_text(encoding='utf-8') for p in (
    'stegverse/sovereign_validation_runtime.py',
    'stegverse/standing_execution_context.py',
))
for name in ('GITHUB_TOKEN', 'GH_TOKEN', 'TVC_PRIVATE_SOURCE_READ_TOKEN'):
    assert name not in text
print('SOVEREIGN_STANDING_CONTEXT_NON_AUTHORIZING_SOURCE_OK')
PY
