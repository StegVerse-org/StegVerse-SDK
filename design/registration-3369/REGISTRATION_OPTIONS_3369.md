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
