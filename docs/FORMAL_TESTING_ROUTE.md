# Formal Testing Route

`StegVerse-org/StegVerse-SDK` is the user-facing intake boundary for formal testing datasets in the StegVerse ecosystem.

## Correct Testing Data Loop

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

This is the canonical data path for formal testing data.

## Master-Records Receipt Rule

Every ingestion point must emit an action receipt to `master-records`.

Required receipt emitters:

| Step | Ingestion point | Required master-records action receipt |
|------|-----------------|----------------------------------------|
| 1 | `StegVerse-org/StegVerse-SDK` or LLM Adapter | user intake receipt |
| 2 | `StegVerse-org ingestion` | org intake route receipt |
| 3 | `StegGhost/entity-sandbox-runner ingestion/CGE` | sandbox intake/CGE receipt |
| 4 | `ephemeral sandbox batch` | ephemeral execution receipt |
| 5 | `StegGhost/entity-sandbox-runner ingestion/CGE return validation` | sandbox return/CGE receipt |
| 6 | `StegVerse-org ingestion` | org return intake receipt |
| 7 | `User return` | user delivery receipt |

## Required Flow Invariant

```text
input dataset
→ user intake boundary
→ SDK / LLM Adapter receipt
→ StegVerse-org ingestion receipt
→ StegGhost ingestion/CGE receipt
→ ephemeral sandbox batch receipt
→ StegGhost return ingestion/CGE receipt
→ StegVerse-org return ingestion receipt
→ user delivery receipt
```

No route may consume or return a dataset unless the previous ingestion point has produced a receipt and sent its action receipt to `master-records`.

## Test Route Roles

| Route role | Repository | Purpose |
|-----------|------------|---------|
| User-facing intake | `StegVerse-org/StegVerse-SDK` | Accept user or LLM Adapter test data and bind it to a manifest and intake receipt. |
| Org ingestion | `StegVerse-org` ingestion surface | Route manifest-bound data toward the sandbox path and receive bounded results back. |
| Sandbox ingestion/CGE | `StegGhost/entity-sandbox-runner` | Validate sandbox task packets, run CGE checks, and admit only bounded sandbox execution. |
| Ephemeral sandbox batch | `StegGhost/entity-sandbox-runner` | Execute bounded tests without durable authority transfer. |
| Sandbox return ingestion/CGE | `StegGhost/entity-sandbox-runner` | Validate the sandbox result before return. |
| Org return ingestion | `StegVerse-org` ingestion surface | Validate returned result and prepare delivery to the user. |
| Master records | `master-records` | Receive action receipts from every ingestion point. |

## Secondary Evaluation Routes

Public demo, formal runner, standing-proof, and GLM/boundary tests must be fed from this receipt-bound loop, not from unbound side input.

| Evaluation | Repository | Position |
|-----------|------------|----------|
| Public demo validation | `StegVerse-org/stegverse-demo-suite` | Consumes already ingested and receipt-bound results for public demonstration. |
| Formal demo runner | `StegVerse-org/demo-suite-runner` | Consumes receipt-bound formalism packets after intake. |
| Standing proof | `StegVerse-Labs/Standing-Proof-Engine` | Consumes receipt-bound standing artifacts after intake. |
| Boundary / GLM case | `StegVerse-Labs/Boundary-Test` | Consumes receipt-bound boundary declarations after intake and private-review-first clearance. |

## Rule

```text
User supplies data.
SDK / LLM Adapter binds intake.
StegVerse-org ingestion routes.
StegGhost ingestion/CGE admits.
Ephemeral sandbox batch executes.
StegGhost ingestion/CGE validates return.
StegVerse-org ingestion returns.
User receives bounded result.
Every ingestion point sends an action receipt to master-records.
```
