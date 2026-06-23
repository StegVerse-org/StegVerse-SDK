# StegVerse SDK Mirror Handoff

## Current source of truth

This file is the handoff source of truth for `StegVerse-org/StegVerse-SDK` until superseded.

## Active goal

Goal 2: Universal transition-table SDK intake path.

The repository now proves:

```text
universal transition-table package fixture
→ non-authorizing Commitment Candidate fixture
→ SDK intake adapter
→ Commitment Candidate receipt
→ manifest
→ intake receipt
→ route eligibility receipt
→ Goal 2 activation verifier
```

No live ingestion, sandbox, runtime, commit-time standing determination, execution approval, or production trust-kernel execution is added by this path.

## Installed files

```text
stegverse/universal_transition_table_intake.py
stegverse/universal_transition_table_cli.py
tests/test_universal_transition_table_intake.py
tools/verify_universal_transition_table_intake_fixture.py
tools/verify_goal2_activation.py
docs/UNIVERSAL_TRANSITION_TABLE_INTAKE.md
examples/universal_transition_table_intake/README.md
examples/universal_transition_table_intake/transition_test_package.json
examples/universal_transition_table_intake/expected_result.json
examples/universal_transition_table_intake/replay_packet.json
examples/universal_transition_table_intake/commitment_candidate.json
stegverse/__init__.py exports handle_universal_transition_table_package and validate_commitment_candidate
github/workflows/sdk-demo-test.yml shown without leading period; actual path is dot-github workflows sdk-demo-test.yml
```

## Required invariant

```text
candidate_type == COMMITMENT_CANDIDATE
authorizing == false
inherits_review_authority == false
implies_standing == false
requires_fresh_standing_determination == true
```

## Verification commands

```bash
python tools/verify_goal2_activation.py
python tools/verify_universal_transition_table_intake_fixture.py
pytest tests/test_universal_transition_table_intake.py -v
pytest tests/ -v
```

## Remaining files or modules to install

Intended Org/Repo: `StegVerse-org/StegVerse-SDK`

```text
No remaining files for Goal 2 activation.
```

Intended Org/Repo: `StegVerse-org/core-node-runtime-demo`

```text
Goal 2 activation-ready; no remaining files for current route.
```

Intended Org/Repo: `StegVerse-org/universal-transition-table-test-path`

```text
admissibility wiki sync source once available.
```

## Next integration goal candidate

Goal 3 candidate: direct artifact transport from `universal-transition-table-test-path` into `StegVerse-SDK`, then into `core-node-runtime-demo`, while preserving the non-authorizing Commitment Candidate boundary.

## Archive posture

This handoff preserves the current build state so the complete thread can be archived without needing additional context to continue.
