python - <<'PY'
import json
p=json.load(open('/tmp/pinned-source-integration.json'))
assert p['stegtalk_source_loaded'] is True
assert p['stegtalk_st031_loaded'] is True
assert p['stegtalk_st032_loaded'] is True
assert p['knowledgevault_source_loaded'] is True
assert p['knowledgevault_native_runtime_journal_loaded'] is True
assert p['selected_bearer'] == 'stegtalk-ip'
assert p['fallback_edge_id'] == 'source-integration:phone'
assert p['edge_runtime_callable_executed'] is True
assert p['edge_execution_outcome'] == 'DELIVERED'
assert p['edge_duplicate_dispatch_suppressed'] is True
assert p['kv_duplicate_execution_observation_suppressed'] is True
assert p['ambiguous_action'] == 'VERIFY_EXTERNALLY'
assert p['confirmed_failure_action'] == 'TRY_FALLBACK'
assert p['kv_selection_reconstructed_after_restart'] is True
assert p['kv_lease_reconstructed_after_restart'] is True
assert p['kv_edge_execution_receipt_reconstructed_after_restart'] is True
assert p['kv_recovery_decision_reconstructed_after_restart'] is True
assert p['loopback_test_only'] is True
assert p['physical_transport_proven'] is False
assert p['production_activation_proven'] is False
print(p['selection_sha256'])
print(p['edge_execution_receipt_sha256'])
PY
