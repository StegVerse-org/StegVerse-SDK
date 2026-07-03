# Micro-Node Runtime Target

`StegVerse-SDK` treats `StegVerse-002/micro-node-runtime` as a governed runtime target once adapter-originated transition requests can be validated without granting execution authority.

## Validation role

The SDK validates fixture-bound micro-node adapter artifacts before any live runtime call is introduced.

```text
LLM-adapter fixture
-> SDK validation
-> request shape check
-> governed return check
-> authority non-escalation check
-> receipt reference check
-> validation result
```

## Required invariants

```text
transition_id is preserved
return_path is preserved
returned_to_origin == true
execution_authority_granted == false
provider_output_is_authority == false
decision in {ALLOW, DENY, FAIL_CLOSED}
receipt_hash is present
```

## Boundary

This SDK validation surface does not call the live micro-node runtime, does not call a live LLM provider, does not mutate repositories, does not post publicly, and does not grant execution authority.

## Later integration

After this fixture validation is green, a later integration goal can add a callable runtime target that imports or invokes `micro-node-runtime` directly.
