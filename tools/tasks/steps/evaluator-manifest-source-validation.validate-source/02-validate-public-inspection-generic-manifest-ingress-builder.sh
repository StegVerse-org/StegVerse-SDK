set -eu
cd /tmp/source
python scripts/validate_public_inspection_request.py inspection/examples/example-request.json
python scripts/validate_public_inspection_request.py inspection/examples/governed-test-request.json
python scripts/validate_public_inspection_request.py inspection/examples/multilane-noninterference-request.json
python scripts/validate_public_inspection_request.py inspection/examples/cross-framework-current-basis-request.draft.json
python -m unittest tests.test_public_inspection_request
python -m unittest tests.test_generic_manifest_processing_contract
python -m unittest tests.test_manifest_builder
python -m unittest tests.test_evaluator_manifest_multilane_noninterference
python -m unittest tests.test_cross_framework_current_basis_manifest
python -m unittest tests.test_current_basis_sdk
python -m unittest tests.test_cross_framework_current_basis_execution
python -m unittest tests.test_cross_framework_current_basis_result_packaging
python -m unittest tests.test_public_inspection_governed_binding
python -m unittest tests.test_governance_ingress_runtime
python -m unittest tests.test_product_processing
python -m unittest tests.test_ecosystem_diagnostic_processor
python -m pytest -q tests/test_manifest_plan.py tests/test_sdk_15_unrelated_evaluator_evidence.py tests/test_source_evidence_packet.py
python -m unittest tests.test_route_resolution
python -m unittest -v tests.test_native_source_math
python -m unittest tests.test_cli_preformatted_manifest
python -m unittest tests.test_evaluation_boundary_contract
python -m unittest tests.test_evaluation_boundary_owner_packet
python -m pytest -q tests/test_evaluation_boundary_response_packet.py tests/test_evaluation_boundary_r3_run_harness.py
