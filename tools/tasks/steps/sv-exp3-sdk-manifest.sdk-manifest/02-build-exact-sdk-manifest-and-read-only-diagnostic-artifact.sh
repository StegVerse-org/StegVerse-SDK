set -eu
cd /tmp/source
python -m unittest tests.test_mir_sv_exp3_manifest tests.test_capability_boundary_experiment_org_request tests.test_governed_deny_negative_conformance tests.test_universal_manifest_state_transition_runtime.UniversalManifestRuntimeTests.test_source_profile_deny_cannot_be_laundered_into_authentic_intr_result tests.test_universal_manifest_state_transition_runtime.UniversalManifestRuntimeTests.test_source_profile_terminal_fail_closed_cannot_retry tests.test_universal_manifest_state_transition_runtime.UniversalManifestRuntimeTests.test_nonterminal_diagnostic_requires_exact_result_bytes_and_publisher -v
python -m scripts.build_mir_sv_exp3_manifest --manifest /tmp/mir-sv-exp3.manifest.json --result /tmp/mir-sv-exp3.diagnostic-result.json
python -m json.tool /tmp/mir-sv-exp3.manifest.json >/dev/null
python -m json.tool /tmp/mir-sv-exp3.diagnostic-result.json >/dev/null
python -m scripts.build_capability_boundary_experiment_org_request --organization-root /tmp/mir-sv-exp3-org-request
sha256sum /tmp/mir-sv-exp3.manifest.json /tmp/mir-sv-exp3.diagnostic-result.json
echo 'Source/SDK diagnostic only; no resident physical or governed execution authority.'
