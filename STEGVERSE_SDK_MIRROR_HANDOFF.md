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

### Cross-repository state

```text
StegVerse-org/core-node-runtime-demo
  -> governed comparison request consumer installed
  -> governed route-result producer installed
  -> fixture-bound telemetry only; live governed inference pending

StegVerse-org/LLM-adapter
  -> external recursive route-result producer installed
  -> provider-neutral telemetry contract installed
  -> configured fixture only; live provider trace capture pending

StegVerse-org/StegVerse-SDK
  -> comparison request, transport, paired orchestration, validation, deltas, and receipt installed

StegVerse-Labs/Site
  -> Ecosystem Chat paired execution and visualization pending

master-records
  -> comparison receipt custody and reconstruction pointers pending
```

### Claim boundary

SDK package preparation, transport, orchestration, and returned-result validation are not provider execution, runtime authority, admissibility, or proof of universal cost superiority. Public deltas must derive from like-for-like traces. Fixture, configured, and modeled values must remain explicitly classified and cannot be presented as measured results.

## Remaining files or modules

```text
StegVerse-org/core-node-runtime-demo
  -> live governed trace capture and route endpoint

StegVerse-org/LLM-adapter
  -> live recursive provider instrumentation and route endpoint

StegVerse-Labs/Site
  -> request duplication controls, route timeline, governed/recursive output panels, delta visualization

master-records
  -> receipt custody, hashes, telemetry pointers, reconstruction index
```

## Archive posture

This handoff preserves Goal 4 and the complete Goal 5 SDK comparison state. Live CI execution, live provider/runtime traces, Site rendering, and Master-Records custody remain the external activation gates. Earlier conversation context is not required to continue.
