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
4. Bind SDK result identity/hash into ECE evaluation and Master Records custody/reconstruction evidence.
5. Preserve `NOT_OBSERVED` when authentic observation packets are absent.
6. Observe one authentic resident SDK diagnostic request/result before claiming this lane operational.

## Documentation maintenance

The root README still contains older prose stating governance is the only installed processor. A patch-safe README update remains required; do not replace or truncate the large README merely for bookkeeping.
