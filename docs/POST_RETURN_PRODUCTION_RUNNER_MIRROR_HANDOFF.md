# POST_RETURN Production Proof Runner Mirror Handoff

Updated: 2026-08-24
Repository: `StegVerse-org/StegVerse-SDK`

## Purpose

Close the source-level gap between the independently validated PRE_STEGGATE evidence path, the canonical sovereign runtime, its local run store (the SDK-internal local run record (`stegverse/local_run_record.py`; non-authoritative: authority_effect NONE, completes_transition false; not Master Records authority or custody)), and the already-merged reciprocal POST_RETURN/exchange/replay/reconstruction machinery.

This runner is successor-release-aware. It is intentionally separate from the historical `run_oda3_evaluation_boundary_r3.py` harness because R3 freezes SDK/StegCore coordinates that predate the full POST_RETURN and canonical SPE-standing implementations.

## Entry point

```text
scripts/run_post_return_production_proof.py
-> stegverse.post_return_production_runner.run_post_return_production_proof
```

Required inputs:

```text
coherent successor aggregate-release receipt
public inspection manifest
verified PRE_STEGGATE portable governance bundle
local run-record location (caller-supplied; SDK-internal `stegverse/local_run_record.py`, no default)
bounded sovereign state file path
portable exchange output path
retained proof output path
```

## Fail-closed sequence

The runner performs, in order:

1. independently verify the aggregate receipt schema, TV/TVC credential boundary, exact receipt hash, component commit coordinates, and required proof-capability bindings;
2. reject a historical/capability-free release before any sovereign runtime call;
3. independently verify the PRE_STEGGATE portable bundle;
4. validate/normalize the public inspection manifest;
5. derive canonical StegCore three-layer semantics from `input.steggate_request`;
6. verify the PRE_STEGGATE bridge's own raw three-layer request hash;
7. normalize the bridge request and require exact semantic equality with the manifest-derived three-layer proposition;
8. build the non-authorizing standing execution context from the verified PRE_STEGGATE bundle;
9. create the bounded local state consequence with a deterministic release-set/run idempotency key;
10. call the existing canonical `run_sovereign_validation()` with that exact standing context and bounded consequence;
11. require canonical runtime standing-context consumption, StegGate `ALLOW`, and a real state transition;
12. read the run's local run-store record (`LocalRunRecordStore.evidence_package`) when present, as downstream, non-gating evidence only;
13. call the already-merged `complete_post_return_evidence()` path, which verifies the organization-ledger readback for this run's manifest-directed transition (`--organization-ledger-readback`) and binds the interlock return's `governance_record_hash` and egress receipt to that organization receipt; without a verified readback the result is a six-field `FAIL_CLOSED` whose retry entrypoint is `StegVerse-org/.github:.stegverse/transition-requests/` (SDK-MR-A, #452);
14. require reciprocal participant ACK, POST_RETURN portable verification, governance exchange verification, replay without consequence reexecution, and reconstruction without consequence reexecution;
15. retain one final `stegverse.sdk.post-return-production-runner-result.v1` proof object.

No caller-supplied run-record packet is accepted, and the local run store never completes or gates the proof.

## Proposition anti-cross-pairing rule

A valid standing bundle for proposition A may not be paired with a sovereign manifest for proposition B.

The PRE_STEGGATE bridge's raw `three_layer_request_hash` remains independently verified as part of the portable bundle. For manifest binding, both the bridge three-layer request and the manifest-derived three-layer projection are normalized to the same canonical StegCore defaults (`unknown`, empty refs/hashes, false booleans where the model resolves absent optional values). The normalized objects must be identical.

This distinguishes semantic default resolution from mutation while still detecting action/target/scope, judgment, signal/state, or execution-boundary changes before consequence execution.

## Release coherence

The runner requires the capability IDs defined by `proof_release_gate.py`:

```text
SDK_POST_RETURN_EVIDENCE_V1
STEGCORE_SPE_STANDING_BINDING_V1
```

`MASTER_RECORDS_OPERATION_CUSTODY_V1` is reported as a downstream evidence capability and never gates the proof.

The aggregate receipt must carry an explicit exact `commit_sha` for each release component and a verified feature-to-release containment record for each required capability. A valid R3 historical receipt without these later capabilities must fail closed for this runner.

## Authority boundary

```text
SDK release authority: NONE
SDK credential authority: NONE
release verification authority: NONE
standing decision authority: canonical StegCore only
consequence authority: canonical StegGate + commit coherence only
Master Records: downstream recorder of released batch receipts, not an authority (the local run record is SDK-internal, `stegverse/local_run_record.py`, and non-authoritative)
portable verification authority: NONE
exchange authority: NONE
copied exchange == canonical custody: FALSE
arbitrary network side effects enabled: FALSE
```

The runner reads no GitHub/release/private-source credential. TV/TVC release authorization and publication occur upstream. The runner consumes only the resulting non-secret release evidence.

## Bounded consequence

The proof consequence remains an actual atomic local state transition through `reference_state_executor`:

```text
state_transition_performed = true
before_state_hash
 after_state_hash
idempotency key bound to release_set_id + PRE_STEGGATE run_id + consequence key
external_side_effect = false
```

A duplicate/replayed run cannot count as a new consequence because the final proof requires `state_transition_performed=true`, while canonical replay/reconstruction must report `consequence_reexecuted=false`.

## Completion boundary

Source validation/merge of this runner is not production proof completion.

The final task can become COMPLETE only after:

```text
StegCore #146 admitted + merged
successor immutable SDK/StegCore/Master Records release coordinates frozen
successor TV/TVC aggregate receipt proves all required capability containment
real PRE_STEGGATE evidence from the public/reference participant exists
runner executes against canonical sovereign dependencies
real bounded transition occurs
The exact run record is retained in the SDK-internal local run record (`stegverse/local_run_record.py`; authority_effect NONE, completes_transition false; not Master Records custody)
participant return is ACKNOWLEDGED
POST_RETURN portable verification PASS
exchange verification PASS
replay PASS without reexecution
reconstruction PASS without reexecution
final proof object retained
```

## 2026-08-26 runtime/release reconciliation

Upstream source/release preparation has advanced beyond the original runner implementation state:

```text
StegCore canonical standing consumer: MERGED / VALIDATED
StegCore bounded public interlock consequence proof: MERGED / VALIDATED
SDK 1.2.0 release source parent: 47a85c402d8d72e1db90445ec272fa83e8a40b08
SDK 1.2.0 release commit: beaabe0a06ef32f0f62fbe6bc360463b245bff61
StegCore 0.3.0 source parent: ef38410505b0ef3e84148892b1d6e3cdef20f300
StegCore 0.3.0 release commit: 58445bb14642c1889cf9802666c15bd48c6d2e39
Master Records 0.2.0 source parent: 03312236c115bc814024d700810391340648601f
Master Records 0.2.0 release commit: c524b1a0c1a43e49c70faeac7b67f78c5908e4e4
TVC successor policy/source validation: COMPLETE / MERGED
TVC provider-neutral sealed SKAP release-credential source: COMPLETE / VALIDATED / MERGED
TV authorization request: REQUESTED_NOT_GRANTED
successor aggregate receipt: NOT PRODUCED
POST_RETURN production proof: NOT EXECUTED
```

The immediate blocker is no longer runner source, release-coordinate selection, or sealed-credential source. It is the real TV/TVC authority/runtime boundary: current GRANTED authorization, live resident SKAP recipient activation/liveness/lease, real owner/device sealed capsule, and real DEVICE->KV->SKAP_VAULT InTr evidence. After those exist, TVC owns resident `runtime_activate`, immutable release publication/verification, aggregate receipt generation, then this runner owns the genuine POST_RETURN proof.

Do not substitute hosted CI, moving main, a generic GitHub token, a plaintext SKAP credential file, or a fabricated receipt for that boundary.
