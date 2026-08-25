# Release Dependency Alignment Mirror Handoff

Updated: 2026-08-24
Repository: `StegVerse-org/StegVerse-SDK`

## Purpose

Prevent a released SDK artifact from claiming a coherent successor release while its installed `governed-test` metadata still points at older executable StegCore/Core-Lite/Master Records commits.

This gate is distinct from release-capability containment:

```text
aggregate receipt proves released components contain required features
AND
installed SDK wheel metadata must point its governed-test VCS dependencies at the same executable source coordinates
```

Both must hold before the canonical POST_RETURN production-proof command may proceed.

## Installed-artifact contract

`stegverse.release_dependency_alignment.verify_installed_governed_test_dependency_alignment()` reads the installed `stegverse-sdk` distribution metadata through `importlib.metadata.requires()` and extracts exact Git commit pins from the `governed-test` extra.

Required dependency/repository bindings are:

```text
stegcore -> StegVerse-Labs/StegCore
stegverse-core-lite -> Data-Continuation/core-lite
stegverse-master-records -> master-records/orchestration
```

For each aggregate-release component, the executable coordinate is resolved in this order:

```text
source_parent_commit
source_parent_commit_sha
commit_sha
commit
```

The installed wheel pin must equal that exact executable coordinate. Missing pins, missing release components, repository mismatch, stale commits, or unexpected governed-test Git pins fail closed.

## Canonical production-proof binding

`scripts/run_post_return_production_proof.py` verifies installed dependency alignment immediately after loading the release receipt and before invoking the sovereign production runner.

Therefore:

```text
valid aggregate receipt + stale installed StegCore pin -> FAIL_CLOSED
valid aggregate receipt + aligned installed pins -> may continue to release/proof-capability and runtime gates
```

The check grants no standing, admissibility, release authority, execution authority, or custody.

## Current development observation

The current SDK `1.2.0.dev0` development metadata still points `governed-test` at the historical executable coordinates used by the earlier frozen release set. That is valid historical/development metadata but must not be frozen as the successor POST_RETURN release until StegCore #146 is admitted/merged and the SDK governed-test StegCore pin is updated to the exact successor executable coordinate.

Core-Lite and Master Records do not need gratuitous successor source changes solely for this proof if their existing immutable releases already contain the required runtime/custody behavior and remain the exact executable coordinates used by the successor set.

## Validation requirement

The dedicated non-authorizing workflow must:

1. run source alignment tests;
2. build the exact SDK wheel;
3. install that wheel into an isolated environment;
4. prove installed metadata aligns with the historical executable coordinates it currently declares;
5. prove the same installed wheel rejects a successor receipt requiring StegCore #146;
6. compile the verifier and canonical proof command;
7. consume no release/runtime credential.

## Completion

Source completion requires exact-head validation and merge. Successor release completion additionally requires updating the SDK governed-test pins to the exact frozen successor component coordinates before the SDK 1.2.0 candidate is frozen and released.
