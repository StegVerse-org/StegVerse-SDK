# Ecosystem Diagnostic Processor Mirror Handoff

Updated: 2026-09-11

```text
Goal Task ID: SDK-ECOSYSTEM-DIAGNOSTIC-PROCESSOR-001
Parent Goal Task ID: ECOSYSTEM-CONTINUITY-EVALUATOR-001
COSV: 71000000101000
State: SOURCE MERGED+VALIDATED / PERIODIC ECE BRIDGE+AUTHENTIC RUNTIME PENDING
Authority effect: NONE_DIAGNOSTIC_ONLY
GitHub runtime authority: NONE
Credential authority: TV/TVC
```

## Purpose

Install a first-class `ecosystem_diagnostic` processor in the generic SDK manifested-data path. The processor standardizes diagnostic request/result transport and preserves authentic observation states; it does not derive ecosystem continuity, perform repair, mutate providers, acquire credentials, or grant transition authority.

## Merge and validation evidence

PR #219 merged at `50fa9ca306ada6f75fb928281e2bf495ebb08ce8` from exact head `19f573c54c39298e266caa4fe63d7706c9d09d34`.

Exact-head PASS runs:

```text
MCP Source Validation: 34670488331
Manifest Builder Source Validation: 34670488339
Portable Package Source Validation: 34670488380
External Framework Public Submission Validation: 34670488297
Portable Release Index: 34670488334
Connect my LLM Source Validation: 34670488353
Evaluator Contract Console Validation: 34670488636
SDK Production Manifold Governance Validation: 34670488263
Release Dependency Alignment Validation: 34670488338
Evaluator Manifest Source Validation: 34670488333
Communication Edge SDK Demo Validation: 34670488287
SDK Package Artifact Validation: 34670488313
SDK Output-Boundary Proof Validation: 34670488212
```

## Installed source

```text
schemas/stegverse.ecosystem-diagnostic-request.v1.schema.json
schemas/stegverse.ecosystem-diagnostic-result.v1.schema.json
stegverse/ecosystem_diagnostic_runtime.py
stegverse/ecosystem_diagnostic_cli.py
stegverse/route_resolution.py
stegverse/manifest_builder.py
pyproject.toml
tests/test_ecosystem_diagnostic_processor.py
tests/test_manifest_builder.py
```

## Public processor contract

```text
processing.capability = ecosystem_diagnostic
processing.route_id = stegverse.route.ecosystem-diagnostic.v1
runtime binding = stegverse.ecosystem_diagnostic_runtime.execute_manifest
CLI = stegverse-diagnostic --manifest <manifest.json>
request schema = stegverse.ecosystem-diagnostic-request.v1
result schema = stegverse.ecosystem-diagnostic-result.v1
authority effect = NONE_DIAGNOSTIC_ONLY
mutation_permitted = false
continuity_state_present = false
```

`stegverse manifest build --process ecosystem_diagnostic --processor-request diagnostic-request.json ...` constructs the same universal `stegverse.ingress-manifest.v1`; it does not create a diagnostic-specific ingress envelope and does not require governance candidate/request fields.

## Diagnostic semantics

Supported observation vocabulary:

```text
PASS
FAIL
DEGRADED
UNKNOWN
NOT_OBSERVED
STALE
UNREACHABLE
PROBE_REQUIRED
```

Missing observation packets remain `NOT_OBSERVED`. If the request pre-registers evidence expectations and a claimed PASS/FAIL/DEGRADED/STALE/UNREACHABLE observation has no evidence references, the processor emits `PROBE_REQUIRED` instead of accepting an unsupported claim. Backed observation state/evidence is preserved without the SDK calculating continuity.

## Trust boundaries

- payload class != diagnostic capability;
- diagnostic capability != runtime route;
- route/capability selection != authority;
- diagnostic observation != continuity determination;
- diagnostic result != remediation authority;
- repair receipt != recovery proof;
- source/CI/package artifact != authentic runtime execution.

## Current proof boundary

```text
SDK schemas: MERGED / EXACT VALIDATION PASS
SDK installed diagnostic route: MERGED / EXACT VALIDATION PASS
Manifest Builder diagnostic binding: MERGED / EXACT VALIDATION PASS
SDK diagnostic runtime handler source: MERGED / EXACT VALIDATION PASS
stegverse-diagnostic CLI source: MERGED / EXACT VALIDATION PASS
Healer periodic ECE -> SDK diagnostic bridge: NOT IMPLEMENTED
Exact SDK diagnostic-result bytes bound into ECE/Master Records chain: NOT PROVEN
Authentic resident SDK diagnostic request/result: NOT OBSERVED
```

## Exact next sequence

1. Modify the existing Healer periodic ECE cycle to build a canonical `ecosystem_diagnostic` manifest from registered ECE predicates plus the current authentic observation bundle.
2. Execute the manifest through the installed SDK diagnostic processor and retain exact diagnostic-result bytes/hash under the resident ECE cycle.
3. Transform only SDK result observations into ECE observation input; the SDK result must never supply or override ECE continuity state.
4. Bind SDK result identity/hash into ECE evaluation and the organization-ledger transition receipt; Master Records may record the released batch receipt downstream for reconstruction (optional, non-gating).
5. Preserve `NOT_OBSERVED` when authentic observation packets are absent.
6. Observe one authentic resident SDK diagnostic request/result before claiming this lane operational.

## Documentation maintenance

The root README still contains older prose stating governance is the only installed processor. A patch-safe README update remains required; do not replace or truncate the large README merely for bookkeeping.


## 2026-09-25 Experiment 3 existing-owner cross-repository source replay

`SDK-ECOSYSTEM-DIAGNOSTIC-PROCESSOR-001` (COSV `71000000101000`) remains the existing SDK processor owner. Related MIR/SV Experiment 3 (COSV `50000000100000`) reuses that installed read-only processor and the existing StegBrowser/Universal InTr event-ephemeral contract; no parallel processor, runtime, scheduler, authority or device is introduced. Merged SDK PR #325 and #328 already preserve strict source-profile DENY, separately typed local terminal FAIL_CLOSED and nonterminal diagnostic processing ALLOW without claiming terminal Publisher/far-side completion. Older overlapping SDK PR #324 is being reconciled onto current main solely for its unique historical frozen-manifest cross-repository source replay. The existing `mir-sv-exp3-sdk-manifest.yml` source-only workflow now regenerates the original from pinned SDK commit `2508068f5475364ed4b47db6f6349e9b91fdb290`, requires exact archived file SHA-256 `e1b05a082ce19d3d254e3cde1dced03019174a94287724959672c9e65510c8f3`, independently validates original wire digest `ad9b8b8aab2beeea04bff2aac34fd2e7bfa5915133bcaef9209c16de7d9bea68`, and invokes the existing central profile pinned at `f4b234dd1c9e93dc67f0ede2738bbf5b50c54751` for its correctable source-only `ECOSYSTEM_DIAGNOSTIC_NONWORKER_DISPATCH_UNWIRED` result. SDK result validation rejects altered request digest and forged authenticated ingress. These are source-only CI acceptance criteria: do not promote them to actual organization custody or independent Master Records reconstruction. The authentic resident event-ephemeral attempt remains a separately required transition through native owners, and `FAIL_CLOSED` terminates an attempted execution without automatic retry.

## 2026-10-17 governed-DENY negative-conformance fixture (StegVerse-Labs/.github#3183 Workstream A)

Per the StegHealth #51 2026-10-16 directive, the StegHealth-originated deliberate governed-DENY trial (`STEGHEALTH-ECOSYSTEM-FAILURE-REMEDIATION-001` / COSV `10100000100000`; Experiment 3, `MIR-SV-CAPABILITY-BOUNDARY-EXPERIMENT-003` / COSV `50000000100000`) is reused under this owner as an SDK Mesh Destination Map / InTr full-mesh **negative-conformance** diagnostic. It is not a new StegHealth remediation.

- Fixture `tests/fixtures/conformance/governed_deny_experiment3.json` binds the original source and record bytes by repository, commit, path and sha256. It does not contain or claim any resident organization-ledger receipt, because none was appended. The directive also records that no authenticated trial was executed.
- `stegverse/negative_conformance.py` is a pure, non-authorizing classifier. It reuses `organization_ledger_evidence.REFUSAL_FIELDS` for the six refusal fields. It emits an `ecosystem_diagnostic` request for the installed processor.
- `tests/test_governed_deny_negative_conformance.py` covers the following:
  - The SDK-held receipts are byte-bound.
  - The current builder regenerates the frozen original file exactly (sha256 `e1b05a08…`, wire `ad9b8b8a…`).
  - The live `execute_manifest` handoff through the Labs boundary has `awaits_external_machine=false`, `organization_receipt_observed=false` and returns via `admit_runtime_result`.
  - The governance disposition `FAIL_CLOSED` with experiment outcome `NOT_FAILED` classifies as `NEGATIVE_CONFORMANCE_PASS_CORRECT_REFUSAL`.
  - The installed processor keeps the organization receipt, InTr admission and Master Records effects `NOT_OBSERVED`.
  - The classifier rejects a variant that is missing any of the six fields.
  - It rejects a variant that marks the experiment `FAILED` with the refusal as its only basis.
  - It rejects a variant that awaits an external machine or gates on destination liveness.
  - It rejects an unobserved effect that lacks `NOT_AUTHENTICALLY_OBSERVED` and a `reconciliation_entrypoint`.
- The 2026-09-30 `FROZEN_EXP3_ORIGINAL_MANIFEST_ROOT_DRIFT` FAIL_CLOSED is carried verbatim as `HISTORICAL_SUPERSEDED`, because the current builder now reproduces the frozen bytes. The Labs canonical record has not been reconciled to reflect this.

Source-only. This fixture adds no authentic InTr verdict, organization receipt, Master Records record, retry or authority.
