# StegVerse SDK Mirror Handoff

## Current source of truth

This file is the handoff source of truth for `StegVerse-org/StegVerse-SDK` until superseded.

## Active goal

Goal 2: Universal transition-table SDK intake adapter.

The repository should prove:

```text
verified universal transition-table package
→ SDK intake adapter
→ manifest
→ intake receipt
→ route eligibility receipt
```

No live ingestion, sandbox, runtime, or production trust-kernel execution is added by this adapter.

## Installed files

```text
stegverse/universal_transition_table_intake.py
stegverse/universal_transition_table_cli.py
tests/test_universal_transition_table_intake.py
docs/UNIVERSAL_TRANSITION_TABLE_INTAKE.md
stegverse/__init__.py exports handle_universal_transition_table_package
github/workflows/sdk-demo-test.yml shown without leading period; actual path is dot-github workflows sdk-demo-test.yml
```

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
live runtime boundary validator after CI is green
runtime receipt fixture after boundary validator is accepted
```

Intended Org/Repo: `StegVerse-org/universal-transition-table-test-path`

```text
admissibility wiki sync source once available
```

## Next step

Run CI. If green, continue in `StegVerse-org/core-node-runtime-demo` with live runtime boundary validator, still without ingestion, sandbox, or micro-node execution.

## Archive posture

This handoff preserves the current build state so the complete thread can be archived without needing additional context to continue.
