# Testing Data Loop Status Ingestion

## Purpose

This document defines how exported workflow observations update the testing data loop status artifact.

The command is intentionally offline-compatible. It does not require live GitHub Actions access. When live run metadata becomes available, export the observations into the same JSON shape and run the same command.

## Input Observation Shape

```json
[
  {
    "repository": "StegVerse-org/StegVerse-SDK",
    "commit": "<commit-sha>",
    "workflow_visible": true,
    "conclusion": "success"
  }
]
```

Allowed conclusions:

```text
success
failure
cancelled
skipped
timed_out
action_required
```

## Command

```bash
python scripts/ingest_testing_data_loop_status.py \
  --status examples/testing_data_loop_status.json \
  --observations examples/testing_data_loop_workflow_observations.json \
  --output /tmp/testing_data_loop_status.json
```

Validate the generated status artifact:

```bash
python scripts/validate_formal_testing_route.py --kind status /tmp/testing_data_loop_status.json
```

## Visibility Semantics

```text
visible     all observed repositories have workflow_visible=true
partial     at least one observed repository is visible and at least one is not visible
incomplete  all observed repositories have workflow_visible=false
unknown     no observations were supplied
```

## Status Update Rule

A repository status observation may update:

```text
last_observed_commit
combined_status_visible
last_observed_conclusion
```

The command does not change:

```text
contract_status
ci_guard_status
implementation_posture
```

Those fields describe installed wiring, not transient workflow results.

## Completion Use

The testing data loop can be considered externally confirmed only when observations show workflow visibility for the relevant repositories and their conclusions support the expected route checks.
