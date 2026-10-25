set -euo pipefail
tmp="$(mktemp -d)"
git init -q --bare "$tmp/org.git"
tree=$(printf '' | git -C "$tmp/org.git" mktree)
head=$(git -C "$tmp/org.git" -c user.name=t -c user.email=t@t commit-tree "$tree" -m seed)
git -C "$tmp/org.git" update-ref refs/stegverse/organization-ledger "$head"
python3 - "$head" "$tmp/manifest.json" <<'PY'
import json, sys
m = json.load(open(".stegverse/transition-ledger/initialization-manifest.v1.json"))
m["expected_organization_ledger_head"] = sys.argv[1]
open(sys.argv[2], "w").write(json.dumps(m, indent=2, sort_keys=True) + "\n")
PY
digest="sha256:$(sha256sum "$tmp/manifest.json" | cut -d' ' -f1)"
python3 scripts/initialize_repository_ledger.py --manifest "$tmp/manifest.json" \
  --manifest-sha256 "$digest" --hb-epoch 1 \
  --ledger-location "git+$tmp/org.git#refs/stegverse/organization-ledger" > "$tmp/plan.json"
python3 -c "import json,sys; d=json.load(open(sys.argv[1])); assert d['disposition']=='ALLOW' and d['result']=='PLANNED_NO_WRITE' and d['consequence_committed'] is False, d; print('REPOSITORY_LEDGER_INITIALIZATION_PLAN_ALLOW', d['genesis_receipt']['receipt_sha256'])" "$tmp/plan.json"
test "$(git -C "$tmp/org.git" rev-parse refs/stegverse/organization-ledger)" = "$head"
