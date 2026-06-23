# StegVerse SDK Mirror Handoff

## Current source of truth

This file is the handoff source of truth for `StegVerse-org/StegVerse-SDK` until superseded.

## Active goal

Goal 2: Universal transition-table SDK intake adapter with non-authorizing Commitment Candidate support.

The repository should prove:

```text
verified universal transition-table package
→ optional non-authorizing Commitment Candidate
→ SDK intake adapter
→ commitment candidate receipt
→ manifest
→ intake receipt
→ route eligibility receipt
```

No live ingestion, sandbox, runtime, commit-time standing determination, execution approval, or production trust-kernel execution is added by this adapter.

## Installed files

```text
stegverse/universal_transition_table_intake.py
stegverse/universal_transition_table_cli.py
tests/test_universal_transition_table_intake.py
docs/UNIVERSAL_TRANSITION_TABLE_INTAKE.md
stegverse/__init__.py exports handle_universal_transition_table_package and validate_commitment_candidate
github/workflows/sdk-demo-test.yml shown without leading period; actual path is dot-github workflows sdk-demo-test.yml
```

## Non-authorizing invariant

The Commitment Candidate must satisfy:

```text
candidate_type == COMMITMENT_CANDIDATE
authorizing == false
inherits_review_authority == false
implies_standing == false
requires_fresh_standing_determination == true
```

It presents a reviewed transition for a fresh standing determination. It does not approve execution, inherit review authority, or create standing.

## Verification commands

```bash
pytest tests/test_universal_transition_table_intake.py -v
pytest tests/ -v
```

## Remaining files or modules to install

Intended Org/Repo: `StegVerse-org/StegVerse-SDK`

```text
optional console script entry point in pyproject.toml after CLI interface stabilizes
optional fixture import from universal-transition-table-test-path once cross-repo fixture transport is installed
```

Intended Org/Repo: `StegVerse-org/core-node-runtime-demo`

```text
Goal 2 activation-ready; no remaining files for current route
```

Intended Org/Repo: `StegVerse-org/universal-transition-table-test-path`

```text
admissibility wiki sync source once available
```

## Next step

Continue with cross-repo fixture transport only after this SDK path is green.

## Archive posture

This handoff preserves the current build state so the complete thread can be archived without needing additional context to continue.
