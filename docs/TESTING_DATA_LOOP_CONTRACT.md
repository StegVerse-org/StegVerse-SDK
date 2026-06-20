# Testing Data Loop Contract

## Purpose

This document is the SDK-facing contract for the corrected formal testing data route.

The SDK or LLM Adapter is the user-facing intake boundary. Formal testing data must then move through StegVerse-org ingestion, StegGhost sandbox admission/execution/return validation, StegVerse-org return ingestion, and user delivery.

## Canonical Loop

```text
User
→ StegVerse-org/StegVerse-SDK or LLM Adapter
→ StegVerse-org ingestion
→ StegGhost/entity-sandbox-runner ingestion/CGE
→ ephemeral sandbox batch
→ StegGhost/entity-sandbox-runner ingestion/CGE return validation
→ StegVerse-org ingestion
→ User
```

## Receipt Rule

Every ingestion or execution boundary emits an action receipt to `master-records`.

A step may not hand off to the next step unless the current step has:

1. a local step receipt;
2. a dataset manifest hash;
3. prior receipt references;
4. `master-records.action_receipt_sent = true`.

## Executable Implementations

| Segment | Repository | Executable gate |
|---------|------------|-----------------|
| SDK intake contract | `StegVerse-org/StegVerse-SDK` | `scripts/validate_formal_testing_route.py --kind loop` |
| Org outbound / return ingestion | `StegVerse-org/demo_ingest_engine` | `scripts/run_org_ingestion_step.py` |
| Org handoff gate | `StegVerse-org/demo_ingest_engine` | `scripts/gate_ingestion_handoff.py` |
| End-to-end loop fixture | `StegVerse-org/demo_ingest_engine` | `scripts/run_testing_data_loop_demo.py` |
| End-to-end loop verification | `StegVerse-org/demo_ingest_engine` | `scripts/validate_testing_data_loop_chain.py` |
| Sandbox admission / batch / return | `StegGhost/entity-sandbox-runner` | `scripts/run_sandbox_step.py` |
| Sandbox handoff gate | `StegGhost/entity-sandbox-runner` | `scripts/gate_sandbox_handoff.py` |

## Required Ordered Steps

```text
human_input
sdk_or_llm_adapter_intake
stegverse_org_ingestion_outbound
stegghost_ingestion_cge_admission
ephemeral_sandbox_batch
stegghost_ingestion_cge_return_validation
stegverse_org_ingestion_return
human_delivery
```

## Completion State

The route is considered operationally wired when the following are true:

```text
SDK loop manifest validates.
SDK handoff manifest validates.
StegVerse-org outbound receipt validates.
StegVerse-org outbound handoff gates to StegGhost admission.
StegGhost admission receipt validates.
StegGhost admission handoff gates to ephemeral sandbox batch.
StegGhost return validation gates to StegVerse-org return ingestion.
StegVerse-org return ingestion gates to user delivery.
End-to-end loop receipt chain validates.
```

## Non-Bypass Rule

Public demos, formal runners, Boundary-Test / GLM cases, and Standing-Proof-Engine standing checks must consume receipt-bound testing artifacts from this loop. They must not accept unbound side input as formal testing data.
