set -eu
python -B -m unittest tests.test_sv_llm_intr_roundtrip -v 2>&1 | tee "$RUNNER_TEMP/roundtrip.log"
# The positive path must have run, not skipped.
test -s "$SV_LLM_ROUNDTRIP_REPORT"
python - <<'PY'
import json, os
report = json.load(open(os.environ["SV_LLM_ROUNDTRIP_REPORT"], encoding="utf-8"))
assert report["all_legs_allow"] is True, report
assert report["evidence_class"] == "SAME_HOST_SCRATCH_CODE_PATH_CONFORMANCE_ONLY", report
pub = report["publisher_return"]
assert pub["sdk_return_binding_observed"] is True, pub
out = os.environ["SV_LLM_ROUNDTRIP_PUBLISHER_DIR"]
assert open(os.path.join(out, pub["pdf"]["path"]), "rb").read(5) == b"%PDF-", pub
print("SV_LLM_INTR_ROUNDTRIP_CONFORMANCE_PASS legs=%d" % len(report["legs"]))
PY
