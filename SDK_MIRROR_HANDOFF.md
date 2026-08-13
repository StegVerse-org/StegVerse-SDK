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
```

No person-specific evaluator route is canonical.

## Governing invariant

```text
every ecosystem state transition is recorded in Master Records
successful governed SDK run without Master Records custody: PROHIBITED
successful replay/reconstruction return without operation-transition custody: PROHIBITED
caller return projection may suppress Master Records custody: FALSE
```

## Production-validation route

The governed SDK runtime now uses the manifested Core-Lite route carrier and targets the deployed StegCore service rather than evaluating locally.

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

## Hosted deployment gate

The existing Render `steggate-core` service auto-deploy attempted the StegCore merged commit above. Render canceled the build before execution because the workspace had exhausted build-pipeline minutes for the current billing period.

```text
repository implementation: COMPLETE
StegCore repository CI: PASS
new live StegCore manifested-validation endpoint: NOT YET ACTIVE
hosted SDK -> Core-Lite -> StegCore -> Master Records integrated run: NOT YET EXECUTED
genuine evaluator receipt IDs from that hosted route: NOT YET ISSUED
```

This is an external hosting-capacity blocker, not a repository test failure. Do not substitute older local or ephemeral receipt identifiers.

## Remaining evaluator-readiness gate

```text
1. restore hosted build capacity or otherwise activate the merged StegCore endpoint on the canonical hosted surface;
2. execute T0, T1-A, and T1-B through the hosted production-validation route;
3. verify one transaction identity per manifested run;
4. verify complete MRR-* route transition chain and MR-* exact-run custody;
5. execute replay and reconstruction and verify MRO-* operation transition custody;
6. retain PASS evidence and only then hand off genuine receipt IDs.
```

## Release state

Do not claim evaluator-ready production validation or release until the hosted integrated run above passes.
