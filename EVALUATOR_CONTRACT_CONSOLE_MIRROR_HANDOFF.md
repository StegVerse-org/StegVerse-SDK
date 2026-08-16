# Evaluator Contract Console Mirror Handoff

## Source of truth

```text
organization: StegVerse-org
repository: StegVerse-SDK
branch: main
credential authority: TV/TVC
runtime GitHub credential required: false
```

## Goal

An evaluator with an installed SDK must be able to discover the public evaluator request contract directly from the console without first browsing repository documentation.

## Implemented

```text
stegverse contract
stegverse contract --schema
stegverse contract --example
stegverse contract --all
python -m stegverse contract [same flags]
```

Implementation:

```text
stegverse/evaluator_contract.py
stegverse/evaluator_console.py
stegverse/__main__.py
pyproject.toml
tests/test_evaluator_contract_console.py
```

The contract output is non-authorizing and derives capability/evidence/profile vocabulary from `stegverse.public_inspection` constants rather than inventing a separate evaluator route.

## Boundary

```text
contract discovery grants authority: false
contract discovery executes governance: false
evaluator identity is decision input: false
expected observation is decision input: false
configuration may augment route: false
```

The evaluator still submits a conforming request with:

```text
stegverse governance --select 0 --input <request.json>
```

or directly through the canonical public inspection runtime.

## Validation state

Focused source tests have been added. No CI result is claimed by this handoff until a workflow/run or equivalent sovereign validation receipt is observed for the new head.

## Remaining

```text
README command discoverability update: pending
CI/source execution validation: pending
native 0B stegverse.ingress-manifest.v1 binding: separate goal, still fail-closed
```
