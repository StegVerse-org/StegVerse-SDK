# SDK Production Manifold Governance Demo Mirror Handoff

## Source of truth

```text
organization: StegVerse-org
repository: StegVerse-SDK
branch: main
goal_id: SDK-PRODUCTION-MANIFOLD-GOVERNANCE-DEMO-001
parent_handoff: SDK_MIRROR_HANDOFF.md
production_governance_owner: StegVerse-Labs/StegCore
production_governance_handoff: StegVerse-Labs/StegCore/MANIFOLD_GOVERNANCE_MIRROR_HANDOFF.md
production_runtime: stegcore.manifold_governance.govern_manifold_action
credential_authority: TV/TVC
github_token_runtime_authority: NONE
sdk_role: DEMO_TEST_CLIENT
parallel_evaluator_permitted: false
```

## Goal

Expose the canonical StegCore governed-manifold production capability through the SDK for evaluator demo/test use without reimplementing manifold governance in the SDK.

The SDK may construct/validate a portable test packet, map it into canonical StegCore request objects, call the production `govern_manifold_action(...)` runtime, and return the canonical action/projection. The SDK must not reinterpret canonical dispositions or create a demo-specific evaluator.

## Production capability relationship

Canonical production source merged in StegCore:

```text
StegVerse-Labs/StegCore
PR: #157
merge: 99397392462b8e39a510ec6d9e543551270bd402
runtime: src/stegcore/manifold_governance.py
entry: govern_manifold_action(...)
```

Core invariants consumed by this SDK lane:

```text
human-in-the-loop timing != governance authority
wall-clock time != governance authority
heartbeat cadence != governance authority
observation != authorization
linear transition path required: false

independent ALLOW branches may continue toward the separately governed commit boundary
while unrelated REVIEW branches remain reviewable
and dependent branches remain held.

protected boundary crossing requires separately applicable authority.
```

## SDK implementation target

```text
stegverse/manifold_governance.py
stegverse/demo_data/manifold_governance_reviewable.json
stegverse/sdk_surfaces.py
stegverse/cli.py
tests/test_manifold_governance_sdk.py
```

Evaluator commands:

```bash
stegverse demo manifold-governance
stegverse run manifold-governance --input <packet.json>
```

The bundled demo must exercise a multi-branch population in which independent ALLOW paths remain eligible to continue while a protected REVIEW branch and its dependent successor remain reviewable/held.

## Authority boundary

The SDK is a client of production governance only.

```text
SDK grants authority: false
SDK defines manifold disposition: false
SDK performs external consequence: false
SDK mints Master Records custody: false
SDK can override protected boundary: false
StegCore canonical evaluator unchanged: true
```

Actual consequence execution remains behind the existing StegCore governed commit/execution boundary and normal Master Records custody requirements.

## Validation requirements

Required deterministic checks:

1. SDK bridge imports and calls `stegcore.manifold_governance.govern_manifold_action`.
2. No SDK-local fallback evaluator exists.
3. Bundled demo produces a reviewable manifold with independent continued paths and a held dependent path.
4. DENY and FAIL_CLOSED remain preserved.
5. Output identifies StegCore as production runtime authority.
6. Output states wall clock and HB cadence are not governance authority.
7. Arbitrary evaluator packets can be supplied through `stegverse run manifold-governance --input ...`.
8. Missing canonical StegCore capability fails closed with an explicit dependency error.
9. No GitHub or non-TV/TVC runtime credential is introduced.

## Completion rule

This goal is complete only after source implementation, focused tests, hosted validation, merge to SDK `main`, and canonical handoff reconciliation. A demo-specific duplicate evaluator is a failure condition.
