set -eu
cd /tmp/source
pytest -q \
  tests/test_mhia_module_manifest_schema.py \
  tests/test_mhia_capability_graph.py \
  tests/test_mhia_reference_firmware.py \
  tests/test_mhia_reference_hal.py \
  tests/test_mhia_procurement_gate.py
echo 'MHIA_SOURCE_VALIDATION_PASS'
echo 'This hosted validation grants no execution, credential, publication, transition, procurement, or runtime authority.'
