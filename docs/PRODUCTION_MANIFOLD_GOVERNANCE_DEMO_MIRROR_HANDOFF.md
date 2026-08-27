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

## Installed source state

```text
stegverse/manifold_governance.py: IMPLEMENTED
stegverse/demo_data/manifold_governance_reviewable.json: IMPLEMENTED
stegverse/sdk_surfaces.py registration: IMPLEMENTED
stegverse/cli.py demo/run bindings: IMPLEMENTED
tests/test_manifold_governance_sdk.py: IMPLEMENTED
.github/workflows/manifold-governance-sdk.yml: IMPLEMENTED
pyproject.toml manifold-test exact StegCore pin: IMPLEMENTED
source_state: IMPLEMENTED_VALIDATED_MERGED
release_state: NOT_RELEASED
```

The existing `governed-test` frozen dependency set is intentionally unchanged. A separate `manifold-test` optional extra pins the exact StegCore production merge `99397392462b8e39a510ec6d9e543551270bd402` so this new evaluator capability does not rewrite older frozen evaluation coordinates.

## Merge state

```text
SDK PR: #89
SDK merge: 9bfb318b409624868160b32a831d327f9ef3ecf9
source merge: COMPLETE
production StegCore validation: PASS / run 33118864638
SDK delegation-boundary validation: PASS / run 33119113357
```

## Production validation binding — current

The production capability itself is no longer validation-pending.

```text
StegCore production implementation PR: #157
StegCore production implementation merge: 99397392462b8e39a510ec6d9e543551270bd402
StegCore validation reconciliation PR: #158
StegCore hosted validation run: 33118864638
StegCore hosted validation result: SUCCESS
```

The SDK validation lane deliberately does not copy or reimplement private StegCore source. Its hosted test proves the SDK is a thin client of the canonical runtime contract and that absence of StegCore fails rather than selecting an SDK fallback. The real-runtime behavior is proven by the owning StegCore validation above.

An end-to-end evaluator execution of the SDK command requires an installed canonical StegCore build containing `govern_manifold_action`. The repository already records the exact internal test coordinate through the `manifold-test` optional dependency. Distribution/release of that StegCore build remains governed by StegCore/TV/TVC release authority and is not fabricated by this SDK lane.

## SDK validation and merge evidence

```text
SDK source integration PR: #89
SDK source integration merge: 9bfb318b409624868160b32a831d327f9ef3ecf9
SDK validation reconciliation PR: #90
SDK validated head: 31d9c84f710f1497b90b277cbf20dacbd85ca4c3
SDK validation workflow run: 33119113357
SDK validation result: SUCCESS
SDK validation merge: 1825b37a08956ce23aee48b352271a0bc2e31c5a
production StegCore runtime merge: 99397392462b8e39a510ec6d9e543551270bd402
production StegCore validation run: 33118864638 SUCCESS
source + delegation boundary: COMPLETE
demo/test source capability: COMPLETE
end-to-end evaluator execution predicate: installed canonical StegCore build containing govern_manifold_action
release/distribution authority: StegCore / TV/TVC
```

The SDK capability is complete as a production-governance client. It intentionally does not embed a second manifold evaluator. External distribution of the newly extended StegCore build is a separately governed release concern and must not be conflated with SDK source completeness.
