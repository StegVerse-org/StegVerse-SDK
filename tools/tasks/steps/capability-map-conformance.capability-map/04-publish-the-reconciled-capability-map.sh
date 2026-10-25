python -m stegverse capability-map | tee /tmp/capability-map.json
python - <<'PY'
import json
report = json.load(open("/tmp/capability-map.json", encoding="utf-8"))
assert report["drift_count"] == 0, report
assert report["expired_exemption_count"] == 0, report
assert report["exemption_baseline_matches"] is True, report
assert report["grants_execution_authority"] is False
print("CAPABILITY_MAP_CONFORMANCE_PASS"
      f" invocable={report['evaluator_invocable_count']}"
      f" exempt={report['declared_exemption_count']}"
      f" drift={report['drift_count']}"
      f" expired={report['expired_exemption_count']}")
PY
