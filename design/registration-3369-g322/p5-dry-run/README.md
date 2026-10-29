# P5′ generation-ordering dry run (2026-10-29 ~15:10Z)

Local, read-only against Labs; authority_effect NONE. Nothing was pushed to StegVerse-Labs/.github.
Base: Labs branch `repair/stegapp-3291-apply-vocabulary-gen323-20261029` @ `f13383c` (the #3403 CI
repair; registry generation 323 — StegApp ingress vocabulary already applied there). Each step is one
`scripts/apply_task_record_data.py <file> --apply --tip-ref HEAD` on the previous step's commit.

| step | record data | plan | apply | generation | newly failing tests (registry/record/collision modules + sovereign-KV custody) |
|---|---|---|---|---|---|
| 1 | #3380 F1 `gen322-worker-task-resource-cost-linkage-row-record-reconciliation.v1.json` | ALLOW | ALLOW | 324 | 1: `test_exact_invocation_superseded_record_data.py::…::test_data_is_scoped_to_one_task_and_three_fields` — pins `registry_generation_base == tip`; the exact-invocation file must be re-based to 324 (mechanical) |
| 2 | #3380 F2 `gen323-dependency-blocker-shape-normalization.v1.json` | ALLOW | ALLOW | 325 | 1: `test_task_registry_sovereign_kv_event_custody.py::test_prompt_ceiling_successor_does_not_replace_canonical_runtime_owner` — asserts a bare dependency id; fixed by `0001-tests-accept-normalized-dependency-objects-in-the-so.patch` (applies on #3380 head `b70a499`; 4 passed before and after the apply) |
| 3 | main's `exact-invocation-superseded-by-cycle-closure.v1.json` (base re-pinned) | ALLOW | ALLOW | 326 | 5: the same module's precondition/plan tests (`test_preconditions_hold_on_the_base`, `test_plan_allows_exactly_tip_plus_one_and_writes_nothing`, `test_apply_supersedes_row_and_record_and_changes_nothing_else`, `test_row_fields_without_registration_fail_closed_with_six_fields`, `test_stale_before_value_fails_closed_and_restores`) — by design once the proposal is spent; retire/convert them in the apply commit, as #3403 did for the StegApp proposal |
| 4 | #3358 `payment-provider-authentic-ingress-components.v1.json` (PAYMENT + STEGHEALTH components) | ALLOW | ALLOW | 327 | 0 |
| 5 | #3369 option C `protocol-v1-3369-option-c-bind-org-batch-custody-ledger-readback.v1.json` | ALLOW | ALLOW | 328 | 0 |

End-state registry sha256 in `end-registry.sha256`. Option B (bind ingress conformance to
SDK-MANIFEST-ECOSYSTEM-TRANSITION-DISPOSITION-001) still plans FAIL_CLOSED
`RECORD_DATA_ROW_FIELD_BEFORE_MISMATCH` on `targets` until that lane reconciles its row/shard.

Notes for the owners
- `apply_task_record_data.py` checks before-values and tip+1, not the file's declared
  `registry_generation_base`; only the tests pin that field. So the queue is mechanical for every
  lane except the generation it lands on.
- Queue implied by this run: #3403 (323) → #3380 (324, 325; add the test patch) → exact-invocation
  supersede (326; retire its precondition tests) → #3358 (327; its 27-commit PR still needs the
  StegHealth authority ruling and a rebase, but the record-data step itself is clean) → #3369 option C
  (328). Nobody else should take 323–328 meanwhile.
