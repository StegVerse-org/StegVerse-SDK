python - <<'PY'
import json
repo=json.load(open('/tmp/communication-edge-demo.json'))
installed=json.load(open('/tmp/communication-edge-installed.json'))
assert installed == repo
assert installed['sdk_simulation_only'] is True
assert installed['authority_granted'] is False
assert installed['execution_performed'] is False
assert installed['selection']['selected_bearer'] == 'stegtalk-ip'
assert installed['recovery_scenarios']['ambiguous_after_dispatch']['action'] == 'VERIFY_EXTERNALLY'
assert installed['recovery_scenarios']['confirmed_pre_side_effect_failure']['action'] == 'TRY_FALLBACK'
print(installed['demo_sha256'])
PY
