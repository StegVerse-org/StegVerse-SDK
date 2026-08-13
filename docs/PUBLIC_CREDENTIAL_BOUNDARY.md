# Public credential boundary

The public StegVerse SDK does not ask evaluators, contributors, LLMs, or ordinary callers to provide GitHub tokens, provider keys, private keys, passwords, or other protected runtime credential material.

Protected credential and route semantics belong to TV/TVC. Public SDK inputs and inspection requests are non-authorizing.

## Sovereign evaluator path

The canonical `stegverse.public_inspection_runtime` path is sovereign/local and uses pinned canonical Core-Lite, StegCore/StegGate, and Master Records implementations with local validation custody.

It does not require a public caller to manage a protected Master Records credential and does not use a GitHub token as StegVerse runtime authority.

```text
public caller credential authority: NONE
GitHub token runtime authority: NONE
protected credential semantics: TV/TVC
manifest_receipt_id authority effect: NONE
```

Optional hosted transports, if used separately, do not change this authority model and are not prerequisites for the sovereign evaluator path.

## Authority invariants

```text
credential presence != authority
public SDK request != authority
provider output != authority
manifest_receipt_id != authority
GitHub != StegVerse runtime authority
Master Records custody != execution authority
```

Canonical evaluator state and validation evidence are recorded in `SDK_MIRROR_HANDOFF.md` and `validation/SOVEREIGN_FROZEN_EVALUATOR_VALIDATION_2026-08-13.md`.
