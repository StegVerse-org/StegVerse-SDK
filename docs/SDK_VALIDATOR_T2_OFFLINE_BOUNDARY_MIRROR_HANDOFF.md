# SDK #484 T2 — Offline Pinned Organization Boundary Mirror Handoff

Goal reference: StegVerse-org/StegVerse-SDK#484, T2.
Canonical Goal Task ID / COSV: unresolved; reconcile with StegVerse-Labs/.github Registry and existing successor owners before governed runtime migration.
Status: SOURCE_CANDIDATE / RUNTIME_NOT_OBSERVED / CI_NOT_YET_VALIDATED.

## Repair
- Replaces the live GitHub boundary read in `stegverse/manifest_execution.py` with an SDK-installed immutable JSON snapshot.
- Canonical origin: `StegVerse-Labs/.github:org-runtime/interlock-intr.json@aa2f89ac877e6a84bedb81a8b4efb30f4910d5f4`.
- Expected Git blob SHA-1: `a1f61d82a38a817a1dd2749505d8802dd09a22f8`. Check the blob header and content at every load; mismatch yields non-ALLOW.
- Wheel/sdist package data includes `stegverse/pinned_sources/*.json`.
- No added dependencies. No remote machine, network, hosted endpoint, receiver liveness or observer gate.
- Existing `canonical_source_fetcher` argument retained for call compatibility, but cannot substitute runtime source.
- Interlock/InTr retains transition authority; this snapshot is a source binding, not runtime admission evidence.

## Validation and disposition
Run the exact-head SDK tests including `tests/test_pinned_organization_boundary.py`, manifest-state-transition integration and existing fetcher-fixture tests; repair failures on this same branch before merge. Check installed wheel/sdist contents. Do not claim CI or runtime validation until actually observed. Organization-ledger runtime reality and non-gating Master Records remain distinct.

## Exact-head validation progress
- Head `66bdc2028d14d9e83c17553ee60e0cded4bec644`: 29 of 30 GitHub Actions workflows succeeded; test-suite ratchet was still running when observed.
- Manifest Builder Source Validation now succeeds after correcting the obsolete injected-source-failure expectation.
- No merge authorized until the ratchet completes and all required checks are green; source checks do not establish authentic runtime/Organization ledger receipts.

## Exact-head CI closeout — 2026-10-13
At T2 PR #505 head `4544ba4922d2d9a40fb2292a0ef6552d6a23cd70`, 30 of 30 GitHub Actions workflows completed successfully, including Test suite ratchet. The two obsolete live-fetch expectations were replaced with installed-boundary offline assertions without modifying the ratchet baseline. This closes the *source CI* blocker only. This is a draft, unmerged, non-authorizing source candidate. Issue #484 expressly permits non-authorizing source merge without T1 but requires canonical Goal Task ID/COSV registration before governed migrations. Do not conflate CI with Organization ledger readback, T5 authenticated TV/TVC provenance, owner approval, or runtime ALLOW.
