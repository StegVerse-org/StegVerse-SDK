# SDK Governance Sovereign Fallback Mirror Handoff

## Authority

```text
goal_id: SDK-GOVERNANCE-SOVEREIGN-FALLBACK-003
originating_goal: make StegGate/AdmittedCode SDK testing capable immediately and retain the canonical sovereign/local path as the permanent degraded-mode fallback
repository: StegVerse-org/StegVerse-SDK
branch: main
parent_handoff: SDK_MIRROR_HANDOFF.md
canonical_navigation_handoff: docs/MANIFEST_RECEIPT_NAVIGATION_MIRROR_HANDOFF.md
canonical_issue: #16
credential_authority: TV/TVC
github_token_runtime_authority: NONE
non-TV/TVC secret_or_token_required: false
```

This handoff is subordinate to the root SDK handoff and issue #16. It does not create a second evaluator, custody store, receipt-ID algorithm, route authority, credential path, or governance authority.

## Incident finding

The canonical sovereign runtime and the SDK governed-operation observation adapter used different result-field aliases:

```text
sovereign submit: route_receipt_chain_head
adapter previously required: receipt_chain_head

sovereign replay: manifest_receipt_id
adapter previously required: original_manifest_receipt_id
```

That mismatch allowed a real canonical StegGate run to be rejected by the SDK integration layer after governance had already produced a result. The adapter now accepts both canonical sovereign names and historical/provider-neutral aliases without modifying the returned result.

## Installed source

```text
stegverse/governance_fallback.py
stegverse/governed_operations.py
tests/test_governance_fallback.py
tests/test_governed_operations.py
claims/SDK-GOVERNANCE-SOVEREIGN-FALLBACK-003.json
```

Commits:

```text
7b372ee2a5fb9a6adca1ae4a612a92a55a78742c  claim established
390989aa590211c91331986bc51a80eaf670f1df   permanent canonical sovereign fallback module
870bae62ebd19adcfd0979a867cb78c56ad785ed   focused fallback tests
ccb57309d74649590761263c2d596770a19100a9   accept canonical sovereign result aliases
bea7c814c15fa196e6e1ad10648de5e0084397a9   canonical sovereign adapter tests
```

## Permanent fallback contract

Direct degraded-mode entry:

```bash
python -m stegverse.governance_fallback run <public-inspection-request.json>
python -m stegverse.governance_fallback replay <manifest_receipt_id>
python -m stegverse.governance_fallback reconstruct <manifest_receipt_id>
```

The fallback delegates to `stegverse.sovereign_validation_runtime` and prints the canonical result unchanged. Fallback-selection metadata is emitted separately to stderr. Therefore fallback use cannot convert, wrap, reinterpret, or replace a genuine StegGate `ALLOW`, `DENY`, `REVIEW`, or `FAIL_CLOSED` disposition.

Failure states before a canonical governance result exists are separated as:

```text
INVALID_REQUEST
RUNTIME_COMPONENT_UNAVAILABLE
GOVERNANCE_RUNTIME_ERROR
FALLBACK_FAILED
```

None is a governance disposition.

## Credential / authority boundary

```text
GitHub token accepted as runtime authority: false
GitHub token required: false
non-TV/TVC secret/token accepted: false
provider secret accepted: false
wallet credential accepted: false
credential authority: TV/TVC
authority effect of fallback selector: NONE
```

## Validation evidence

No new GitHub Actions run was manually triggered for this incident work.

Local deterministic validation performed without network or GitHub credentials:

```text
fallback focused unit validation: 4/4 PASS
canonical sovereign adapter shaped-result validation: 3/3 PASS
python syntax validation: PASS
```

GitHub Actions query for head `870bae62ebd19adcfd0979a867cb78c56ad785ed` returned zero workflow runs. Hosted validation therefore remains unclaimed; absence of a run is not represented as PASS.

## Convergence / collision prevention

Existing merged work:

```text
PR #28 -> stegverse/governed_operations.py
SDK-USAGE-GOVERNED-OPERATION-WIRING-002 -> COMPLETE_VALIDATED_MERGED
```

This incident fix extends that canonical adapter; it does not replace it.

Existing machine-owned exact sovereign execution/custody evidence lane:

```text
claims/SDK-AUTHORITY-BOUNDARY-SOVEREIGN-RUN-002.json
```

This session must not compete with that lane. The fallback source can be invoked by a user or authorized machine, but exact activation/custody evidence owned by the canonical machine lane remains separate.

## Remaining work

Canonical navigation issue #16 still owns the broader public UX contract:

```text
000 -> runtime-bound demo processing
0   -> complete public submit UX wiring
1   -> replay UX
2   -> reconstruct UX
```

The fallback is now installed as a permanent degraded-mode capability. The remaining navigation work must use the same canonical handlers and may automatically select this fallback only before a canonical governance result exists. It must never override a genuine governance disposition.

## Automation / continuation

```text
owner: StegVerse-org/StegVerse-SDK#16
trigger: primary SDK execution path unavailable or fails before canonical governance result
fallback: stegverse.governance_fallback -> stegverse.sovereign_validation_runtime
persistent state: canonical Master Records custody DB selected by sovereign runtime
outputs: unchanged canonical run/replay/reconstruct result
fail closed: yes
next executable task: bind the public option 0/1/2 UX to GovernedOperations handlers and select the sovereign fallback only for pre-governance transport/runtime failure
```

## Completion accounting

For `SDK-GOVERNANCE-SOVEREIGN-FALLBACK-003`:

```text
required developed files: 4
implemented: 4/4
scaffolding/stubs: 0
missing files: 0
focused validation gates: 2
validated: 2/2 locally deterministic
hosted workflow validation: NOT RUN / not required for source activation
integration gates: 3
1 adapter accepts canonical sovereign submit vocabulary: PASS
2 adapter accepts canonical sovereign replay/reconstruct locator vocabulary: PASS
3 public primary navigation automatically selects fallback on pre-governance failure: PENDING #16
goal activation: 2/3
```

## Session consolidation

Transferred requirements:

```text
permanent fallback after incident: DURABLE HERE + #16
same canonical governance/custody path: DURABLE HERE
no non-TV/TVC secrets/tokens: DURABLE HERE
never reinterpret governance disposition: DURABLE HERE
separate infrastructure/runtime failure from governance result: DURABLE HERE
```

Archive dependency for this incident slice: the source/fallback requirement is durably transferred and implemented. The overall session is not archive-ready while it retains distinct support obligations across the canonical SDK navigation workstream or other goals not yet consolidated.
