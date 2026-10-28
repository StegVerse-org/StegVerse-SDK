set -eu
cd /tmp/source
python -m unittest -v \
  tests.test_publisher_return_binding \
  tests.test_publisher_return_materialization
echo 'PUBLISHER_SDK_RETURN_BINDING_SOURCE_VALIDATION=PASS'
echo 'SDK_RETURN_MATERIALIZATION_SOURCE_VALIDATION=PASS'
echo 'AUTHENTIC_SDK_RETURN_RUNTIME_INPUT_OBSERVED=false'
echo 'PUBLISHER_RUNTIME_EXECUTION_OBSERVED=false'
echo 'LLM_ADAPTER_TRANSITION_OBSERVED=false'
echo 'INTERLOCK_INTR_EGRESS_OBSERVED=false'
echo 'FAR_SIDE_TRANSITION_OBSERVED=false'
