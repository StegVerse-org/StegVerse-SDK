# #3369 registration: owner-decision inputs

Base: StegVerse-Labs/.github `origin/main` e0d2970, Registry generation 321. Local only; nothing pushed, no COSV, claim, fence or receipt exists. All files under `scratchpad/reg3369/`.

## Candidate scope (minimal)

- ID: `PROTOCOL-V1-MINIMUM-PACKET-CONFORMANCE-001`; issue #3369, parent #3368 (issue lineage; `parent_task_id` null because #3368 is not a Goal Task).
- Repos: `StegVerse-Labs/.github`, `StegVerse-org/StegVerse-SDK`.
- Components: ingress path `resident-runtime/sdk_manifest_crossing.py`, `org-boundary/runtime/process_boundary.py`, `resident-runtime/organization_manifest_ingress.py`, ledger readback `org-kernel/organization-ledger`, fixtures `org-kernel/organization-ledger/fixtures/protocol-v1-conformance/`.
- Outcome: every non-ALLOW carries the six fields; no effect committed. Finish point: `python -m unittest tests.test_protocol_v1_conformance_fixtures` at exact head.

## Overlap table (evaluator at gen 321 + direct record inspection)

| Existing goal | State | Real scope overlap | Evidence | Evaluator (components under mutation = candidate's) |
|---|---|---|---|---|
| SDK-MANIFEST-ECOSYSTEM-TRANSITION-DISPOSITION-001 | ACTIVE / CHECKED_OUT | **Real.** Both candidate repos; component `allow-deny-fail-closed` is the six-field outcome; its I12 extension names `organization_manifest_ingress.py`; 6 of 8 committed #3369 refusal fixtures name it `owning_existing_goal` | registry.json:20552-20561 (targets), :20653 (ingress path); shard:161; `cases/n1,n3,n5-n8.json:9` | Baseline already STOP_COLLISION (6 lineage siblings under root SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003). Candidate adds 2 hard: the two omitted shards below. Row/shard diverge: row repo `StegVerse-Labs/.github`, shard `StegVerse-org/.github` (shard:17-21) |
| ORGANIZATION-BATCH-CUSTODY-REPLAY-001 | ACTIVE / HANDOFF_READY (not owner-held) | **Real, ledger readback only.** `current_truth` names `organization_manifest_ingress.py::_organization_receipt_read_back`; `n2-replay.json:21` names it owner of the replay-refusal gap | registry.json:10559-10565, :10810; shard has **no `targets`** | Baseline COORDINATE_CONVERGENCE (5 adjacencies). Evaluator cannot see component overlap because it declares no targets |
| STEGVERSE-CANONICAL-WORK-COORDINATION-001 | PROPOSED | **Name adjacency only.** None of its 27 components (registry:88-115) are the candidate's; as PROPOSED it is never a collision candidate for others | registry.json:15-115 | Baseline STOP_COLLISION with 4 (SS-KV-SKAP-SOCIAL-RELEASE-001, TASK-REGISTRY-SESSION-RETURN-ORCHESTRATION-001 and the two lineage children below) — matches the owner handoff; not caused by #3369 |
| GITHUB-UNIVERSAL-GOVERNANCE-PRODUCT-001 | not registered | none | `i1-goal-manifests/MANIFEST.json:109-137` (NO_SHARD_NO_ROW) | STOP_NOT_REGISTERED |
| CANONICAL-WORK-END-TO-END-CYCLE-CLOSURE-001 (omitted shard, collision guard) | ACTIVE / CHECKED_OUT | **Real.** Components `sdk-manifest-ingress`, `organization-transition-ledger`, `workercoordinator-claim-fence`; both repos; source_ref `org-runtime/interlock-intr.json` | shard:9-10, 28-40 | Hard collision whenever the candidate names `sdk-manifest-ingress` |
| CANONICAL-WORK-EXACT-INVOCATION-EVIDENCE-RECONCILIATION-001 (omitted shard) | ACTIVE / CHECKED_OUT | **Real** on `organization-ledger-readback` | shard:9-10, 23-31; #3358 supersedes it (`data/registry-record-data/exact-invocation-superseded-by-cycle-closure.v1.json`, gen 322) | Hard collision on that component until #3358 lands |

Candidate itself: `STOP_NOT_REGISTERED` either way (`evaluator/candidate-*.json`). Full dispositions: `evaluator/`.

**Finding:** the evaluator matches component *strings*. The same scope with #3369-specific names (`name-distinct` variant) produces zero component overlap and `plan` returns ALLOW. Whether that is honest scoping or renaming around owners is the owner's ruling, not the tool's.

## Plan receipts

- `plan-receipt.primary.json` (honest vocabulary, adjacency declared): schema, record, scope seal and COSV derivation pass; **FAIL_CLOSED `REGISTRY_COLLISION_CHECKIN_NOT_CONTINUE`**, head STOP_COLLISION, hard = END-TO-END, EXACT-INVOCATION, SDK-MANIFEST-{ECOSYSTEM, COLLAB-INGRESS, IDENTITY-ROUTING}; candidates also ORGANIZATION-BATCH-CUSTODY-REPLAY-001 (adjacency). Expected result.
- `plan-receipt.name-distinct-variant.json`: **ALLOW**, successor gen 322, derived vector `10100000010000` (plan output, not an assigned COSV), five derived files, null-ref claim request.
- Record-data (plan-only): B `RECORD_DATA_ROW_FIELD_BEFORE_MISMATCH` (shard targets differ from row); C **ALLOW** gen 322; D fails on B's defect. C simulated in scratch: validators accept, but ORGANIZATION-BATCH-CUSTODY-REPLAY-001 becomes STOP_COLLISION against EXACT-INVOCATION until #3358 merges.

## Option map

| | Authority needed | `plan` returns now | Generation vs #3358/#3373 (both 322) | Best case | Worst case |
|---|---|---|---|---|---|
| **A** NEW_IDENTITY | Owner collision ruling naming the 5 hard IDs; owner-approved manifest; optional `scripts/adjacency_ruling.py` file | FAIL_CLOSED collision (honest names) / ALLOW (distinct names) | Third consumer of 322; serial rebase after both | Clean ID, own COSV, finish point sealed to the conformance test | Owner refuses renamed scope; or ID lands and immediately STOP_COLLISIONs on every check-in |
| **B** bind to SDK-MANIFEST-ECOSYSTEM… | SDK-MANIFEST owner (CHECKED_OUT lane) first reconciles shard `targets.repositories`; then one record-data apply | FAIL_CLOSED before-mismatch | One bump after the shard fix | Fixtures already route 6/8 refusals here; no new identity, no new COSV | Inherits a lane that is already STOP_COLLISION with 6 lineage siblings; ledger-readback half has no owner |
| **C** bind to ORGANIZATION-BATCH-CUSTODY-REPLAY-001 | Custody owner approval; #3358 merged first | ALLOW (322) | Must land after #3358 (which is 322) → 323 | Smallest admissible change today; gives that goal evaluator-visible targets for the first time | Ingress conformance (most of #3369) is mis-homed under a custody goal; STOP_COLLISION if applied before #3358 |
| **D** split B + C | Both owners + shard fix + #3358 | FAIL_CLOSED (B defect) | Two edits, one bump, after #3358 | Each half under the owner the fixtures already name; no new identity | Two approvals, two lanes, one of them pre-blocked |

**Recommendation: D, sequenced C then B.** The committed fixtures already assign ownership this way (n2 → custody; the rest → SDK-MANIFEST). Order: (1) #3358 merges; (2) apply C (ALLOW today, one bump); (3) SDK-MANIFEST owner reconciles shard `targets.repositories` in its own lane, then apply B. Keep A in reserve only if an owner rules the work a distinct goal; then use the honest-vocabulary manifest plus an adjacency ruling, not the renamed variant.

---

## 2026-10-28 refresh: generation 322 (origin/main 0fff5f5)

Local only; nothing pushed, no comments, no COSV, claim, fence or receipt exists. Files under `scratchpad/reg3369-g322/` (same layout as `reg3369/`; `upstream/` holds the #3358/#3380 record-data files and their plan outputs).

### What changed on main (e0d2970 -> 0fff5f5)

- #3373 merged: `EC9-WHEN-AI-SERVICES-FAIL-PUBLICATION-001` registered (PROPOSED, COSV `10100000110000`, seal `control/goal-scope-seals/EC9-...json`), Registry generation **321 -> 322**. Its targets are `Executive_Rhetoric_Ledger`, `Site`, `SV-LLM/Ecosystem_Chat` with paper-publication components: no repository or component overlap with the candidate, and PROPOSED rows are never collision candidates.
- #3373 also re-based `data/registry-record-data/exact-invocation-superseded-by-cycle-closure.v1.json` on main to base 322 (note text; the fence is on the merged generation, not that field) and re-pinned the I1 registration fixtures to 322.
- #3387 merged (StegApp ingress vocabulary): adds `stegapp-ephemeral-composition-ingress-vocabulary.v1.json` (proposal only, base 321, not applied); no Registry generation change.
- `pr/3358` (head 9a936cc) still carries its own applied generation 322 (PAYMENT/STEGHEALTH targets) and does not contain 0fff5f5: it now conflicts with main's 322 and **must re-derive at 323**. Plan-only at tip 322: `payment-provider-authentic-ingress-components.v1.json` -> ALLOW 323 (records PAYMENT-PROVIDER-AUTHENTIC-INGRESS-001, STEGHEALTH-ECOSYSTEM-FAILURE-REMEDIATION-001); `exact-invocation-superseded-by-cycle-closure.v1.json` -> ALLOW 323. Both are applicable, but only one of them can take 323.
- `pr/3380` (head 42ea658, registry still 321): `gen321-worker-task-resource-cost-linkage-row-record-reconciliation.v1.json` plan-only at tip 322 -> **ALLOW 323**, `records_changed: []` (row-only restore, record already equal). Its `apply_before` follow-up (`gen322-dependency-blocker-shape-normalization.v1.json`) would then be 324. The "gen321" in the file name is stale; the proposal itself still applies.

### Plan results at 322 (`plan-receipt.*.json`, `record-data-plan.*.json`)

| Input | Gen 321 | Gen 322 | Change |
|---|---|---|---|
| NEW_IDENTITY, honest vocabulary (`control/.../protocol-v1-minimum-packet-conformance-001.json`, digest `sha256:0068b14c...`) | FAIL_CLOSED `REGISTRY_COLLISION_CHECKIN_NOT_CONTINUE`, STOP_COLLISION | **same**; schema, record, scope seal and COSV derivation pass; hard = END-TO-END-CYCLE-CLOSURE, EXACT-INVOCATION, SDK-MANIFEST-{COLLAB-INGRESS, ECOSYSTEM, IDENTITY-ROUTING}; candidates + ORGANIZATION-BATCH-CUSTODY-REPLAY-001 | none (EC9 is not a candidate) |
| NEW_IDENTITY, name-distinct variant | ALLOW, successor 322 | **ALLOW, successor 323**, derived vector `10100000010000`, null-ref claim request | successor generation only |
| Option B (`...option-b-...`) | FAIL_CLOSED `RECORD_DATA_ROW_FIELD_BEFORE_MISMATCH` | **same**: row `StegVerse-Labs/.github` vs shard `StegVerse-org/.github` in `targets.repositories` | none; shard fix still owner-side |
| Option C (`...option-c-...`) | ALLOW 322 | **ALLOW 323**, record ORGANIZATION-BATCH-CUSTODY-REPLAY-001 | generation only |
| Option D | FAIL_CLOSED (B defect) | **same** | none |

Evaluator (`evaluator/*.json`, observed generation 322): SDK-MANIFEST-ECOSYSTEM-TRANSITION-DISPOSITION-001 honest -> STOP_COLLISION with the same 8 hard IDs as at 321; baseline the same 6. ORGANIZATION-BATCH-CUSTODY-REPLAY-001 honest -> STOP_COLLISION with the same 5; baseline COORDINATE_CONVERGENCE with the same 5 adjacencies. STEGVERSE-CANONICAL-WORK-COORDINATION-001 honest -> same 7. Candidate -> STOP_NOT_REGISTERED either way. **No hard-collision set changed with the EC9 row present.**

Scratch simulations (`evaluator/simulated-*.json`; applied in the throwaway worktree, reverted, nothing committed):

- Option C applied at 322 -> 323 **before** #3358: ORGANIZATION-BATCH-CUSTODY-REPLAY-001 becomes STOP_COLLISION against CANONICAL-WORK-EXACT-INVOCATION-EVIDENCE-RECONCILIATION-001 (unchanged finding).
- #3358's exact-invocation supersede applied first (322 -> 323), then option C (323 -> 324): ORGANIZATION-BATCH-CUSTODY-REPLAY-001 returns **COORDINATE_CONVERGENCE, hard = []**, the same 5 adjacencies as its baseline. Ordering is the whole difference.

### finish_point (owner-decision packet item)

Schema (`schemas/canonical-task-registration-request.schema.json`) requires only four non-empty strings; the stricter contract is `scripts/adjacency_ruling.py` `ADDRESSABLE`: `acceptance_test` must read `<org>/<repo>:<path/to/test.py>[::<Class>::<test>]`, one test file, so condition (b) can be recomputed from it. The gen-321 draft's prose `acceptance_test` would have been refused `ADJACENCY_RULING_FINISH_POINT_NOT_ADDRESSABLE` the moment a ruling was attached. Changed to:

- `acceptance_test`: `StegVerse-Labs/.github:tests/test_protocol_v1_conformance_fixtures.py` (addressable; 12 tests, all pass at 0fff5f5 under `python -m unittest`; `.stegverse/test-sets.json` set id `tests/test_protocol_v1_conformance_fixtures.py`, inputs `org-kernel/organization-ledger/fixtures/protocol-v1-conformance/**`, `org-runtime/interlock-intr.json`, `resident-runtime/organization_manifest_ingress.py`, `resident-runtime/sdk_manifest_crossing.py`).
- `predicate`: unchanged, `PROTOCOL_V1_MINIMUM_PACKET_CONFORMANCE_PROFILE_HELD_AT_EXACT_HEAD`.
- `verifier_entrypoint`: now maps every `expected_evidence_predicates` entry to a real node id (PositiveCaseTest / NegativeCaseTest x2 / ReplayCaseTest / FixtureShapeTest x2 / exact-byte digest test + retained CI run) and names the ledger-readback test `tests/test_organization_ledger_same_store_readback.py::test_ingress_readback_reads_the_declared_git_store` (exercises `organization_manifest_ingress._organization_receipt_read_back` against the declared git store; passes in isolation and in-file) for `PROTOCOL_V1_ORGANIZATION_LEDGER_READBACK_INDEPENDENTLY_OBSERVED_OR_SIX_FIELD_NOT_ATTEMPTED`.
- `lowest_supported_mode`: `E0`, unchanged.

Observation while verifying: `tests/test_organization_ledger_same_store_readback.py::test_refusal_record_is_appended_and_found_again_on_the_declared_git_store` fails in isolation (`ImportError: cannot import name 'build_state_receipt' from partially initialized module 'workers.canonical_state_transition_custody'`, circular import) and passes when the file runs whole; it is not in the finish point. The KV packet text itself was not available locally; this section works from the task's summary of it plus the schema and the ruling contract.

Both manifests validate against the schema and both `plan` runs accept the seal (`GOAL_SCOPE_SEALED` passes; the honest one fails only at the collision check-in).

### Sequencing now that #3373 landed

1. **#3358 re-derives at 323** (its branch registry says 322, same number as main's EC9 bump). Both of its record-data files plan ALLOW at tip 322; it should carry the exact-invocation supersede, because that is the edit the rest of this issue depends on. Whether PAYMENT/STEGHEALTH ride the same bump or take 324 is the #3358 owner's call.
2. **#3380** is independent of #3369 and plans ALLOW at 322 -> 323 too; it competes with #3358 for 323 and rebases serially behind it (324/325).
3. **Option C** applies at the first tip after the exact-invocation supersede (324 if #3358 takes 323 and #3380 is after, otherwise later). Applied before it, C is admissible but immediately puts ORGANIZATION-BATCH-CUSTODY-REPLAY-001 into STOP_COLLISION; applied after it, the same edit leaves that goal at COORDINATE_CONVERGENCE with no hard collision (simulated above).
4. **Option B / D** wait on the SDK-MANIFEST owner's shard `targets.repositories` fix in its CHECKED_OUT lane; nothing in 321 -> 322 moved that.
5. **Option A** (NEW_IDENTITY) is unchanged: FAIL_CLOSED on the same five hard IDs with honest vocabulary; the manifest is now ruling-ready (addressable finish point) if an owner rules the work distinct and writes the class D adjacency ruling. The three CHECKED_OUT SDK-MANIFEST siblings and END-TO-END-CYCLE-CLOSURE remain hard collisions a ruling cannot clear.

Recommendation unchanged: D sequenced C then B, with C queued behind #3358's exact-invocation supersede.
