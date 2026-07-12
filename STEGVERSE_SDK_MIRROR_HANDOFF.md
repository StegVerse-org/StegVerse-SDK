# StegVerse SDK Mirror Handoff

## Current source of truth

This file is the handoff source of truth for `StegVerse-org/StegVerse-SDK` until superseded.

## Active goal

Goal 4: micro-node governed return-path SDK validation.

Goal 3 established the governed LLM end-to-end demonstrator SDK intake path. Goal 4 now validates that the SDK can inspect the LLM-adapter micro-node return-path fixture pair without becoming the runtime, granting execution authority, or persisting a master record.

## Goal 4 proof path

```text
LLM-adapter micro-node request fixture
-> SDK micro-node return-path validator
-> terminal governed return payload
-> return-path preservation check
-> no execution authority check
-> fixture verification script
```

## Installed baseline already present

```text
sdk.capabilities.json
docs/GOVERNED_LLM_SDK_ACTIVATION.md
docs/GOVERNED_LLM_SESSION_PACKETS.md
scripts/smoke_governed_llm_sdk.py
stegverse/governed_llm_session.py
stegverse/governed_llm_session_intake.py
stegverse/governed_llm_manifest.py
stegverse/governed_llm_receipt.py
tests/test_governed_llm_session.py
tests/test_governed_llm_session_intake.py
tests/test_governed_llm_manifest.py
tests/test_governed_llm_receipt.py
examples/governed_llm_demo/session_packet.simple_query.json
examples/governed_llm_demo/README.md
scripts/verify_governed_llm_demo_packet.py
tests/test_governed_llm_demo_packet.py
```

## Installed for Goal 4 on current build branch

```text
docs/MICRO_NODE_RETURN_PATH_SDK.md
examples/micro_node_return_path/request.json
examples/micro_node_return_path/governed_return.json
scripts/verify_micro_node_return_path.py
scripts/verify_goal4.py
stegverse/micro_node_return_path.py
tests/test_micro_node_return_path.py
```

## Required invariant

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

## Canonical verification command

```bash
python scripts/verify_goal4.py
```

The aggregate verifier runs:

```bash
python scripts/smoke_governed_llm_sdk.py
python scripts/verify_governed_llm_demo_packet.py
python -m pytest tests/test_governed_llm_demo_packet.py -v
python scripts/verify_micro_node_return_path.py
python -m pytest tests/test_micro_node_return_path.py -v
```

## Upstream sync targets

```text
StegVerse-org/LLM-adapter
  -> emits the governed session demo packet
  -> emits the micro-node-compatible governed return-path fixtures
```

## Downstream sync target

```text
StegVerse-Labs/admissibility-wiki
  -> documents the public demo overview and verification path
  -> publishes the Goal 4 portable governed return-path proof
```

## Remaining files or modules to install

```text
None for SDK Goal 4 fixture-bound proof.
```

## Workflow consolidation

GitHub Actions validation has been consolidated into:

```text
.github/workflows/sdk-demo-test.yml
```

The former standalone workflows were removed after their commands were absorbed into the consolidated workflow:

```text
.github/workflows/formal-testing-route-validate.yml
.github/workflows/dynamic-admissibility-tests.yml
```

The consolidated workflow now owns the Python-version test matrix, complete pytest suite, formal-route validation, dynamic-admissibility examples, Goal 5 comparison verification, package build, GitHub release, and PyPI publication. This reduces workflow-level duplication while preserving validation coverage as separate jobs and steps.

## Parallel Goal 5 candidate: governed-vs-recursive comparison test bed

This candidate is being developed without displacing Goal 4. It prepares the SDK-side contract needed for Ecosystem Chat to compare one normalized request across a StegVerse governed route and an external recursive LLM route.

### Installed candidate files

```text
stegverse/llm_route_comparison.py
schemas/llm_route_comparison.schema.json
tests/test_llm_route_comparison.py
docs/GOVERNED_VS_RECURSIVE_COMPARISON.md
scripts/verify_llm_route_comparison.py
stegverse/__init__.py public comparison exports
```

### Installed candidate capabilities

```text
transport-neutral comparison request
shared task identity and output requirement binding
common route telemetry contract
MEASURED / CONFIGURED / DERIVED / UNAVAILABLE evidence classes
returned route-result validation
missing-metric rejection
task-identity preservation check
measured-only delta calculation
comparison receipt generation
comparison receipt deterministic SHA-256
public SDK imports
standalone fixture verifier
```

### Candidate proof path

```text
one normalized request
-> SDK comparison package
-> StegVerse governed route + external recursive route
-> shared telemetry contract
-> returned route traces
-> SDK route-result validation
-> DeltaCost / DeltaLatency / DeltaCalls / DeltaTokens / DeltaReceipts
-> reconstructable comparison receipt
-> Ecosystem Chat visualization
```

### Canonical candidate verification commands

```bash
python scripts/verify_llm_route_comparison.py
python -m pytest tests/test_llm_route_comparison.py -v
```

### Remaining Goal 5 integrations

```text
StegVerse-org/StegVerse-SDK
  -> add runtime transport adapter
  -> add user-facing comparison CLI
  -> add receipt import/export helpers

StegVerse-org/core-node-runtime-demo
  -> accept SDK comparison packages
  -> execute the governed route
  -> emit common telemetry and receipt-linked evidence

StegVerse-org/LLM-adapter
  -> execute or observe external recursive provider routes
  -> emit provider-neutral cost, latency, call, token, retry, and tool traces

StegVerse-Labs/Site
  -> duplicate one Ecosystem Chat request across selected routes
  -> render governed output, recursive output, route bars, and delta metrics

master-records
  -> retain route hashes, telemetry, receipts, and reconstruction pointers
```

### Candidate claim boundary

SDK package preparation and returned-result validation are not provider execution, runtime authority, or proof of cost superiority. Public deltas must come from actual traces or be explicitly marked configured or modeled.

## Archive posture

Not archive-ready until the consolidated validation workflow and aggregate Goal 4 verification command pass in a live GitHub Actions or clone/Codespaces environment and the wiki handoff reflects the portable governed return-path proof. Goal 5 remains a parallel candidate until its cross-repository execution path is installed and exercised.
