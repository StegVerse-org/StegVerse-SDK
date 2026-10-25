set -euo pipefail
python - <<'PY'
from stegverse.release_index import RELEASE_API
assert RELEASE_API.startswith('https://api.github.com/repos/StegVerse-Labs/StegCore/releases')
PY
