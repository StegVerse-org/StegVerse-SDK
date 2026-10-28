python - <<'PY'
import importlib.util, json, os
spec = importlib.util.spec_from_file_location("gpf", "tools/governance_product_finish.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
binding = m.release_ref_binding(".", os.environ["HEAD_COMMIT"])
commit = binding.get("release_commit", "")
with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as out:
    out.write(f"release_commit={commit}\n")
with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as summary:
    summary.write("### Finish ref binding\n```json\n" + json.dumps(binding, indent=2, sort_keys=True) + "\n```\n")
print(json.dumps(binding, sort_keys=True))
PY
