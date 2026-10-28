python - <<'PY'
import importlib.util, json, os
spec = importlib.util.spec_from_file_location("gpf", "tools/governance_product_finish.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
verdict = m.finish_verdict(os.environ["FINISH_ROOT"])
keys = ("disposition", "predicates") + m.SIX
shown = {k: verdict.get(k) for k in keys}
with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as summary:
    summary.write("### Finish verdict\n```json\n" + json.dumps(shown, indent=2, sort_keys=True) + "\n```\n")
print(json.dumps(shown, sort_keys=True))
PY
