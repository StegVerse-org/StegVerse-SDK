set -eu
cd /tmp/source
python -m py_compile \
  stegverse/public_inspection.py \
  stegverse/sovereign_validation_runtime.py \
  stegverse/product_processing.py \
  stegverse/ecosystem_diagnostic_runtime.py \
  stegverse/route_resolution.py \
  stegverse/native_source_math.py \
  stegverse/governance_navigation.py \
  stegverse/manifest_contract.py \
  stegverse/manifest_builder.py \
  stegverse/governance_ingress_runtime.py \
  stegverse/governance_ingress_cli.py \
  stegverse/cli.py \
  stegverse/evaluation_boundary_verifier.py \
  stegverse/current_basis.py \
  scripts/run_cross_framework_current_basis_v04.py \
  scripts/package_cross_framework_current_basis_results.py \
  scripts/validate_public_inspection_request.py \
  scripts/build_evaluation_boundary_artifact_manifest.py \
  scripts/build_evaluation_boundary_owner_packet.py \
  scripts/build_evaluation_boundary_response_packet.py \
  scripts/run_evaluation_boundary_r3.py
