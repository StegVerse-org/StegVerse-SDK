# StegVerse SDK Mirror Handoff

## Current source of truth

This file is the handoff source of truth for `StegVerse-org/StegVerse-SDK` until superseded.

## Active goal

Goal 4: micro-node governed return-path SDK validation.

Goal 3 established the governed LLM end-to-end demonstrator SDK intake path. Goal 4 validates that the SDK can inspect the LLM-adapter micro-node return path without becoming the runtime, granting execution authority, or persisting a master record.

## Goal 4 proof path

```text
LLM-adapter micro-node request fixture
-> SDK micro-node return-path validator
-> terminal governed return payload
-> return-path preservation check
-> no execution authority check
-> fixture verification script
```

## Goal 4 installed files

```text
docs/MICRO_NODE_RETURN_PATH_SDK.md
examples/micro_node_return_path/request.json
examples/micro_node_return_path/governed_return.json
scripts/verify_micro_node_return_path.py
scripts/verify_goal4.py
stegverse/micro_node_return_path.py
tests/test_micro_node_return_path.py
```

## Required invariants

```text
sdk_validation_is_execution == false
sdk_intake_is_authority == false
manifest_binding_is_persistence == false
receipt_handoff_is_master_record_installation == false
sdk_micro_node_validation_is_runtime_execution == false
sdk_micro_node_validation_grants_authority == false
sdk_micro_node_validation_persists_master_record == false
adapter_provider_output_is_authority == false
commitment_request_is_authority == false
returned_to_origin == true
```

## Goal 4 verification

```bash
python scripts/verify_goal4.py
```

The aggregate verifier includes the governed LLM packet, manifest, receipt, and micro-node return-path checks.

## Workflow consolidation

GitHub Actions validation is consolidated into one workflow:

```text
.github/workflows/sdk-demo-test.yml
```

The former standalone formal-route and dynamic-admissibility workflows were removed after their commands were absorbed into the consolidated workflow. The remaining workflow owns the Python test matrix, complete pytest suite, formal-route validation, dynamic-admissibility examples, comparison verification, package build, release, and PyPI publication.

## Parallel Goal 5: governed-vs-recursive comparison test bed

This Goal 5 build proceeds without displacing Goal 4. It gives Ecosystem Chat a governed SDK boundary for sending one normalized request through a StegVerse governed route and an external recursive route, validating both returned traces, and calculating transparent deltas.

### Installed Goal 5 files

```text
stegverse/llm_route_comparison.py
stegverse/comparison_transport.py
stegverse/comparison_orchestrator.py
schemas/llm_route_comparison.schema.json
docs/GOVERNED_VS_RECURSIVE_COMPARISON.md
scripts/verify_llm_route_comparison.py
scripts/run_llm_route_comparison.py
scripts/verify_comparison_orchestrator.py
tests/test_llm_route_comparison.py
tests/test_comparison_transport.py
tests/test_comparison_orchestrator.py
examples/llm_route_comparison/request.json
stegverse/__init__.py public comparison and orchestration exports
```

### Installed Goal 5 capabilities

```text
transport-neutral comparison request
shared task identity and output requirement binding
common route telemetry contract
MEASURED / CONFIGURED / DERIVED / UNAVAILABLE evidence classes
returned route-result validation
missing-metric rejection
task-identity preservation
measured-only delta calculation
deterministic comparison receipt
HTTP transport envelope
JSON import/export
paired route orchestration
parallel or sequential route submission
exact route-target matching
same immutable request envelope sent to both routes
fail-closed route identity and comparison identity checks
single canonical paired-result receipt
public SDK imports
standalone verifiers
```

### Goal 5 proof path

```text
one normalized request
-> SDK comparison package
-> paired orchestrator
-> core-node-runtime-demo governed route
-> LLM-adapter external recursive route
-> validated route results
-> DeltaCost / DeltaLatency / DeltaCalls / DeltaTokens / DeltaReceipts
-> reconstructable comparison receipt
-> Ecosystem Chat visualization
```

### Goal 5 verification

```bash
python scripts/verify_llm_route_comparison.py
python scripts/verify_comparison_orchestrator.py
python -m pytest tests/test_llm_route_comparison.py tests/test_comparison_transport.py tests/test_comparison_orchestrator.py -v
```

The consolidated workflow runs the complete test suite and both comparison verifiers. No additional workflow was created.

## Parallel Goal 6: cross-entry roles and transition usage ledger

Goal 6 defines how SDK, LLM Adapter, Ecosystem Chat, and future entry points describe their roles while preserving one session and usage lineage.

### Installed Goal 6 files

```text
schemas/entry_point_role.schema.json
schemas/transition_usage_event.schema.json
stegverse/entry_point_roles.py
stegverse/transition_usage.py
tests/test_entry_point_roles.py
tests/test_transition_usage.py
docs/ENTRY_POINT_ROLES.md
docs/TRANSITION_USAGE_LEDGER.md
stegverse/__init__.py public role and usage exports
```

### Installed Goal 6 capabilities

```text
canonical SDK / LLM Adapter / Ecosystem Chat role registry
primary and related role declarations
accepted-input and produced-output declarations
interaction-type declarations
entry-point authority-boundary validation
stable measurement_id plus metric_owner deduplication
cross-entry session aggregation
mixed-session rejection
MEASURED / CONFIGURED / DERIVED / UNAVAILABLE preservation
transition and origin-entry-point lineage
receipt reference preservation
deterministic usage-event and aggregation hashes
transition usage prepend contract
public SDK imports
```

### Goal 6 proof path

```text
entry point interaction
-> canonical role declaration
-> TRANSITION_USAGE_RECORDED event
-> measurement ownership validation
-> session and transition lineage preservation
-> duplicate measurement rejection
-> cross-entry session aggregation
-> transition prepend metadata
-> shared Ecosystem Usage Ledger
```

### Required Goal 6 invariants

```text
entry_point_acceptance_is_authority == false
translation_is_admissibility == false
display_is_execution == false
usage_event_is_authority == false
usage_event_is_admissibility == false
session_identity_preserved == true
transition_lineage_preserved == true
measurement_owner_is_unique == true
```

### Goal 6 verification

```bash
python -m pytest tests/test_entry_point_roles.py tests/test_transition_usage.py -v
```

The existing consolidated workflow discovers these tests and now verifies the public role and usage imports in both editable and built-wheel installations. No new workflow was created.

## Cross-repository state

```text
StegVerse-org/core-node-runtime-demo
  -> governed comparison request consumer installed
  -> governed route-result producer installed
  -> runtime usage-event emitter pending
  -> fixture-bound telemetry only; live governed inference pending

StegVerse-org/LLM-adapter
  -> external recursive route-result producer installed
  -> provider-neutral telemetry contract installed
  -> adapter role documentation installed
  -> machine-readable role declaration and provider usage-event emitter pending

StegVerse-org/StegVerse-SDK
  -> comparison request, transport, paired orchestration, validation, deltas, and receipt installed
  -> entry-point role registry and shared usage-event contract installed
  -> session aggregation and deduplication installed

StegVerse-Labs/Site
  -> Ecosystem Chat role page, transition prepend, session ledger, and comparison visualization pending

master-records
  -> comparison and usage-event custody, deduplication index, and reconstruction pointers pending
```

## Claim boundary

SDK package preparation, transport, orchestration, role description, usage recording, aggregation, and returned-result validation are not provider execution, runtime authority, admissibility, standing, or proof of universal cost superiority. Fixture, configured, and modeled values must remain explicitly classified and cannot be presented as measured results.

## Remaining files or modules

```text
StegVerse-org/core-node-runtime-demo
  -> live governed trace capture
  -> route endpoint
  -> runtime/node/closure usage-event emitter

StegVerse-org/LLM-adapter
  -> live recursive provider instrumentation
  -> route endpoint
  -> machine-readable adapter role declaration
  -> provider usage-event emitter

StegVerse-Labs/Site
  -> request duplication controls
  -> entry-point role and capability page
  -> transition usage prepend component
  -> cross-entry session ledger
  -> governed/recursive output panels and delta visualization

master-records
  -> usage-event custody
  -> measurement deduplication index
  -> session and transition lineage reconstruction
  -> receipt, hash, and telemetry pointer retention
```

## Archive posture

This handoff preserves Goal 4 and the complete Goal 5 and Goal 6 SDK state. Live CI execution, live provider/runtime traces, Site rendering, and Master-Records custody remain the external activation gates. Earlier conversation context is not required to continue.
