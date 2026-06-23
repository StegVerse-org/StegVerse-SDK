# Goal 3 Cross-Repo Artifact Transport

Goal 3 defines direct artifact transport from `StegVerse-org/universal-transition-table-test-path` into `StegVerse-org/StegVerse-SDK`, then toward `StegVerse-org/core-node-runtime-demo`.

## Current boundary

Goal 3 does not enable live runtime execution.

It only defines transport requirements for moving an already verified package into SDK intake while preserving the non-authorizing Commitment Candidate boundary.

## Transport path

```text
universal-transition-table-test-path
→ artifact transport manifest
→ StegVerse-SDK intake
→ SDK intake result
→ core-node-runtime-demo boundary consumer
```

## Required transported artifacts

```text
transition_test_package.json
expected_result.json
replay_packet.json
commitment_candidate.json
```

## Required invariant

```text
candidate_type == COMMITMENT_CANDIDATE
authorizing == false
inherits_review_authority == false
implies_standing == false
requires_fresh_standing_determination == true
```

## Non-scope

```text
runtime execution
ingestion execution
sandbox execution
commit-time standing determination
execution approval
```
