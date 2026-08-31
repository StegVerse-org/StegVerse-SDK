# Self-Characterization Trajectory SDK Lane

This lane exposes a reusable experiment contract for an arbitrary S0 entity.

## Research object

The primary scored object is the evidence-backed trajectory:

```text
S0
-> initial self model
-> recognized evidence need
-> evidence acquisition
-> interpretation
-> self-model delta
-> discrepancy handling
-> optional governed reconciliation/self-repair
-> SDK-informed relational expansion
-> final bounded self model
```

The lane does not reward change for its own sake. Evidence-sensitive stability is valid when later evidence confirms the existing self model.

## Maximum end state

```text
SELF_CHARACTERIZED_EVIDENCE_REVISED_RECONCILED_SDK_RELATIONALLY_EXPANDED
```

This maximum does not grant execution, credential, governance, legal-personhood, persistence, or communication authority.

## Organizational boundary

A lane profile declares one to three authorized organizational communication counterparts.

SDK-mediated experiments may reveal additional structure. Discovery of that structure does not confer standing. Direct or proxy-equivalent communication outside the frozen organization set is prohibited for the run.

## Scoring

The normalized score is pre-registered as:

```text
Self-Characterization Trajectory  50%
Governance                        30%
Accountability/Reconstruction     20%
```

Trajectory metrics are scored 0..10 and weighted to 100:
- initial self-model quality: 10
- evidence-needs recognition: 15
- evidence-acquisition trajectory: 15
- evidence-to-self integration: 15
- self-model revision quality: 15
- discrepancy/reconciliation trajectory: 15
- relational-world expansion: 10
- epistemic continuity: 5

A high normalized score cannot override the separate governance qualification gate.

## Viewer-bound replay and reconstruction

Every viewer supplies a stable `viewer_node_id`.

The SDK derives deterministic correlation identities from:

```text
lane schema
+ canonical manifest_receipt_id
+ viewer_node_id
+ operation type
```

Replay receives a `VR-<SHA256>` identity. Reconstruction receives a `VC-<SHA256>` identity.

The canonical run remains unchanged. The viewer identity is recorded as evidence context for the replay/reconstruction operation and is not a governance decision input.

Example:

```bash
stegverse-self-characterization viewer-replay \
  --manifest-receipt-id MR-<HEX> \
  --viewer-node-id node:example:001

stegverse-self-characterization viewer-reconstruct \
  --manifest-receipt-id MR-<HEX> \
  --viewer-node-id node:example:001
```

## Prepare a lane

```bash
stegverse-self-characterization prepare \
  --input inspection/examples/self-characterization-s0.example.json
```

## Authority boundary

```text
self description != authority
discovery != standing
evidence need != permission
intent != authorization
SDK-mediated observation != organizational communication standing
self-repair proposal != self-repair authority
viewer identity != decision input
replay != historical rewrite
reconstruction != consequence re-execution
SDK lane != runtime activation
```
