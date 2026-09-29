# Entry-point parity: Chat as an equal of a console entry

Granular control is a property of the **entry point**, not of the builder. The
console offers submission, replay, reconstruction, and control over what the
return projects and how it is labelled. Unless the Chat entry point reaches the
same capability, someone using Chat silently gives up abilities.

That is not hypothetical. `SDK_TT_EVALUATOR_TESTS_1_3_RUN_EVIDENCE.md` records
that the evaluator was operating from an iPhone with no practical console
surface, so another operator had to drive the console on their behalf — and the
evidence file has to qualify its own claim because of it.

## Transportability is a node capability, not a device property

A device is **interchangeable**. `physical_device_identity_gate` is
`NONE_PROHIBITED` and `device_identity_is_execution_metadata_only` is true, so
no capability may ever be gated on which device is in hand. The correction was
already made once for `SDK-WORKSPACE-EXTCOLLAB-AUTHENTIC-RUNTIME-004`, whose
predicate `ONE_CURRENT_DEVICE_END_TO_END_PROVEN` was replaced by
`ESTABLISHED_NODE_END_TO_END_PROVEN`; it had not been carried into Chat.

What a capability may be conditioned on is **transportability**: a capability of
a *registered node*, conferred by registration rather than owned by any device.
A capability requiring it is reachable from any device on which a node is
established or recovered.

| requires transportability | available without node registration |
|---|---|
| `SUBMIT_RAW_USER_DATA` | `RETURN_PROJECTION_CONTROL` |
| `SUBMIT_PREFORMATTED_MANIFEST` | `MANIFEST_LABEL_CONTROL` |
| `REPLAY_BY_RECEIPT_LOCATOR` | |
| `RECONSTRUCT_BY_RECEIPT_LOCATOR` | |

Submission and verification cross to custody, so they move data. Projection and
label control shape a return rather than being operations of their own, so they
do not. Naming the limit this way matters: it is registration, which anyone may
obtain on any eligible device, and never the device itself.

Registration confers transportability and **no authority**.
`node_user_verifier_authority`, `device_user_verifier_authority` and
`transport_user_verifier_authority` are all NONE, and
`user_verification_authority` is exclusively the KV/SKAP Vault. A node moves
data; it never vouches for anyone.

## Replay and reconstruction are the point

They are how a result is **verified** rather than trusted. An entry point that
can submit but cannot verify leaves its user dependent on someone else's
console, which is the same dependency in a new place. So the parity report
tracks them separately: a verification capability is never an acceptable gap,
and the gate fails when one is missing from Chat regardless of what else passes.

Each verification request names the exact fields a person compares:

| field | why |
|---|---|
| `manifest_receipt_id` | the locator being verified |
| `receipt_sha256` | the digest originally recorded |
| `reconstructed_receipt_sha256` | the digest independently re-derived |
| `reconstruction_status` | whether re-derivation succeeded |
| `immediate_predecessor_receipt_sha256` | the chain the receipt sits in |
| `consequence_reexecuted` | must be false — reconstruction never re-executes |

The verification is the equality of two digests plus a PASS. That is legible on
a phone, which is the whole point.

## Chat interfaces with the builder; it does not build

A raw submission carries the user's data and declared goal to the Manifest
Builder and names the builder call the console would make. A preformatted
submission carries another framework's manifest through unchanged. In both
cases `chat_builds_manifest` is false and `manifest_constructed_by_chat` is
false, and `console_equivalent_request` projects the entry onto the console's
own operation shape so neither path drifts into its own dialect.

## Current state

7 console capabilities: **6 available at Chat, 1 declared gap, 0 drift,
0 expired.** The gap is the bundled demonstration dataset (`000`), which may
well belong to the console only — the gap records that question rather than
hiding it.

## Gaps are granted, and they expire

Exactly as capability-map exemptions are. A gap names its failed predicate and
repair, an `owning_existing_goal` matching the canonical task-id shape, the
registry repository and the generation at which that goal was observed, a
`granted_by` that must name the owning goal, and a `review_by` date after which
the gate goes red. A gap cannot grant itself.

## Why it is a gate

`tests/test_entry_point_parity.py` **exercises the Chat entry contract** rather
than trusting the parity constant, so the map cannot claim a capability the
contract does not carry. Verified red for each failure mode before merge: a
capability dropped or renamed out of the contract while the map still claims it;
a verification capability missing from Chat; a self-granted gap; a lapsed review
date; and a new console capability with no gap declared.

Inspect it with `stegverse entry-point-parity`.

## Boundary

Source reconciliation and request validation only. Nothing is submitted,
replayed, reconstructed or built; no receipt is minted and no execution
authority is granted. A capability reported available at Chat means the entry
contract carries it — not that any backend has been activated behind it.
