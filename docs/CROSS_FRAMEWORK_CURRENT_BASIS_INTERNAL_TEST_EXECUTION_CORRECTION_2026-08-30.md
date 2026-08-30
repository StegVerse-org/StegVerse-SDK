# Cross-Framework Current-Basis Internal Test Execution Correction — 2026-08-30

## Scope

This note corrects the execution-boundary interpretation for the frozen cross-framework current-basis v0.4 test.

The frozen v0.4 experiment is an internally resident StegVerse test. It is not an external-evaluator ingress demonstration.

## Correct internal test path

```text
frozen test definition
-> canonical SDK execution
-> canonical StegCore / StegGate evaluation
-> Master Records custody created as part of the governed SDK run
-> S1 observation
-> post-observation S0->S1 transition receipt
-> replay
-> reconstruction
-> RUN_COMPLETE
-> host-neutral verified result packet
-> StegVerse-native durable retention / evaluator availability
-> optional third-party mirrors
```

Master Records custody is a normal property of the governed SDK execution. It is not an additional external-ingress attestation prerequisite for this internally resident test.

The test must therefore not be blocked on a separate external evaluator ingress, external rendezvous, resident observer loop, or external-ingress-specific provenance cycle merely to execute.

## External evaluator ingress property

An evaluator-initiated demo/test that originates outside StegVerse has an additional boundary-observation property:

```text
external evaluator
-> external ingress / Interlock / InTr
-> admitted StegVerse governed execution
-> ordinary Master Records custody of the governed run
-> governed egress / Interlock / InTr
-> evaluator-visible evidence
```

The added requirement is evidence that the externally supplied request genuinely crossed the governed ingress/egress boundary and was handled by StegVerse. It does not create a second Master Records custody requirement for internally resident tests.

## Replay / reconstruction artifact contract

The final retained test artifacts must expose the exact Master Records navigation value needed for replay and reconstruction in a device-neutral copy/paste form.

The v0.4 execution harness therefore emits:

```text
REPLAY_REFERENCE.txt
```

The file is newline-delimited `KEY=VALUE` text with no table formatting, hidden UI dependency, or device-specific presentation requirement. It includes at least:

```text
TEST_ID
MANIFEST_RECEIPT_ID
MANIFEST_SHA256
MANIFEST_GIT_BLOB_SHA1
TRANSITION_ID
TRANSITION_RECEIPT_HASH
STEGVERSE_RESULT_SHA256
PORTABLE_REPLAY_REFERENCE
REPLAY_REFERENCE
RECONSTRUCTION_REFERENCE
```

The portable form is:

```text
stegverse-replay:v1:<manifest_receipt_id>:<frozen_manifest_sha256>
```

The result packager must reject publication if the copyable reference artifact is missing or does not bind to the retained run evidence.

## Authority boundary

```text
internal test execution != external ingress demo
Master Records custody of canonical SDK run: REQUIRED
external-ingress boundary observation for internally resident test: NOT REQUIRED
GitHub Actions runtime authority: NONE
StegVerse-native retention / evaluator availability: REQUIRED
third-party distribution dependency: NONE
GitHub Actions publication role: OPTIONAL_MIRROR_ONLY
TV/TVC credential authority: UNCHANGED
```

This correction does not weaken Master Records custody, replay, reconstruction, frozen-input identity, counterpart isolation, or post-observation receipt timing. It removes only the incorrectly elevated external-ingress-specific prerequisite from internally resident test execution.


## Third-party independence correction — 2026-08-30

The completed v0.4 experiment must not depend on GitHub or any other third-party platform for execution, custody, replay, reconstruction, packet verification, durable retention, evaluator availability, activation, or completion.

The required completion path is:

```text
canonical internal StegVerse execution
-> Master Records durable custody
-> S1 observation
-> post-observation S0->S1 transition receipt
-> replay
-> reconstruction
-> RUN_COMPLETE
-> host-neutral verified result packet
-> StegVerse-native durable retention and evaluator-visible availability
```

GitHub Actions may optionally mirror an already-complete packet. Failure, unavailability, removal, or non-use of that mirror must not alter the StegVerse-native completion state.
