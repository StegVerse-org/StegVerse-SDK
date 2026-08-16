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

## Status

```text
SDK-EVALUATOR-CONTRACT-CONSOLE-001: COMPLETE_VALIDATED_MERGED
```

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
.github/workflows/evaluator-contract-console-validation.yml
README.md
```

The contract output is non-authorizing and derives capability/evidence/profile vocabulary from `stegverse.public_inspection` constants rather than inventing a separate evaluator route.

The displayed JSON Schema enforces the same lane-specific provenance combinations used by the canonical public request contract, including production-vs-demo routing/containment and fail-closed external-consequence constraints.

## Public evaluator path

```text
install SDK
-> stegverse contract
-> optionally stegverse contract --schema / --example / --all
-> author conforming JSON anywhere
-> stegverse governance --select 0 --input <request.json>
   OR python -m stegverse.public_inspection_runtime run <request.json>
-> canonical governed route
```

The evaluator does not need to browse GitHub or request a developer-created testing route to discover the accepted contract.

## Boundary

```text
contract discovery grants authority: false
contract discovery executes governance: false
evaluator identity is decision input: false
expected observation is decision input: false
configuration may augment route: false
GitHub grants runtime authority: false
public caller credential required: false
```

## Validation evidence

Initial executable validation correctly exposed a validation-definition defect:

```text
run: 31962343447
result: FAILURE
cause: pytest-style test functions were invoked with unittest; zero tests ran
product failure: false
```

The validation definition was corrected to invoke pytest. Subsequent source validation passed:

```text
run: 31962419953
head: 49c656876ff247dfde208a582817bd02d0897232
result: SUCCESS
purpose: validate schema-aligned console implementation

run: 31962427681
head: 26c2bbf2d0ddd579705faff41bf8143ae82d5c57
result: SUCCESS
purpose: validate strengthened contract tests, including invalid cross-lane provenance rejection

run: 31962462067
head: 89686e5a9b975f3d5ccfd9c02dd5f05395b5937e
result: SUCCESS
purpose: validate final README-visible console contract state and executable copy/paste validation command
```

The workflow uses `permissions: {}` and verifies that `GITHUB_TOKEN` and `GH_TOKEN` are absent from the process environment before anonymously materializing public source. It exercises:

```text
pytest -q tests/test_evaluator_contract_console.py
stegverse contract
stegverse contract --schema
stegverse contract --example
python -m stegverse contract --all
```

and asserts the returned contract identity, schema title, non-authorizing example, and canonical submission command.

## Completion

```text
console contract discovery implementation remaining: 0
schema/runtime contract divergence remaining: 0
README discoverability remaining: 0
focused executable validation remaining: 0
source activation complete: true
```

The separate native `0B` `stegverse.ingress-manifest.v1` binding remains a different SDK goal and is still fail-closed. It is not required for the public-inspection JSON evaluator path completed here.
