# MIR × StegVerse Historical Accounting Run 2

Goal Task ID: `MIR-STEGVERSE-HISTORICAL-ACCOUNTING-RUN-002`
Parent Task ID: `MIR-STEGVERSE-SEPARATION-OF-POWERS-EVIDENCE-CONTRACT-001`
COSV ID: `50000000100000`
Issue: `StegVerse-org/StegVerse-SDK#217`
Status: `ACTIVE / EXECUTION PREPARED / AUTHENTIC RUN PENDING`

## Frozen test choreography

This run MUST preserve the human-declared experiment sequence and MUST NOT be reinterpreted from lower-level component contracts:

1. StegVerse executes one governance test through the existing canonical SDK route.
2. StegVerse retains exact run evidence from initiation through the MIR handoff boundary.
3. StegVerse emits one bounded historical handoff package to MIR.
4. MIR independently performs its historical recording/accounting function over the handed-off history.
5. MIR returns one historical-accounting artifact.
6. StegVerse validates that artifact against the original run and computes the delta.
7. Replay/reconstruction evidence is retained where the canonical runtime supports it.
8. Publisher consumes the authentic evidence package and produces the complete Run-1 + Run-2 evaluator report.

`mir.leaf.v3`, MIR standing evidence, and other component surfaces are supporting checks only. They do not replace this choreography.

## StegVerse governance input

Run 2 uses the existing evaluator-facing governed test request at:

`inspection/examples/governed-test-request.json`

The exact bytes/hash used for execution MUST be retained at run time. A changed request requires a new run identity; it must not silently replace Run 2.

## Required StegVerse evidence before MIR handoff

Retain at minimum:

- exact submitted request bytes and SHA-256;
- normalized/canonical manifest identity and SHA-256;
- governance-request binding hash;
- governance disposition/result artifact;
- manifest receipt identity;
- ordered route/transition receipts from initiation through handoff;
- Master Records custody locator/status where emitted;
- replay/reconstruction locators/results where supported;
- exact software/runtime identities required for reconstruction.

The MIR handoff package is derived from authentic retained run evidence only. CI/source fixtures must not be substituted for runtime evidence.

## MIR handoff boundary

The handoff package must present the ordered state/history created by this run through the handoff point, with exact content commitments sufficient for MIR to account for the history independently.

MIR is asked to perform historical recording/accounting. MIR is NOT asked to issue `ALLOW`, `DENY`, `ADMISSIBLE`, or another StegVerse governance verdict.

## MIR return artifact

The returned MIR artifact must be retained byte-for-byte or by an exact content-addressed representation and must identify its accounting of the handed-off history. No MIR output may be synthesized from StegVerse expectations.

## StegVerse delta validation

StegVerse compares the MIR accounting to the original run and reports at minimum:

- exact matches;
- missing entries;
- extra entries;
- order differences;
- changed identifiers/digests/checkpoints;
- field/value differences;
- overall `EXACT_MATCH` or `DELTA_PRESENT` classification.

A delta is evidence to inspect, not automatically a governance failure.

## Publisher completion

The complete Publisher package must include prior Run-1 material plus Run-2 primary execution, StegVerse→MIR handoff, MIR accounting return, delta analysis, replay/reconstruction evidence, screenshots/presentation captures, and the evidence ledger.

Publisher must not label the report complete until authentic required artifacts exist. GitHub Actions remains validation/evidence transport only and is not the run-time authority.

## Immediate execution gate

No further semantic interpretation work is required before Run 2. The remaining gate is authentic execution through an available resident/runtime surface and a working MIR exchange path. If either surface is unavailable, report that exact execution blocker without redefining the test.
