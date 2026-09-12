# Ecosystem Diagnostic Processor Mirror Handoff

Updated: 2026-09-11

```text
Goal Task ID: SDK-ECOSYSTEM-DIAGNOSTIC-PROCESSOR-001
Parent Goal Task ID: ECOSYSTEM-CONTINUITY-EVALUATOR-001
COSV: 71000000101000
Branch: feature/ecosystem-diagnostic-processor-001
State: SOURCE IMPLEMENTED / VALIDATION PENDING
Authority effect: NONE_DIAGNOSTIC_ONLY
GitHub runtime authority: NONE
Credential authority: TV/TVC
```

## Purpose

Install a first-class `ecosystem_diagnostic` processor in the generic SDK manifested-data path. The processor standardizes diagnostic request/result transport and preserves authentic observation states; it does not derive ecosystem continuity, perform repair, mutate providers, acquire credentials, or grant transition authority.

## Installed source on this branch

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
authority effect = NONE_DIAGNOSTIC_ONLY
mutation_permitted = false
```

`stegverse manifest build --process ecosystem_diagnostic --processor-request diagnostic-request.json ...` constructs the same universal `stegverse.ingress-manifest.v1`; it does not create a diagnostic-specific ingress envelope.

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

Missing observation packets remain `NOT_OBSERVED`. If the request pre-registers evidence expectations and a claimed PASS/FAIL/DEGRADED/STALE/UNREACHABLE observation has no evidence references, the processor emits `PROBE_REQUIRED` instead of accepting an unsupported claim.

The result explicitly sets:

```text
mutation_performed = false
authority_effect = NONE_DIAGNOSTIC_ONLY
continuity_state_present = false
```

ECE remains responsible for dependency-aware continuity interpretation across retained diagnostic results over time.

## Trust boundaries

- payload class != diagnostic capability;
- diagnostic capability != runtime route;
- route/capability selection != authority;
- diagnostic observation != continuity determination;
- diagnostic result != remediation authority;
- repair receipt != recovery proof;
- source/CI != authentic runtime execution.

## Validation predicates

- governance manifest construction remains backward-compatible;
- installed processor registry exposes governance + ecosystem_diagnostic;
- diagnostic manifests do not require governance candidate/request fields;
- route resolution binds exactly to the diagnostic runtime;
- missing observation -> NOT_OBSERVED;
- pre-registered evidence without evidence refs -> PROBE_REQUIRED;
- authentic backed observation state/evidence is preserved without reinterpretation;
- v1 mutation request is rejected;
- diagnostic result contains no continuity state.

## Remaining work after source validation

1. Merge SDK source only after exact-head SDK validation passes.
2. Update canonical Task/COSV evidence with merge and validation refs.
3. Modify the Healer periodic ECE cycle to build/execute the SDK diagnostic manifest first and transform its diagnostic-result artifact into ECE observation input.
4. Preserve exact diagnostic-result bytes/evidence identity into the ECE/Master Records chain.
5. Observe one authentic resident SDK diagnostic request/result before claiming the SDK diagnostic lane operational.

Source merge alone does not establish item 5.
