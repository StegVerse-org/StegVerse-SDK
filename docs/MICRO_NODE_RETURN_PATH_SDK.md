# Micro-Node Return-Path SDK Validation

This document records the SDK side of the Goal 4 micro-node governed return-path proof.

## Purpose

`StegVerse-org/LLM-adapter` can express a governed LLM response as a micro-node-compatible transition request and receive a governed return payload. The SDK validates that fixture pair without becoming the runtime, granting execution authority, or persisting a master record.

## Proof path

```text
LLM-adapter micro-node request fixture
-> SDK micro-node return-path validator
-> terminal governed return payload
-> return-path preservation check
-> no execution authority check
-> fixture verification script
```

## Verification

```bash
python scripts/verify_micro_node_return_path.py
pytest tests/test_micro_node_return_path.py -v
```

## Boundary

```text
sdk_micro_node_validation_is_runtime_execution == false
sdk_micro_node_validation_grants_authority == false
sdk_micro_node_validation_persists_master_record == false
adapter_provider_output_is_authority == false
commitment_request_is_authority == false
returned_to_origin == true
```

## Next integration target

After adapter and SDK fixture validation are both green, a later integration can point to `StegVerse-002/micro-node-runtime` as a governed runtime target through a stabilized contract. That later integration remains separate from this fixture-bound proof.
