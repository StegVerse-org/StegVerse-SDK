# ODA3 Evaluation Boundary — Mirror Handoff

Status: ACTIVE — evaluator-boundary implementation and evidence packet
Date: 2026-08-18
Repository: `StegVerse-org/StegVerse-SDK`
Source-of-truth role: this handoff tracks the ODA3 bounded-transition / evaluator-defined testing workstream for this repository.

## Governing boundary

For a fixed, versioned StegVerse implementation and governed state, evaluator-supplied experimental metadata may select and compose published capabilities but must not add capabilities, alter the canonical decision route or semantics, or influence the governance result. The declared experiment, exact governance request, and returned result must remain independently verifiable as the same proposition and transaction.

The evaluator chooses the experiment; the published system determines the result.

## ODA3 requested first exercise

The first bounded exercise should test the evaluation boundary itself rather than immediately testing an authority-state-change scenario.

Required conditions:

1. Valid manifest using only published capabilities.
2. Equivalent manifest with changed evaluator identity, rationale, and expected observation.
3. Request for unavailable or undeclared capability.
4. Attempted alteration of canonical route or decision semantics.
5. Attempted alternate execution path.
6. Post-submission modification of normalized manifest.
7. Modification of governance request or returned result after execution.
8. Independent verification showing which alterations are rejected, detected, or preserved in evidence.

## Evidence package requested by ODA3

The repository must make the following directly identifiable and reproducible:

- exact tagged SDK release or commit;
- corresponding runtime or demonstration-repository version;
- manifest schema and complete representative manifest;
- published capability registry for that version;
- canonical route and StegGate semantic version;
- implementation/specification showing which manifest fields reach governance decision logic and which are evidence-only;
- normalization and binding specification, including algorithms, canonicalization rules, key ownership, and verification procedure;
- runnable tests/commands for the boundary conditions;
- representative receipts, reconstruction material, and negative-case outputs;
- method proving tested runtime corresponds to identified source version;
- licences and access limitations;
- file manifest and hashes for applicable artifacts.

## Execution-arrangement questions to close

Document and prove:

- whether ODA3 can run independently;
- whether any StegVerse-controlled service/sandbox is required;
- who controls relevant signing keys and governed state;
- how reviewers distinguish an SDK result from a separately controlled runtime result.

## Autonomous-system identification requirement

Before the eventual transition experiment, identify the AI or autonomous-system actor, its version, the proposed consequential action, and the exact enforcement point where StegVerse may permit, refuse, or defer the action.

## Outcome policy

Successful, refusal, negative, and inconclusive outcomes are all valid research records. The implementation must not optimize the route for a favorable evaluator result.

## Next experiment after boundary proof

If the evaluation-boundary claim is supported, define a second experiment involving one or more of:

- revocation;
- expiry;
- changed delegation;
- stale authorization;
- unavailable governing state;
- attempted alternate execution route.

Then evaluate whether the work supports a formally scoped ODA3 research unit and separately establish contributions, intended output, ownership, attribution, confidentiality, and publication conditions.

## Current implementation priorities

P0 — establish this handoff as durable task source of truth.

P1 — map every ODA3-requested artifact to an existing repository path or create the missing artifact.

P1 — add a deterministic evaluator-boundary test suite covering all eight conditions above.

P1 — ensure evaluator identity, rationale, and expected observation are demonstrably evidence-only and do not influence StegGate decision semantics.

P1 — prove unavailable/undeclared capabilities fail closed rather than silently adapting the route.

P1 — prove normalized manifest + exact governance request + resulting output are cryptographically bound and tamper-evident.

P1 — emit representative receipts, reconstruction material, and negative-case outputs from runnable tests.

P1 — add artifact manifest + hashes and source/runtime correspondence proof.

P2 — document independent-vs-StegvVerse-controlled execution modes, signing-key ownership, governed-state control, licensing, and access limitations.

P2 — identify the autonomous-system actor/version/action/enforcement point for the eventual authority-state transition exercise.

## Constraints

- No evaluator-specific private capability additions.
- No alternate evaluator-specific canonical route.
- No evaluator metadata as a hidden governance input.
- Missing capabilities must be rejected or developed separately as generally versioned capabilities.
- Preserve exact versionability and independent verification.
- Do not treat source merge, CI success, publication, or deployment as proof of live activation.

## Completion criteria

This workstream is complete only when the required artifacts are installed in durable repository locations, runnable boundary tests pass against a fixed versioned implementation, negative/tamper cases are demonstrated, receipts/reconstruction evidence is inspectable, the runtime/source correspondence is provable, and this handoff is updated with exact paths, commits, test commands, and resulting evidence.
