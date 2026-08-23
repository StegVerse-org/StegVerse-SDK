# Minimal Portable Governance Ecosystem Mirror Handoff

## Source of truth

```text
repository: StegVerse-org/StegVerse-SDK
issue: #65
role: public non-authorizing interlock/manifold compatibility contract
```

Live repository state, issue/PR state, workflow results, SPE/StegCore/Master Records handoffs, and committed evidence supersede prose summaries.

## Architecture

The minimal portable StegVerse Governance Ecosystem is the smallest implementation capable of receiving manifested state from a conformant participant, governing a consequential transition without assuming ownership of either endpoint, producing a compatible successor record, and supporting independent replay/reconstruction of the material decision context.

The portable core is:

```text
manifest / receipt protocol
  -> interlock boundary contract
  -> SPE standing/evidence
  -> StegGate / AdmittedCode present-tense admissibility
  -> governed successor state
  -> Master Records manifold-aware preservation
  -> replay / reconstruction / portable verification
```

The SDK is the public manifestation/interlock/conformance membrane. It remains non-authorizing.

## Participant rule

Every StegVerse module and any external framework choosing full interoperability is a participant around the governance core. Internal StegVerse modules do not receive privileged governance semantics. Shared-process or shared-network transport MAY be optimized, but transport optimization MUST NOT bypass manifestation, interlock binding, standing, admissibility, receipt production, or reconstruction requirements.

## Adapter vs interlock

`ADAPTER` means StegVerse can record exactly what it received but cannot infer that the submitted state was the participant's own terminal authoritative state.

`INTERLOCK` means the participant has bound its last receipt/state to the manifested package before the StegVerse boundary. A compatible participant receipt may therefore become a first-class predecessor in the StegVerse receipt graph. This increases continuity/provenance standing only; it does not transfer truth, execution authority, custody, or substantive standing.

The reciprocal return goal is:

```text
participant terminal receipt
  -> participant-bound manifest
  -> StegVerse ingress receipt
  -> governed transition manifold
  -> StegVerse egress receipt
  -> participant successor receipt
```

## Governance declaration

Governance source is explicit. Initial modes are:

- `PROVIDED`: participant-only governance profiles.
- `DEFAULT_STEGVERSE`: one or more explicitly selected StegVerse-maintained, versioned profiles appropriate to the transaction surface.
- `COMPOSED`: participant profiles plus one or more explicitly selected StegVerse profiles.

No StegVerse default is inferred from omitted governance fields.

## Boundary outcomes

Protocol-level boundary state vocabulary is:

```text
PRESENTED
ACCEPT
REPAIR
DENY
REVIEW
```

`REPAIR` must preserve the original manifested package and point to a distinct repaired successor. The SDK contract validates this structure only; it does not decide when repair is permitted.

## Manifold semantics

Linear `previous -> next` chains are a special case. The portable contract models bounded predecessor and successor state sets plus typed relationships. Initial relationship vocabulary:

```text
CAUSE
DEPENDENCY
EVIDENCE
AUTHORITY
CORROBORATION
CONFLICT
SUPERSEDES
OBSERVED_WITHOUT_DEPENDENCY
```

Chronology is evidence but must not silently create causality. Replay/reconstruction is scoped to `MATERIAL_CAUSAL_CLOSURE`: the bounded predecessor/evidence/governance context materially relevant to the transition under review.

## Authority invariants

This first SDK slice enforces:

```text
sdk_authority == NONE
participant_truth_assumed == false
interlock_transfers_authority == false
master_records_custody_claimed == false
execution_authorized == false
```

The interlock validator does not:

- mint standing;
- run SPE;
- run StegGate;
- authorize consequence;
- create Master Records custody;
- assert truth of participant claims;
- create a second receipt authority.

## Production-proof rule

Public SDK demonstration must use the same production-grade manifestation/interlock/governance/receipt/replay/reconstruction path as real consumers. A bounded demonstration may reduce consequence scope; it may not substitute a weaker governance backend.

## Slice 1 source

```text
schemas/interlock_transition.v1.schema.json
stegverse/interlock_transition.py
tests/test_interlock_transition.py
docs/MINIMAL_PORTABLE_GOVERNANCE_ECOSYSTEM_MIRROR_HANDOFF.md
```

Implemented structural checks include:

- adapter vs interlock connection classes;
- required participant terminal receipt/binding for interlock;
- exact boundary receipt membership in predecessor receipts;
- JCS/NFC canonicalization declaration;
- explicit governance source/profile mode;
- many-predecessor/many-successor state representation;
- typed manifold relationships referencing known states;
- immutable original manifest binding;
- explicit distinct repair successor;
- authority non-claims;
- material-causal-closure replay requirement;
- linear transition accepted only as the special 1 -> 1 manifold case;
- deterministic canonical hash helper.

## Collision boundaries

- SDK #61 remains the SDK -> SPE -> StegGate -> return/reconstruction composition owner.
- SDK #64 remains provider interoperability/conformance/certification owner.
- Standing-Proof-Engine remains standing owner.
- StegCore remains canonical StegGate/AdmittedCode owner.
- Master Records remains custody/reconstruction authority where separately admitted.
- StegCore PR #141 is still an active transaction/receipt collision boundary. Do not implement the StegCore side of this interlock by mutating colliding transaction-lifecycle paths until that PR is reconciled.
- TV/TVC only for credential authority; no GitHub-token runtime authority; no Render dependency.

## Required next slices

1. Validate and merge this SDK interlock/manifold contract using existing SDK workflows.
2. Bind the #61 SPE-return bridge to this interlock package identity without turning standing into authority.
3. Define a compatible interlock egress/participant acknowledgement record so a participant can bind StegVerse's terminal receipt into its own successor receipt.
4. After StegCore #141 collision clears, bind the canonical StegGate request/decision to the same interlock transition/package/run identity.
5. Extend Master Records handoff from single-chain assumptions, where any remain, to bounded receipt-manifold preservation and material-causal-closure reconstruction.
6. Migrate one StegVerse module to the exact public interlock contract.
7. Migrate one external/reference participant to the same contract.
8. Expose production-path receipts/explanations/replay/reconstruction through the public SDK surface with no alternate demo governance backend.

## Completion boundary

Issue #65 is not complete on this source slice. Full completion requires live interlock ingress and reciprocal return binding, a real StegVerse module, a real external/reference participant, canonical SPE and StegGate traversal, Master Records manifold preservation, replay/reconstruction PASS, and portable independent verification.
