set -euo pipefail
python -m stegverse.portable_packages inspect --deployment-class NS > /tmp/ns.json
python - <<'PY'
import json
data = json.load(open('/tmp/ns.json', encoding='utf-8'))
assert data['deployment_class'] == 'NS'
assert data['required_archive_formats'] == ['zip', 'tar.gz']
assert data['installation_creates_node_membership'] is False
assert data['authority_effect'] == 'NONE'
assert data['download_active'] is False
sovereignty = data['single_host_sovereignty']
assert sovereignty['physical_host_topology'] == 'ONE_SOVEREIGN_PHYSICAL_HOST'
assert sovereignty['additional_physical_machine_required'] is False
assert sovereignty['third_party_machine_required'] is False
assert sovereignty['third_party_process_host_required'] is False
assert sovereignty['third_party_scheduler_required'] is False
assert sovereignty['third_party_state_host_required'] is False
assert sovereignty['third_party_control_plane_executor_required'] is False
assert sovereignty['independent_validation_mechanism'] == 'SAME_HOST_ISOLATED_LOGICAL_BOUNDARIES'
assert sovereignty['credential_authority'] == 'TV/TVC'
assert sovereignty['non_tv_tvc_secret_or_token_allowed'] is False
PY
if python -m stegverse.portable_packages download --deployment-class NS --format tar.gz --output /tmp/ns.tar.gz; then
  echo 'download unexpectedly succeeded without governed artifact' >&2
  exit 1
fi
