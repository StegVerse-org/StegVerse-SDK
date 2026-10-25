python - <<'PY'
import json
from pathlib import Path
m=json.loads(Path('_site/wiki-source-manifest.json').read_text())
assert m['goal_task_id']=='SDK-PUBLIC-DEVELOPER-WIKI-001'
assert m['public_origin']=='https://sdk.stegverse.org/'
assert m['authority_effect']=='NONE_DOCUMENTATION_PROJECTION_ONLY'
assert len(m['sources']) >= 6
assert Path('_site/CNAME').read_text().strip()=='sdk.stegverse.org'
PY
