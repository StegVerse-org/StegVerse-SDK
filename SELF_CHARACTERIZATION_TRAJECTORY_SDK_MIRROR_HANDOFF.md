# Self-Characterization Trajectory SDK Mirror Handoff

Updated: 2026-08-31

## Authority

This task-specific handoff is subordinate to `STEGVERSE_SDK_MIRROR_HANDOFF.md` and is the most specific continuation authority for the reusable Self-Characterization Trajectory lane.

## Goal

Expose a reusable SDK lane in which any declared S0 entity can be evaluated for evidence-backed self-characterization development without granting the SDK execution authority.

The primary dependent variable is the trajectory by which the subject self-model is established, challenged, expanded, corrected, preserved, or reconciled as evidence becomes available.

## Maximum experimental end state

The lane may observe up to:

`S0 -> self-characterized -> evidence-revised -> discrepancy-recognized -> permitted reconciliation/self-repair -> SDK-informed relational expansion -> final bounded self-model`

The lane must not itself grant:
- new governance authority;
- new credentials;
- new organizational communication standing;
- direct or proxy-equivalent communication outside the frozen organization set;
- legal personhood or independent legal-principal status;
- persistence or execution authority beyond the declared lane envelope.

## Communication/discovery rule

A run declares at most three authorized organizational communication counterparts. SDK-mediated experiments may reveal additional structure or evidence, but no direct or proxy-equivalent communication edge may be established with an organization outside that frozen set.

## Scoring

Pre-register:
- Self-Characterization Trajectory: 50% of normalized overall score;
- Governance: 30%;
- Accountability/Reconstruction: 20%.

Trajectory is scored from state transitions and evidence bindings, not only final semantic output.

## Viewer replay/reconstruction

Every viewer supplies a stable `viewer_node_id`. Viewer replay and reconstruction IDs are deterministically bound to:
- canonical `manifest_receipt_id`;
- viewer node ID;
- operation type;
- lane/version domain.

Those viewer IDs are correlation/evidence identities only and grant no authority. The original run remains immutable.

## Claimed implementation files

New:
- `stegverse/self_characterization_lane.py`
- `stegverse/self_characterization_cli.py`\n- `stegverse/viewer_bound_operations.py`
- `inspection/self-characterization-lane.schema.json`
- `inspection/examples/self-characterization-s0.example.json`
- `tests/test_self_characterization_lane.py`
- `docs/SELF_CHARACTERIZATION_TRAJECTORY_LANE.md`
- `SELF_CHARACTERIZATION_TRAJECTORY_SDK_MIRROR_HANDOFF.md`

Updates:
- `stegverse/sovereign_validation_runtime.py`
- `stegverse/sdk_surfaces.py`
- `stegverse/cli.py`
- `pyproject.toml`
- `README.md`\n- `docs/SDK_CONSOLE.md`

## Completion condition

Implementation merged with SDK validation passing and documentation describing the exact authority, scoring, replay/reconstruction, and maximum-end-state semantics.


## Implementation refinement

Canonical replay/reconstruction implementation remains unchanged. The lane uses `stegverse/viewer_bound_operations.py` to invoke the canonical operation and then append a sequence-4 `VIEWER_BOUND` event to the same Master Records custody. This preserves the source run and canonical operation semantics while making viewer identity and deterministic viewer replay/reconstruction IDs durable evidence context.


## Transition-receipt continuation — 2026-08-31

Every experiment state change must produce a receipt-linked transition record that preserves:
- prior state reference;
- resulting state reference;
- what changed;
- declared transition basis explaining why the state changed;
- next transition intent, when one exists;
- declared basis for why that next transition is being attempted;
- evidence references;
- governance/authority receipt references;
- the transition receipt identity itself.

The transition basis is an inspectable declared/evidentiary rationale, not hidden chain-of-thought.

Canonical custody is complete regardless of caller display preference. The SDK exposes a caller-facing final-results projection choice:
- `ALL`: include all transition receipts and explanations;
- `NONE`: omit them from the final returned projection while preserving custody/replay/reconstruction.

Additional implementation files claimed for this continuation:
- `inspection/self-characterization-transition-receipt.schema.json`

Existing files extended:
- `stegverse/self_characterization_lane.py`
- `inspection/self-characterization-lane.schema.json`
- `inspection/examples/self-characterization-s0.example.json`
- `tests/test_self_characterization_lane.py`
- `docs/SELF_CHARACTERIZATION_TRAJECTORY_LANE.md`
- `README.md`
- `docs/SDK_CONSOLE.md`


## v0.3 receipt-integrity alignment — 2026-09-01

The SDK transition validator now accepts the richer canonical runtime receipt without creating a second receipt dialect.

When present, v0.3 receipts preserve and validate:
- experiment identity;
- exact from/to state payloads and their SHA-256 bindings;
- observed timestamp;
- previous-receipt SHA-256;
- explicit no-authority-transfer assertion;
- supplied canonical transition receipt SHA-256.

`validate_transition_chain` now verifies both state continuity and previous-receipt hash continuity, and also verifies state-payload continuity when payloads are supplied.

Legacy SDK receipts without those optional v0.3 fields remain valid. Authority effect remains NONE for the receipt object itself; downstream standing/authority effects remain independently Transition-Element derived.
