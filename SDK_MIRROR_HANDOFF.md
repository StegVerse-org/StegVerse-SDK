# SDK Mirror Handoff

## Source of truth

This file is the current handoff and task source of truth for `StegVerse-org/StegVerse-SDK`.

## Active goal

```text
Goal: SDK-origin governed transition candidate emission with deterministic SPE commitment intake
Phase: emitter-and-SPE-envelope-installed-validation-pending
Result: LOCAL_IMPLEMENTATION_INSTALLED_VALIDATION_PENDING
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
tests/test_system_boundary.py
docs/SYSTEM_BOUNDARY_INGESTION.md
sdk.capabilities.json
```

Installed contract bindings:

```text
manifest field: system_boundary_declaration
receipt reference field: system_boundary_declaration_ref
model_has_execution_authority: false
consciousness_claim: not_evaluated
personhood_claim: not_evaluated
welfare_claim: not_evaluated
```

The validator rejects false continuity without feedback paths, authority escalation, missing commit boundaries, prohibited consciousness claims, and unexpected top-level fields.

## Current verification

Run through the existing SDK test surface; no new workflow was added:

```text
python -m unittest tests.test_transition_candidate
python -m unittest tests.test_spe_commitment_intake
pytest tests/test_system_boundary.py
```

Current state:

```text
sdk_to_spe_tests: validation_pending
system_boundary_tests: validation_pending
workflow_evidence: pending
release_readiness: not_ready_for_tag
```

## Next task

```text
1. Verify sdk-demo-test workflow includes and passes the new SPE intake and system-boundary tests.
2. Add a transport-neutral SPE consumer adapter or fixture in StegVerse-Labs/Standing-Proof-Engine.
3. Define the receipt-bound SPE return packet.
4. Preserve transition_id and run_id through SPE, delegation, and final receipt.
5. Record observed workflow evidence in master-records/orchestration.
6. Install runtime system-boundary declaration generation in StegVerse-org/LLM-adapter.
7. Bind generated declaration identifiers into governed session manifests and receipt handoffs.
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

A candidate manifest is not execution authority. SDK route ALLOW permits only progression to the next governed boundary. SPE ALLOW is not execution and must be bound to a returned receipt before downstream use. System-boundary validation is not a consciousness, personhood, welfare, admissibility, or standing determination.

## Archive readiness

This handoff contains the complete current SDK transition-candidate, SPE intake, and bounded system-boundary integration state. Earlier thread context is not required.
