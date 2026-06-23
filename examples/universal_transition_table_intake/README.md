# Universal Transition Table Intake Fixture

This fixture exercises the SDK intake proof path with a non-authorizing Commitment Candidate.

## Path

```text
transition_test_package.json
→ expected_result.json
→ replay_packet.json
→ commitment_candidate.json
→ SDK intake adapter
→ sdk_intake_result.json
```

## Non-authorizing invariant

```text
candidate_type == COMMITMENT_CANDIDATE
authorizing == false
inherits_review_authority == false
implies_standing == false
requires_fresh_standing_determination == true
```

## Verify

```bash
python tools/verify_universal_transition_table_intake_fixture.py
```

The verifier writes:

```text
examples/universal_transition_table_intake/sdk_intake_result.json
```

## Non-scope

```text
runtime execution
ingestion execution
sandbox execution
commit-time standing determination
execution approval
```
