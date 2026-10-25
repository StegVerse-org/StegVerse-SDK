set -eu
cd /tmp/source
python -m pip install -q pytest
python -m unittest tests.test_manifest_builder tests.test_review_publisher_transfer -v
python -m pytest -q tests/test_governance_reference_graph.py
python -m pytest -q tests/test_governance_reference_projection.py
python -m pytest -q tests/test_worker_participation_history.py
python -m pytest -q tests/test_micro_node_commit_time_experiment.py
python -m pytest -q tests/test_untrusted_dependency_review.py
python -m pytest -q tests/test_component011_receipt_compatibility.py
PYTHONPATH=. python validation/governance_reference_graph_console.py
python -m unittest tests.test_state_transition_evidence
python -m unittest tests.test_external_interlock_ingress_binding
python -m unittest tests.test_workspace_resource_consumer
python -m pytest -q tests/test_machine_contract.py tests/test_external_framework_manifest_first.py
python -m unittest tests.test_external_framework_runner
python -m unittest tests.test_generic_manifest_processing_contract
python -m unittest tests.test_governance_navigation
python -m unittest tests.test_governance_ingress_runtime
python -m unittest tests.test_route_resolution
python -m unittest tests.test_cli_preformatted_manifest
python -m py_compile \
  stegverse/worker_participation_history.py \
  stegverse/micro_node_commit_time_experiment.py \
  stegverse/untrusted_dependency_review.py \
  stegverse/component011_receipt_compatibility.py \
  stegverse/manifest_builder.py \
  stegverse/governance_reference_graph.py \
  stegverse/governance_reference_projection.py \
  stegverse/evaluator_manifest_builder.py \
  stegverse/external_framework_runner.py \
  stegverse/manifest_contract.py \
  stegverse/state_transition_evidence.py \
  stegverse/external_interlock_ingress_binding.py \
  stegverse/workspace_resource_consumer.py \
  stegverse/route_resolution.py \
  stegverse/governance_ingress_runtime.py \
  stegverse/evaluator_console.py
