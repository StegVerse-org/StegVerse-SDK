# SDK Machine Contract Mirror Handoff

Parent Goal: `SVORG-STEGOS-PORTABILITY-001`
Registry: `StegVerse-org/.github:orchestration/task-registry.json`
Coordination state: ACTIVE (`in_progress`); COSV: ABSENT_FROM_CURRENT_TASK_REGISTRY_SCHEMA.
SDK baseline: `50d6ed8c1e9058092ce5056fa09157804b2c70d3`.
Parent handoff: `StegVerse-org/.github:docs/STEGOS_PORTABILITY_MIRROR_HANDOFF.md`.


## Test 5/6 external submission boundary — 2026-10-02

External instructions terminate at `SUBMIT_CANONICAL_MANIFEST` and `RETAIN_SUBMISSION_RESULT_AND_EVIDENCE`. Interlock/InTr is `INTERNAL_POST_SUBMISSION`; `EXTERNAL_INTERLOCK_INTR` is deferred to a separate successor expansion after Tests 5/6. This changes the caller instruction boundary, not the retained experiment, Test 5-before-Test 6 ordering, or downstream receipt/custody acceptance. Source tests are not Test 5/6 runtime results.

`SDK_MACHINE_CONTRACT` derives from existing SDK builder signatures, processor/route declarations, return projections and console commands. The adapter consumes that SDK projection instead of maintaining a second instruction recipe. The console wrapper already dispatched manifest/external-run; its top-level help omitted them. Shared dispatch/help declarations repair that discovery mismatch.

The external-framework helper currently reports `SDK_LOCAL_MANIFEST_HANDOFF`; it does not prove receiver observation. Adapter predecessor checks establish structural validity only, not authenticated standing. Production endpoint binding, authentic standing, runtime execution, deployment and custody remain NOT_PROVEN. No endpoint, runtime, credential path or authority was created.

Validation: 35 source tests and 4 subtests passed locally across SDK machine-contract/manifest-builder and adapter discovery-submission/governed-ingress suites. Injected receivers are explicitly fixtures; no authentic submission or runtime observation is claimed.
