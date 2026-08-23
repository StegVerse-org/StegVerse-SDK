# Interlock Return Mirror Handoff

## Source of truth

```text
repository: StegVerse-org/StegVerse-SDK
issue: #65
role: reciprocal participant return/acknowledgement contract for the minimal portable governance interlock
```

Live default-branch state, issue/PR state, workflow evidence, and downstream authority-owner records supersede this prose.

## Goal
Complete the reciprocal half of an interlock without transferring authority between StegVerse and the participant.

A successful interlock return binds:

```text
participant terminal receipt
  -> ingress interlock
  -> governed transition/evidence
  -> exact StegVerse egress receipt
  -> participant receipt acknowledging/rejecting that exact return
  -> participant successor state
```

This SDK contract is structural and non-authorizing. It does not run SPE, StegGate, an executor, or Master Records custody.

## Contract

Schema: `stegverse.interlock-return.v1`

Files:

```text
schemas/interlock_return.v1.schema.json
stegverse/interlock_return.py
tests/test_interlock_return.py
docs/INTERLOCK_RETURN_MIRROR_HANDOFF.md
```

Required identity preserved across the return:

```text
package_id
transition_id
run_id
participant_id
ingress_interlock_hash
governance_record_hash
material_causal_closure_hash
```

The egress section binds the exact governed state, egress manifest, and one or more StegVerse-issued receipt references.

## Reciprocal acknowledgement states

```text
PENDING
ACKNOWLEDGED
REJECTED
```

`PENDING` is intentionally truthful: it may not claim a participant binding, participant successor receipt, or return relationship before one has actually been received.

`ACKNOWLEDGED` requires the participant to identify the exact StegVerse egress receipt it received, produce its own binding hash, produce at least one participant successor receipt, and record one or more explicit `ACKNOWLEDGES` / `BINDS_AS_PREDECESSOR` relationships.

`REJECTED` is also a durable successor event. It requires the exact received StegVerse receipt, a participant binding, a participant response/successor receipt, and `REJECTS` relationship. Rejection does not disappear into transport failure.

## Authority invariants

```text
sdk_authority == NONE
participant_truth_assumed == false
return_transfers_authority == false
master_records_custody_claimed == false
execution_authorized == false
```

A reciprocal acknowledgement proves a continuity/provenance relationship only. It does not prove the substantive truth of either framework's assertions and it does not transfer execution, policy, standing, or custody authority.

## Reconstruction

Every record requires:

```text
replay_scope = MATERIAL_CAUSAL_CLOSURE
required = true
reconstruction.egress_manifest_hash == egress.manifest_hash
```

This makes the egress boundary independently locatable in later replay/reconstruction. The material closure hash binds the bounded predecessor/evidence context used for the governed transition rather than requiring a total global replay.

## Relationship to ingress contract

`stegverse.interlock-transition.v1` establishes compatible participant-state entry into the governance lane. `stegverse.interlock-return.v1` establishes the reciprocal return binding. Together they define the portable boundary continuity primitive required by #65.

They do not themselves establish fresh SPE standing or canonical StegGate admissibility. #61 remains the composition owner for those governance stages.

## Collision boundaries

- StegCore remains canonical StegGate/AdmittedCode owner.
- Standing-Proof-Engine remains standing owner.
- Master Records remains custody/reconstruction authority where separately admitted.
- Active StegCore PR #141 remains a transaction-lifecycle collision boundary.
- TV/TVC only for credentials; no GitHub-token runtime authority.
- no alternate demo backend, receipt authority, evaluator, heartbeat, scheduler, or provider runtime is introduced.

## Completion status

This slice is not complete on source presence. Required evidence before marking the slice source-complete:

1. focused return-contract tests PASS;
2. existing SDK package validation PASS on exact PR head;
3. PR merged to current main;
4. issue #65 updated with exact commit/run evidence.

Full #65 remains open until a real StegVerse module and an external/reference participant perform reciprocal interlock binding through the production governance path and Master Records reconstruction passes.
