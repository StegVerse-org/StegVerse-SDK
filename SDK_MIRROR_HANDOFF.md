# SDK Mirror Handoff

## Source of truth

This file is the current handoff and task source of truth for `StegVerse-org/StegVerse-SDK`.

## Active goal

```text
Goal: SDK-origin governed transition candidate emission with deterministic SPE commitment intake
Phase: explicit-current-main-validation-installed-observation-pending
Result: LOCAL_IMPLEMENTATION_AND_CI_BINDING_INSTALLED_VALIDATION_PENDING
```

## Architecture

```text
SDK-origin request
-> emit schema-compatible DECLARED transition candidate
-> optional deterministic Commitment Candidate construction
-> transport-neutral Standing-Proof-Engine intake envelope
-> fresh standing determination
-> hybrid-collab-bridge normalization / delegation path remains separately governed
-> master-records/orchestration lifecycle
-> final receipt / custody / reconstruction
-> Site projection
```

The SDK is a sibling input nest. It does not grant execution, delegation, publication, orchestration, final-receipt, Master-Records, or SPE standing authority.

## Installed files

```text
stegverse/transition_candidate.py
stegverse/spe_commitment_intake.py
examples/sdk_transition_candidate.json
scripts/verify_sdk_transition_candidate.py
tests/test_transition_candidate.py
tests/test_spe_commitment_intake.py
docs/SDK_TO_SPE_COMMITMENT_INTAKE.md
sdk.capabilities.json
.github/workflows/sdk-demo-test.yml
SDK_MIRROR_HANDOFF.md
```

## Existing transition candidate posture

The emitter uses the canonical relationship shape owned by `master-records/orchestration` and emits:

```text
origin_class: SDK_INPUT
lifecycle_state: DECLARED
admissibility_result: PENDING
commit_time_validity: PENDING
final_receipt_id: null
master_record_status: NOT_YET_SUBMITTED
```

## SDK-to-SPE commitment intake

The intake module reuses:

```text
stegverse/universal_transition_table_intake.py::validate_commitment_candidate
```

It constructs a deterministic Commitment Candidate with:

```text
candidate_type: COMMITMENT_CANDIDATE
authorizing: false
inherits_review_authority: false
implies_standing: false
requires_fresh_standing_determination: true
```

It then produces a transport-neutral SPE envelope containing:

```text
transition_id
run_id
candidate_hash
envelope_hash
destination_repo: StegVerse-Labs/Standing-Proof-Engine
route_purpose: FRESH_STANDING_DETERMINATION
expected_result: ALLOW | DENY | FAIL_CLOSED
receipt_required: true
```

## Preserved HPS and orchestration roles

```text
StegVerse-org/HPS-runtime -> runtime standing state
StegVerse-Labs/Standing-Proof-Engine -> fresh standing determination
StegVerse-Labs/hybrid-collab-bridge -> sibling input normalization
StegVerse-Labs/Ecosystem-Delegation -> governed delegation evaluation
master-records/orchestration -> lifecycle, receipts, custody references, reconstruction
```

## Parallel governed-LLM system-boundary integration

This bounded workstream is subordinate to the active SDK-to-SPE goal and does not replace it.

Source doctrine and schema:

```text
StegVerse-Labs/admissibility-wiki
docs/governance/llm-consciousness-model-system-boundary.md
static/governance/system-boundary-declaration.schema.v0.1.json
```

Installed SDK artifacts:

```text
schemas/system-boundary-declaration.schema.v0.1.json
stegverse/system_boundary.py
stegverse/system_boundary_round_trip.py
stegverse/governed_llm_manifest.py
stegverse/governed_llm_receipt.py
tests/test_system_boundary.py
tests/test_system_boundary_round_trip.py
tests/test_governed_llm_system_boundary_binding.py
docs/SYSTEM_BOUNDARY_INGESTION.md
receipts/system-boundary-round-trip-installation-2026-07-14.json
sdk.capabilities.json
```

Installed contract bindings:

```text
manifest field: system_boundary_declaration
receipt field: system_boundary_declaration_receipt
receipt reference field: system_boundary_declaration_ref
manifest binding mode: optional until explicit migration
reference algorithm: sha256
model_has_execution_authority: false
authorizing: false
custody_transferred: false
admissibility_determined: false
consciousness_claim: not_evaluated
personhood_claim: not_evaluated
welfare_claim: not_evaluated
production_binding_enabled: false
```

The declaration validator rejects false continuity without feedback paths, authority escalation, missing commit boundaries, prohibited consciousness claims, and unexpected top-level fields.

The receipt round-trip verifier independently reconstructs:

```text
canonical declaration identity
declaration content hash
receipt body and receipt hash
declaration-reference digest
declaration-reference receipt hash
evidence-reference preservation
non-authority boundary fields
```

It fails closed on declaration tamper, receipt mismatch, digest drift, authority escalation, custody escalation, admissibility escalation, production-binding escalation, and consciousness reclassification.

The governed LLM manifest and receipt modules now also consume the adapter's actual optional `algorithm/digest/declaration_id` reference contract. They validate the declaration before manifest serialization, reject orphan or mismatched references, preserve legacy packets without boundary fields, and carry the validated reference into the receipt handoff. This serialization path remains non-authorizing and does not replace the stronger declaration/receipt/reference tuple verifier.

## Current verification

The existing SDK test surface still runs the complete suite. Commit `e2c1467be02dfd40b0f136684247e7e04715c963` made the SPE and declaration contracts explicit. Commit `49085cc67ac9a68d64feb6378c76e020cf4b822a` extended the explicit system-boundary step to the receipt round-trip suite. Commit `3120ba858392000053b398464e86856f8ae95014` added the governed manifest/receipt serialization suite:

```text
python -m unittest tests.test_transition_candidate tests.test_spe_commitment_intake
pytest tests/test_system_boundary.py tests/test_system_boundary_round_trip.py tests/test_governed_llm_system_boundary_binding.py -v
```

Current state:

```text
sdk_to_spe_tests: explicit_ci_binding_installed_observation_pending
system_boundary_tests: explicit_ci_binding_installed_observation_pending
system_boundary_round_trip_tests: explicit_ci_binding_installed_observation_pending
manifest_receipt_serialization_tests: explicit_ci_binding_installed_observation_pending
adapter_receipt_consumption: installed
adapter_manifest_serialization: installed_optional_legacy_compatible
adapter_production_binding: disabled
workflow_evidence: pending_current_main_run
release_readiness: not_ready_for_tag
```

Relevant round-trip commits:

```text
874063c94397a11a439fa674e6cebcf69c439da6  SDK round-trip verifier
610c3c571086bf6884122cd061d9a74fe770252f  round-trip and tamper tests
49085cc67ac9a68d64feb6378c76e020cf4b822a  sdk-demo-test integration
37a61dfbdcf161abf51d15fc6da9f5101224e7ea  installation receipt
```

Relevant manifest/receipt serialization commits:

```text
e3d43a072648ec09b9bcbe5a0477c9f58a3fe78b  initial optional manifest binding
5a6afcd388645b3c1534959a599c5cd2f8bc0a5b  receipt reference preservation
4933bc4fb9449f78344af2f951889aaf4a4c5fd4  adapter reference-contract reconciliation
bd2197bc39a28fa3b073cd64f01a2d19b7713bff  legacy and fail-closed serialization tests
3120ba858392000053b398464e86856f8ae95014  explicit route-validation binding
54eda9e5ca7c9002934e7178729dab059785f597  capability registration
```

## Next task

```text
1. Observe and record the current-main sdk-demo-test result containing commit 54eda9e5ca7c9002934e7178729dab059785f597 or later.
2. Repair only the first repository-local failing step, if any.
3. Preserve the workflow-bound SDK round-trip and manifest-serialization receipts after a successful run.
4. Preserve transition_id and run_id from the canonical SPE standing receipt into master-records/orchestration lifecycle evidence.
5. Define the governed execution-authority consumer contract for SPE ALLOW without converting ALLOW into execution.
6. Add an adapter-produced fixture that enters SDK manifest serialization without test-local reconstruction.
7. Keep adapter production system-boundary binding disabled until separately authorized.
8. Propagate verified status to Site, Publisher, admissibility-wiki, and stegguardian-wiki only after current-main evidence exists.
```

## Downstream destinations

```text
StegVerse-Labs/Standing-Proof-Engine
StegVerse-Labs/hybrid-collab-bridge
StegVerse-Labs/Ecosystem-Delegation
master-records/orchestration
StegVerse-org/LLM-adapter
StegVerse-Labs/Site
GCAT-BCAT-Engine/Publisher
StegVerse-Labs/admissibility-wiki
StegVerse-002/stegguardian-wiki
```

## Boundary

A candidate manifest is not execution authority. SDK route ALLOW permits only progression to the next governed boundary. SPE ALLOW is not execution and must be bound to a returned receipt before downstream use. System-boundary validation, receipt round-trip acceptance, manifest serialization, or receipt-reference preservation is not a consciousness, personhood, welfare, admissibility, custody, execution, or standing determination.

## Archive readiness

This handoff contains the complete current SDK transition-candidate, SPE intake, explicit CI binding, system-boundary validation, receipt round-trip, manifest serialization, and receipt-reference preservation state. Earlier conversation context is not required.
