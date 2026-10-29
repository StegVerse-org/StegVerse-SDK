# Ingress gap option map: `SDK:ManifestIngress` (StegVerse-Labs/.github @ bbd84af)

Scope: the four `spec_gap`s that b81a35d (the corrective patch to #3375) records on `organization_manifest_ingress.py::receive` (`OMI`), `sdk_manifest_crossing.py::cross` (`SMC`) and `node_standing.py` (`NS`). This map is design input only. Evidence class: SOURCE_READ. Nothing here was executed, admitted or granted.

## Findings that change the framing

| # | Finding | Source |
|---|---|---|
| F1 | **Gap 4 is half a gap.** Idempotent redelivery is the specified behaviour: "On a redelivery of a recorded request, the organization receipt names the packets of the delivery that committed it… Exact retries (E1) are unchanged." The durable queue depends on it: "redelivering an event is the exact retry the ledgers already make idempotent". #3369 asks only for "no duplicate effect", and the #3369 doc is itself "NOT ADMITTED". | `docs/STEGDB_ORGANIZATION_ROLE_VERSION_PROPAGATION_MIRROR_HANDOFF.md:163-167` (I-10); `OMI:1293`; `PROTOCOL_V1_CONFORMANCE_SHARE_PACKET.md:4,16` |
| F2 | **The real replay defect is a duplicate effect, which the spec_gap does not name.** `cross()` (`OMI:1041`) runs the endpoint (`process_boundary.py:98`) *before* the recorded-transition lookup (`OMI:1118-1121`). So a redelivery processes again, and only the ledger append is deduplicated. A replay of a governance request also reaches `request_governance_decision` again (`OMI:1174`). | code order |
| F3 | **Gap 1 is half a gap.** `cross()` building the origin (`SMC:174`) is the anti-forgery property, not the defect: this binding is intra-organization, and caller-editable origin is "FORBIDDEN_AS_AUTHORITATIVE_EVIDENCE". Checking `node_ref` for presence only is also required: node/device identity may not gate (`device_attestation_gate: NONE_PROHIBITED`, `node_user_verifier_authority: NONE`, `NO_DEVICE_ATTESTATION_OR_PHYSICAL_DEVICE_IDENTITY_GATE`). The real residual gap is that the submitter's KV/SKAP verification is not bound at ingress. | `CANONICAL_NODE_INGRESS_CONTRACT_001.json:149`; `task-registry-global-invariants.json:11,14,130` |
| F4 | **Contract conflict.** CANONICAL-NODE-INGRESS-CONTRACT-001 v0.3 (DRAFT) lists `device_attestation: POTENTIALLY_AUTHORITATIVE_IF_VALIDATED`, and n3's spec_gap `next_attempt` waits on an "attestation owner". The global invariant prohibits both. The spec_gap's next_attempt should be re-pointed. | `CANONICAL_NODE_INGRESS_CONTRACT_001.json:215` vs invariants `:130` |
| F5 | **Owner IDs.** `CANONICAL-NODE-INGRESS-CONTRACT-001` is a contract document, not a registered task. Its `goal_task_id SVORG-STEGOS-PORTABILITY-001` is absent from this registry, and its `cosv_state` is `ABSENT_FROM_CURRENT_TASK_REGISTRY_SCHEMA`. The #3369 packet assigns "claim/fence and expected head" to the **Registry/WorkerCoordinator owner** (`SHARE_PACKET:23`), not to ingress. | `data/canonical-task-registry.json` (no match) |
| F6 | **Authority is already pinned to NONE in the receipts.** Both appends hard-code `"NONE"` (`OMI:417,426`). The manifest's `authority_effect` reaches only the envelope (`SMC:142`), the boundary result (`process_boundary.py:99`) and receipt evidence (`OMI:673`). The boundary declares `authority_effect_resolution: DERIVED_FROM_APPLICABLE_TRANSITION_ELEMENTS` (`org-runtime/interlock-intr.json:284`), so carrying a caller value verbatim contradicts the boundary document. | |
| F7 | **Credential-model tension.** `origin_attestation.py` puts `TV_HMAC_SIGNING_KEY` on a TV/TVC resident host. Under the custody model TV/TVC holds no credentials. | `org-boundary/runtime/origin_attestation.py:15-19` |

## (a) Existing parts

| Mechanism | file:line | On this path? |
|---|---|---|
| Repo-ledger recorded lookup / chain walk | `.stegverse/transition-ledger/emit.py:60,73,84` | Yes (`OMI:1119`), after `cross()` |
| Org-ledger HEAD and receipt readback | `OMI:304` `_organization_receipt_read_back` | Only on partial commit (`OMI:347`) |
| Org append CAS on its own HEAD | `resident-runtime/aggregate_repo_transition.py:1069-1094` | Yes. No caller-expected head; ingress passes the manifest digest as predecessor (`OMI:1088`) |
| Exact-source idempotency (compares authority and context) | `aggregate_repo_transition.py:674-702` | Yes |
| Full org HEAD readback | `resident-runtime/organization_custody_readback.py:151`; `organization_ledger_readback.py:76`; `org-kernel/organization-ledger/organization_ledger_readback.py:472 recorded_for` | No |
| WorkerCoordinator | `heartbeat_runtime/admitted_worker_runtime.py:20` | No |
| Fence shape check (`claim_id` ends `-G<fence>`) | `heartbeat_runtime/process_adapter.py:148` | No |
| Claim/fence parity vs worker registry | `heartbeat_runtime/coordination_ledger.py:65,97`; truth in `control/worker-registry.d/`, `control/claims-active.json` | No |
| Fence binding on renewal | `heartbeat_runtime/engine_v3.py:74-82` | No |
| Registry admission (not authority) | `heartbeat_runtime/worker_task_admission.py:122,220` | No |
| Node standing (shape + gen-1 arithmetic) | `NS:241`, `:265-267`, `:288`, flags `:316-321`; called at `process_boundary.py:90` | Yes |
| TVC origin attestation (live verify) | `origin_attestation.py:202`; declaration `interlock-intr.json:129-160` | No (egress only) |
| Landed TVC receipt verifier (no clock, no network) | `resident-runtime/intr_path_tvc_read.py:100,156` | No |
| KV/SKAP layer-1/2 receipt re-derivation | `workers/device_kv_skap_roundtrip_verifier.py:125` | No |
| Envelope presence check | `org-boundary/runtime/intr_transport.py:11` | Yes, presence only |
| Replay tests | `tests/test_manifest_ingress_idempotent.py:132,144,182,260,377` | n/a |

## (b) Options

Style: predicates are `*_IS_*` / `*_ARE_*`; failure codes are `SCREAMING_SNAKE`; every non-ALLOW carries the six fields.

### Gap 1: sender identity

| Option | Ingress checks | Authority | Predicate / failure code | Evidence class | Owner | Best / worst | Constraint check |
|---|---|---|---|---|---|---|---|
| **1A** KV/SKAP receipt bound to the manifest | a layer-1 KV-access and layer-2 SKAP-access receipt pair whose operation binding names `canonical_manifest_sha256`, re-derived via `device_kv_skap_roundtrip_verifier.py:125` | KV/SKAP Vault | `SUBMITTER_VERIFICATION_IS_KV_SKAP_BOUND_TO_THE_MANIFEST` / `SUBMITTER_KV_SKAP_RECEIPT_ABSENT` (FAIL_CLOSED), `SUBMITTER_KV_SKAP_RECEIPT_CONTRADICTED` (DENY) | SOURCE_IMPLEMENTED → SANDBOX_RUNTIME_OBSERVED | ingress: SDK-MANIFEST-ECOSYSTEM-TRANSITION-DISPOSITION-001; KV binding field: STEGOS-DEVICE-KV-SKAP-ROUNDTRIP-001 | Best: the only constraint-true user identity. Worst: KV receipts bind a DEVICE→KV hop today, not a manifest, so KV needs a binding field | None. Receipts are landed bytes, so nothing waits |
| **1B** TVC origin attestation + bilateral match | `origin_attestation.verify`, plus the origin ledger recording the emission | TV/TVC | `ORIGIN_IS_ATTESTED_AND_BILATERALLY_MATCHED` / `ORIGIN_ATTESTATION_REFUSED` | SANDBOX_RUNTIME_OBSERVED | InTr / TVC | Best: strong for cross-org senders. Worst: N/A here (no InTr hop inside one org), and the live verify is a hold on a resident host | **Risk: external machine** (synchronous TVC resident). Also hits F7. Not for this binding |
| **1C** Record-only, refuse a failed proof | an optional `sender_proof` (1A shape): if present and fails, DENY; if absent, record `submitter_verification_state: NOT_PROVEN` in evidence | none needed | `OFFERED_SUBMITTER_PROOF_VERIFIES` / `SUBMITTER_PROOF_OFFERED_AND_REFUSED` | SOURCE_IMPLEMENTED | SDK-MANIFEST-ECOSYSTEM-TRANSITION-DISPOSITION-001 | Best: zero new authority; mirrors `unattested_crossing_disposition: ADMITTED_AND_RECORDED_AS_UNATTESTED` (`interlock-intr.json:158`). Worst: unverified submitters are still admitted | None |

### Gap 2: stale head / fence

| Option | Ingress checks | Authority | Predicate / failure code | Evidence class | Owner | Best / worst | Constraint check |
|---|---|---|---|---|---|---|---|
| **2A** Predecessor recorded and unsuperseded | for `VERIFY_EXISTING`, the declared `predecessor.result_sha256`/`manifest_sha256` is a receipt in this org ledger, and no later receipt for the same `node_ref` names the same predecessor | Organization ledger (runtime reality) | `DECLARED_PREDECESSOR_IS_RECORDED_AND_UNSUPERSEDED` / `DECLARED_PREDECESSOR_NOT_RECORDED` (FAIL_CLOSED), `DECLARED_PREDECESSOR_SUPERSEDED` (DENY) | SOURCE_IMPLEMENTED | lineage: CANONICAL-NODE-INGRESS-CONTRACT-001 doc owner (unregistered, F5); readback: ORGANIZATION-BATCH-CUSTODY-REPLAY-001 | Best: uses the real HEAD chain; matches `ORG_LOCAL_WORKER_TASK_AND_SEQUENCE_REPLAY_VERIFIED_WITH_EXACT_PREDECESSORS`. Worst: an O(chain) walk per ingress; genesis is unaffected | None |
| **2B** Sender-declared expected org HEAD | a caller `expected_org_head` equals HEAD under the append lock (new aggregator parameter) | Org-ledger owner | `EXPECTED_ORGANIZATION_HEAD_IS_CURRENT` / `ORGANIZATION_HEAD_STALE` | SOURCE_IMPLEMENTED | StegVerse-org/.github#163 (component) | Best: textbook CAS. Worst: every concurrent unrelated submission conflicts (livelock); the sender must read HEAD first; changes a digest-pinned component | None formally, but it moves a coordination concern onto the sender |
| **2C** WorkerCoordinator fence verify | when the manifest declares `claim_ref`/`fence_ref`: the shape check (`process_adapter.py:148` rule), then an unreleased BOUND claim with that token in `control/worker-registry.d/` (`coordination_ledger.py:75-97` semantics) | WorkerCoordinator | `DECLARED_FENCE_IS_THE_CURRENT_WORKERCOORDINATOR_FENCE` / `FENCE_DECLARED_NOT_VERIFIED` (FAIL_CLOSED), `FENCE_STALE_OR_RELEASED` (DENY) | SOURCE_IMPLEMENTED | Registry/WorkerCoordinator owner (#3369 assignment); task context SDK-TT-ATOMIC-TASK-WORKER-BINDING-001 | Best: reads WorkerCoordinator truth and mints nothing. Worst: the committed registry lags runtime claims; it applies only to task-bound manifests | None. Ingress observes and never mints a claim/fence |

### Gap 3: authority

| Option | Ingress checks | Authority | Predicate / failure code | Evidence class | Owner | Best / worst | Constraint check |
|---|---|---|---|---|---|---|---|
| **3A** Refuse any non-NONE declared effect | `manifest.transition.authority_effect` is absent or `NONE` | none (refusal only) | `DECLARED_AUTHORITY_EFFECT_IS_NONE_AT_THIS_RECEIVING_OPERATION` / `AUTHORITY_EFFECT_NOT_WARRANTED_AT_INGRESS` (DENY) | SOURCE_IMPLEMENTED | SDK-MANIFEST-ECOSYSTEM-TRANSITION-DISPOSITION-001 | Best: matches F6; the binding is `NONE_BINDING_ONLY`. Worst: a future warranted effect needs 3B | None |
| **3B** TVC scoped-warrant receipt | non-NONE effect requires a landed TVC warrant receipt bound to manifest digest, scope and `hb_epoch`, verified like `intr_path_tvc_read.py:100` | TV/TVC | `AUTHORITY_EFFECT_IS_WARRANTED_BY_TV_TVC` / `AUTHORITY_WARRANT_NOT_ISSUED` (FAIL_CLOSED), `AUTHORITY_WARRANT_CONTRADICTED` (DENY) | SANDBOX_RUNTIME_OBSERVED | ingress lane + StegVerse-Labs/TVC (`validate_warrant`, TVC#488) | Best: the right long-term authority. Worst: there is no warrant receipt schema yet | None with landed receipts; a **live** `validate_warrant` call would be an external machine (forbidden) |
| **3C** Registry ADMIT + claim | `worker_task_admission` ADMIT plus 2C | Registry | — | — | — | — | **Violates**: ADMIT "does not mint a claim/fence or authorize execution"; `registry_mints_execution_authority: false`. Reject |

### Gap 4: replay

| Option | Behaviour | Predicate / code | Owner | Best / worst | Constraint check |
|---|---|---|---|---|---|
| **4A** Keep idempotent, look up before processing | move the recorded-request lookup ahead of `cross()`; a recorded request returns the recorded receipts with no reprocessing; a partial commit still completes | `RECORDED_TRANSITION_IS_NOT_REPROCESSED` (ALLOW, `transition_replayed: true`) | ORGANIZATION-BATCH-CUSTODY-REPLAY-001 (per spec_gap) | Best: closes F2 and keeps I-10/E1 and outbox at-least-once delivery. Worst: role-conformance ids include the evaluation (`OMI:648-651`), so the lookup must match on `request_sha256` | None |
| **4B** Refuse full redelivery | full record → DENY with the recorded digests; partial commit → complete | `A_REPLAYED_PACKET_IS_REFUSED` / `TRANSITION_ALREADY_RECORDED` | same | Best: literal #3369 matrix. Worst: each distinct redelivery appends a refusal receipt; contradicts I-10; callers must treat DENY as success | None, but it conflicts with the specified I-10 |
| **4C** Refuse all redelivery | DENY even for a partial commit | — | — | Worst: strands partial commits (`OMI:376-384` `next_attempt`) | Breaks durable-queue recovery. Reject |

## (c) Recommendations

| Gap | Recommend | Smallest fail-closed first step (no new authority) |
|---|---|---|
| 1 | **1C now, 1A next** | Accept an optional `sender_proof`. If it is offered and does not re-derive via `device_kv_skap_roundtrip_verifier.py:125`, return DENY `SUBMITTER_PROOF_OFFERED_AND_REFUSED`. Otherwise record `submitter_verification_state: NOT_PROVEN`. Re-point n3's `next_attempt` from "attestation owner" to the KV/SKAP binding (F4). |
| 2 | **2C + 2A, conditional** | If `claim_ref`/`fence_ref` is declared and is not an unreleased BOUND claim with that token, return FAIL_CLOSED `FENCE_DECLARED_NOT_VERIFIED`. If absent, record `fence_state: UNVERIFIED`. For `VERIFY_EXISTING`, a predecessor not found in the org ledger is FAIL_CLOSED `DECLARED_PREDECESSOR_NOT_RECORDED`. |
| 3 | **3A now, 3B when TVC defines a warrant receipt** | Refuse a non-NONE `transition.authority_effect` with DENY `AUTHORITY_EFFECT_NOT_WARRANTED_AT_INGRESS` before `cross()`, recorded as a refusal at both levels. |
| 4 | **4A** (not a refusal) | Look up the recorded request before `cross()`. Re-label n2's spec_gap from `REPLAY_REFUSAL_NOT_IMPLEMENTED_BY_INGRESS` to `REDELIVERY_REPROCESSED_BEFORE_DEDUPLICATION`. |

**Gap 1.** Only KV/SKAP may verify a user; device, node and transport identity may not gate. 1A is the only real verifier, and 1B does not apply intra-org. 1C refuses a wrong proof now and records absence honestly, as the boundary does for unattested crossings.

**Gap 2.** #3369 gives "claim/fence and expected head" to WorkerCoordinator. Ingress observes WorkerCoordinator's claim state (2C) and the ledger's record of the predecessor (2A), and mints neither. 2B livelocks concurrent senders.

**Gap 3.** Receipts already pin NONE, and the boundary derives the effect rather than taking it from the caller. Refusing non-NONE needs no authority. A warranted effect waits on a landed TVC receipt, never a live call.

**Gap 4.** Idempotency is specified (I-10) and load-bearing for partial-commit recovery and the outbox. "No duplicate effect" is broken by the processing order, not by the disposition. Fix the order and keep ALLOW with `transition_replayed: true`.
