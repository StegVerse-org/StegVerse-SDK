cat > /tmp/sdk-task4-group.processor-request.json <<'JSON'
{
  "schema": "stegverse.sdk.purpose-bound-worker-group-test.v1",
  "test_id": "SDK-TASK4-THREE-WORKER-CONCURRENT-001",
  "purpose": "Partition one bounded manifested task across three concurrent purpose-bound workers and return only records after all workers retire.",
  "required_capability": "text.integrity_summary",
  "worker_count": 3,
  "partition_ids": ["A", "B", "C"],
  "group_wall_clock_budget_seconds": 30,
  "per_worker_lifetime_policy": {
    "mode": "DERIVED_COST_TASK_DELAY_BUDGET",
    "production_recompute_required": true,
    "decomposition_target": "RECORDS_ENABLED_PACKET",
    "retirement_condition": "PURPOSE_COMPLETED_OR_FAILED_OR_BUDGET_EXHAUSTED",
    "cost_analysis": {
      "expected_compute_units": 3,
      "external_cost_usd_ceiling": 0,
      "task_cost_basis": "one deterministic partition of a three-worker bounded manifested task"
    },
    "time_budget_seconds": {
      "expected_task_execution": 6,
      "known_delay": 4,
      "inferred_unknown_delay_reserve": 8,
      "records_decomposition": 7,
      "safety_reserve": 5
    },
    "derived_max_lifetime_seconds": 30,
    "unknown_delay_inference_basis": "bounded reserve for local scheduling, processing, and records decomposition"
  },
  "expected_evidence_fields": [
    "worker_count_matches_manifest",
    "distinct_worker_identities",
    "overlap_measurement_available",
    "partition_reconstruction_exact",
    "all_workers_records_only",
    "all_workers_retired",
    "continued_authority_false",
    "group_result_binding"
  ]
}
JSON
