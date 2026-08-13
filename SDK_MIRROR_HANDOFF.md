# SDK Mirror Handoff

## Source of truth

```text
organization: StegVerse-org
repository: StegVerse-SDK
canonical_branch: main
```

Live repository state, immutable commits, validation evidence, scoped mirror handoffs, and this file supersede prior chat claims.

## Goal inventory

```text
SDK-PUBLIC-CONSOLE-001: COMPLETE_RELEASED
SDK-GENERAL-EVALUATION-RELATIONSHIP-001: COMPLETE_RELEASED
SDK-NO-GITHUB-AUTHORITY-003: COMPLETE_RELEASED
SDK-PUBLIC-INSPECTION-ENTRY-001: COMPLETE_VALIDATED_MERGED, NOT_RELEASED
SDK-PUBLIC-INSPECTION-GOVERNED-BINDING-002: COMPLETE_STATIC_VALIDATED_MERGED, NOT_RELEASED
SDK-PUBLIC-INSPECTION-GOVERNED-TEST-004: SUPERSEDED_BY_CUSTODY_BACKED_RUNTIME
SDK-PUBLIC-INSPECTION-CUSTODY-REPLAY-005: CODE_COMPLETE_PENDING_HOSTED_DEPLOY_AND_INTEGRATED_RUN
SDK-PUBLIC-GOVERNANCE-DOCS-006: COMPLETE_MERGED
SDK-PUBLIC-CREDENTIAL-BOUNDARY-007: DOCS_COMPLETE; TVC_TRANSPORT_IMPLEMENTATION_CLAIM_ACTIVE
```

No person-specific evaluator route is canonical.

## Public governance/navigation reconciliation

The public evaluator-facing path is now the ordinary SDK repository and installed console rather than a private instruction channel.

Canonical navigation:

```text
000 -> optional worked transparency/demo
00  -> optional return/explanation configuration
0   -> ordinary governed submission
1   -> replay by manifest_receipt_id
2   -> reconstruction by manifest_receipt_id
```

Primary public surfaces:

```text
README.md
docs/SDK_CONSOLE.md
docs/PUBLIC_INSPECTION_ENTRY.md
docs/PUBLIC_CREDENTIAL_BOUNDARY.md
SDK_README.md -> compatibility pointer only
```

The README explicitly distinguishes the five-option governance navigation from focused lower-level surfaces such as AdmittedCode and LLM admissibility.

## Credential authority correction

Originating requirement:

```text
protected runtime secrets/tokens are managed by TV/TVC
public SDK caller credential handling is not a supported path
GitHub token runtime authority: NONE
```

Public documentation no longer instructs evaluators to place protected Master Records credentials into public SDK commands or public environment instructions. Custody-backed production validation remains an authorized-runtime operation.

Canonical credential-neutral transport continuation:

```text
StegVerse-Labs/TVC/tasks/TVC-MASTER-RECORDS-CUSTODY-BROKER-004.json
StegVerse-Labs/TVC/docs/MASTER_RECORDS_CUSTODY_BROKER_MIRROR_HANDOFF.md
```

The current SDK production-validation source still contains a direct authenticated Master Records transport implementation. That source is not declared caller-facing authority. Full source reconciliation is not complete until the TV/TVC broker consumer replaces direct caller-token inputs and is deterministically validated. Do not represent public credential-neutral custody execution as active before that integration passes.

## Governing invariant

```text
every ecosystem state transition is recorded in Master Records
successful governed SDK run without Master Records custody: PROHIBITED
successful replay/reconstruction return without operation-transition custody: PROHIBITED
caller return projection may suppress Master Records custody: FALSE
credential presence != authority
manifest_receipt_id != authority
```

## Production-validation route

The governed SDK runtime uses the manifested Core-Lite route carrier and targets the deployed StegCore service rather than evaluating locally.

```text
SDK entry
-> Core-Lite manifested route carrier
-> Master Records MRR-* route transition custody
-> deployed StegCore /v1/manifested-validation
-> canonical StegGate evaluation
-> StegCore manifested transaction receipts
-> Master Records MR-* exact-run custody
-> Core-Lite return ingestion/CGE
-> Master Records MRR-* return transition custody
-> SDK return
```

One upstream `transaction_id` is preserved across the route manifest and StegCore manifested transaction. Production-validation provenance is bound into the route manifest and retained exact-run evidence.

The StegCore service endpoint was merged in StegCore PR #90 as:

```text
083557adec1bdbace09ebd10fb0765eb8e9a9d08
```

All five required StegCore repository workflows passed before that merge.

Core-Lite route carrier is merged as:

```text
72bdb0f110031ccc2cd98b8ebb7c22b1ab7326f8
```

Master Records route and replay/reconstruction transition custody is merged as:

```text
d0828441f2e92de736df1123bad5668f67e935fc
```

## Replay

Replay is executable against a retained `MR-*` source and creates its own Master Records operation trajectory:

```text
REQUESTED
-> SOURCE_RESOLVED
-> EVALUATED
-> RETURNED
```

The original exact run is not mutated and its consequence is not re-executed. The replay artifact is not returned unless all operation transitions are recorded.

## Reconstruction

Reconstruction creates its own Master Records operation trajectory:

```text
REQUESTED
-> SOURCE_RESOLVED
-> ARTIFACT_DERIVED
-> RETURNED
```

The original exact run remains immutable and the original consequence is not re-executed.

## Local model/runtime convergence

The session requirements to replace descriptive local-model selection with executable discovery/launch/inference/proof and to formally develop a local model are already complete in the canonical owner and must not be duplicated in the SDK.

```text
canonical_owner: StegVerse-002/micro-node-runtime
handoff: docs/SOVEREIGN_LOCAL_MODEL_RUNTIME_MIRROR_HANDOFF.md
goal: SOVEREIGN-LOCAL-MODEL-001
state: COMPLETE_RELEASED
reference_model: stegverse-reference-lm-v1
github_token_required: false
third_party_inference_required: false
credential_authority: TV/TVC
```

Continuation of live activation is machine-owned through the resident sovereign heartbeat, TVC route authority, LLM-adapter transport, and Master Records custody. No SDK implementation claim exists for that lane.

## Hosted deployment gate

The existing Render `steggate-core` service auto-deploy attempted the merged StegCore manifested-validation endpoint. The recorded handoff evidence says Render canceled the build before execution because the workspace had exhausted build-pipeline minutes for the billing period.

```text
repository implementation: COMPLETE
StegCore repository CI: PASS
new live StegCore manifested-validation endpoint: NOT YET CONFIRMED ACTIVE
hosted SDK -> Core-Lite -> StegCore -> Master Records integrated run: NOT YET EXECUTED
genuine evaluator receipt IDs from that hosted route: NOT YET ISSUED
```

This is a hosted activation/evidence blocker, not a repository test failure. Do not substitute older local or ephemeral receipt identifiers.

## Remaining evaluator-readiness gate

```text
1. complete TV/TVC credential-neutral Master Records custody transport and SDK consumer integration;
2. activate or otherwise directly observe the merged StegCore manifested-validation endpoint on the canonical hosted surface;
3. execute T0, T1-A, and T1-B through the canonical production-validation route;
4. verify one transaction identity per manifested run;
5. verify complete MRR-* route transition chain and MR-* exact-run custody;
6. execute replay and reconstruction and verify MRO-* operation transition custody;
7. retain PASS evidence and only then hand off genuine receipt IDs.
```

## Session-specific requirements transferred

The following unique requirements from the current conversation are now durable:

1. public README is the primary evaluator entry point;
2. cloned-console documentation must match the public README;
3. `000/00/0/1/2` is the human-facing governance workflow;
4. AdmittedCode is a focused subsystem test surface, not the whole evaluator workflow;
5. public SDK can be featured as a governance experiment/test environment for AdmittedCode, StegGate-style admissibility, LLM output, replay, and reconstruction;
6. protected runtime credentials are managed by TV/TVC and are not a caller-managed public SDK concern;
7. local-runtime discovery/launch/proof and formal local-model development are merged into the canonical micro-node-runtime workstream and are not duplicated here;
8. Eduardo-style evaluator handoff remains ordinary SDK plus genuine T0/T1-A/T1-B manifest receipt IDs after exact-run custody validation.

Items 1–8 are transferred to repository state or canonical continuation records. The remaining executable implementation is the TV/TVC custody transport integration and machine/hosting activation evidence.

## Collision / claim state

```text
SDK public documentation: COMPLETE_MERGED; no active implementation claim
local model/runtime: MERGED_INTO_CANONICAL_WORKSTREAM -> StegVerse-002/micro-node-runtime/docs/SOVEREIGN_LOCAL_MODEL_RUNTIME_MIRROR_HANDOFF.md
Master Records credential-neutral transport: CLAIMED_FOR_IMPLEMENTATION -> StegVerse-Labs/TVC/tasks/TVC-MASTER-RECORDS-CUSTODY-BROKER-004.json
production evaluator hosted activation: BLOCKED / activation evidence pending
T0/T1-A/T1-B execution: BLOCKED until custody transport + hosted StegCore prerequisites are observable
```

## Release state

Do not claim evaluator-ready production validation, genuine evaluator receipt IDs, or public custody-backed execution until the integrated route above passes. Credential-free local SDK demos/navigation remain public and usable independently of that activation gate.
