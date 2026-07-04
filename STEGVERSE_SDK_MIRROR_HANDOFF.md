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

## Archive posture

Not archive-ready until the aggregate Goal 4 verification command passes in a live clone/Codespaces environment and the wiki handoff reflects the portable governed return-path proof.
