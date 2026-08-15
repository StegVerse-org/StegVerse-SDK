# SDK Governance Sovereign Fallback Mirror Handoff

## Authority

```text
goal_id: SDK-GOVERNANCE-SOVEREIGN-FALLBACK-003
originating_goal: make StegGate/AdmittedCode SDK testing capable immediately and retain the canonical sovereign/local path as permanent degraded-mode fallback
repository: StegVerse-org/StegVerse-SDK
branch: main
parent_handoff: SDK_MIRROR_HANDOFF.md
canonical_navigation_handoff: docs/MANIFEST_RECEIPT_NAVIGATION_MIRROR_HANDOFF.md
canonical_issue: #16
credential_authority: TV/TVC
github_token_runtime_authority: NONE
non-TV/TVC secret_or_token_required: false
```

This scoped handoff is subordinate to the root SDK handoff and issue #16. It creates no second evaluator, custody store, receipt-ID algorithm, credential path, or governance authority.

## Incident finding and correction

The canonical sovereign runtime and the SDK governed-operation adapter used incompatible result-field aliases:

```text
sovereign submit: route_receipt_chain_head
adapter previously required: receipt_chain_head

sovereign replay: manifest_receipt_id
adapter previously required: original_manifest_receipt_id
```

A genuine canonical StegGate result could therefore be rejected after governance succeeded. `stegverse/governed_operations.py` now accepts the canonical sovereign vocabulary and historical/provider-neutral aliases without rewriting the returned result.

## Installed source

```text
stegverse/governance_fallback.py
stegverse/governed_operations.py
stegverse/cli.py
tests/test_governance_fallback.py
tests/test_governance_fallback_cli.py
tests/test_governed_operations.py
tests/test_governance_public_execution.py
claims/SDK-GOVERNANCE-SOVEREIGN-FALLBACK-003.json
claims/SDK-PUBLIC-GOVERNANCE-EXECUTION-005.json
tasks/SDK-SOVEREIGN-RELEASE-ACTIVATION-004.json
docs/SESSION_GOAL_INVENTORY_2026-08-15_SDK_FALLBACK_TRADE_READY_LOCAL_MODEL.md
```

Key commits:

```text
390989aa590211c91331986bc51a80eaf670f1df   permanent sovereign fallback module
870bae62ebd19adcfd0979a867cb78c56ad785ed   fallback tests
ccb57309d74649590761263c2d596770a19100a9   canonical sovereign result aliases
bea7c814c15fa196e6e1ad10648de5e0084397a9   adapter tests
e8ced0362f1b1ecb3ca968a8b0e4e1fd8063d5ca  public degraded-mode CLI selector
0556129a3b0bb3406fbae2499d431d6a9c3d6d44  fallback CLI tests
50d228fdccdc8cec79c4161b9f5c3aa391d059d3  fallback implementation claim released
e194a336024d2f712765fd9a00349811790c5f0b  sovereign release activation task registered
d9158ff591120f1dfc8ba647b540764ccf64bd8c  public governance execution integration claim
39ec03c360ae126bf22437f05d4a32f9b4ec69f2  ordinary option 0A/1/2 execution wiring
cca135a31bf5db02377e6914c517b9b7d031f1ce  public execution tests
```

## Ordinary public execution now installed

The announced governance CLI is no longer guidance-only for the already-canonical executable shapes:

```bash
stegverse governance --select 0 --input <public-inspection-request.json>
stegverse governance --select 1 --manifest-receipt-id <MR-...>
stegverse governance --select 2 --manifest-receipt-id <MR-...>
```

Semantics:

```text
option 0A -> existing public-inspection request -> GovernedOperations -> sovereign_validation_runtime -> Core-Lite -> StegCore/StegGate -> Master Records
option 1  -> manifest_receipt_id -> canonical sovereign replay
option 2  -> manifest_receipt_id -> canonical sovereign reconstruction
```

Option `0B` is intentionally still fail-closed. No conversion from `stegverse.ingress-manifest.v1` to the public-inspection execution request is invented by this incident work. Installing that canonical binding remains separate issue #16 work.

## Permanent degraded-mode fallback

```bash
stegverse governance --fallback-operation run --fallback-target <public-inspection-request.json>
stegverse governance --fallback-operation replay --fallback-target <manifest_receipt_id>
stegverse governance --fallback-operation reconstruct --fallback-target <manifest_receipt_id>
```

The fallback delegates to the same `stegverse.sovereign_validation_runtime` and returns the canonical result unchanged. A genuine `ALLOW`, `DENY`, `REVIEW`, or `FAIL_CLOSED` is never converted into fallback status.

Pre-governance fallback failures remain distinct:

```text
INVALID_REQUEST
RUNTIME_COMPONENT_UNAVAILABLE
GOVERNANCE_RUNTIME_ERROR
FALLBACK_FAILED
```

## Credential / authority boundary

```text
GitHub token accepted as runtime authority: false
GitHub token required: false
non-TV/TVC secret/token accepted: false
provider secret accepted: false
wallet credential accepted: false
credential authority: TV/TVC
GitHub Actions release authority: NONE
authority effect of navigation/fallback selector: NONE
```

## Validation evidence

No new GitHub Actions run was manually triggered during the billing incident.

Direct deterministic evidence retained from this session:

```text
fallback focused unit validation: 4/4 PASS
canonical sovereign adapter shaped-result validation: 3/3 PASS
fallback python syntax validation: PASS
```

The newer public-execution tests are committed. GitHub Actions query for head `cca135a31bf5db02377e6914c517b9b7d031f1ce` returned zero runs, so hosted execution of those tests is NOT claimed. Exact external evaluator execution/custody evidence also remains unobserved in this session.

## Release/package activation boundary

Repository/package state observed during this session:

```text
pyproject version: 1.0.13
latest tag observed: v1.0.13
latest published GitHub release observed: v1.0.12
incident correction commits: newer than v1.0.13 tag
```

`.github/workflows/headless-release.yml` is validation-only and explicitly grants GitHub Actions no version-bump, tag, push, release, PyPI, or credential authority. Actual release execution is TV/TVC-owned sovereign/local work.

The previously unowned activation gap is now durable at:

```text
tasks/SDK-SOVEREIGN-RELEASE-ACTIVATION-004.json
state: MACHINE_OWNED
owner: TV/TVC-authorized sovereign SDK release lane
```

Completion requires an observable TV/TVC-authorized release/package whose source contains the incident correction and whose distributed package contents verify the corrected fallback/adapter/CLI surfaces. Source-on-main is not represented as user distribution activation.

## Convergence / collision prevention

```text
PR #28 / SDK-USAGE-GOVERNED-OPERATION-WIRING-002: existing canonical GovernedOperations adapter; extended, not replaced
claims/SDK-AUTHORITY-BOUNDARY-SOVEREIGN-RUN-002.json: exact sovereign execution/custody machine-owned; not duplicated
issue #16: canonical navigation/execution continuation
SDK-SOVEREIGN-RELEASE-ACTIVATION-004: release/package activation machine-owned by TV/TVC-authorized lane
```

## Remaining work

```text
000 -> bind the SDK demo dataset to an actual canonical manifested run
0B  -> install canonical stegverse.ingress-manifest.v1 execution binding
0A/1/2 focused source tests -> obtain strongest non-cost-amplifying execution evidence when a local/machine lane is available
release/package -> TV/TVC-authorized sovereign release lane publishes and verifies corrected package
exact sovereign run/custody -> existing machine-owned SDK execution lane
```

Automatic fallback selection is not permitted to override a canonical governance result. If later primary transports are added, they may select fallback only before canonical governance exists.

## Automation / continuation

```text
canonical UX owner: StegVerse-org/StegVerse-SDK#16
release activation owner: tasks/SDK-SOVEREIGN-RELEASE-ACTIVATION-004.json
exact run/custody owner: claims/SDK-AUTHORITY-BOUNDARY-SOVEREIGN-RUN-002.json
fallback trigger: primary execution unavailable before canonical governance result
fallback output: unchanged canonical run/replay/reconstruct result
persistent state: canonical Master Records custody selected by sovereign runtime
fail closed: yes
```

## Completion accounting

Incident/fallback developed surfaces are complete; full public governance activation is not:

```text
incident/fallback required developed files: 7
implemented: 7/7
scaffolding/stubs: 0
missing incident files: 0
validated incident gates: 2/3 (new public-execution tests not yet executed)
integration gates: 4/4 source-installed (adapter aliases, fallback CLI, ordinary 0A, replay/reconstruct)
public navigation remaining: 000 and 0B
published corrected package: false
external corrected-path execution proof: false
```

## Session consolidation

Transferred requirements:

```text
permanent fallback: DURABLE HERE + #16
ordinary 0A/1/2 canonical execution: DURABLE HERE + #16
no non-TV/TVC secrets/tokens: DURABLE HERE
never reinterpret governance disposition: DURABLE HERE
separate runtime/infrastructure failure from governance result: DURABLE HERE
release/package activation: DURABLE MACHINE TASK SDK-SOVEREIGN-RELEASE-ACTIVATION-004
trade-ready/local-model goals: DURABLE IN SESSION INVENTORY + canonical owner handoffs
```

This handoff does not claim full SDK product activation or release activation.
