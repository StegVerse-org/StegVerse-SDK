# Sovereign Frozen Evaluator Validation — 2026-08-13

```text
validation_lane: PRODUCTION_VALIDATION
routing_surface: CANONICAL_PRODUCTION
execution_host_class: SOVEREIGN_LOCAL
third_party_host_required: false
external_consequence_enabled: false
cases: T0, T1-A, T1-B
result: PASS
```

This validation exercised the canonical manifested route locally without requiring a third-party hosted runtime. Each case traversed the same declared route and retained every route transition in Master Records before advancement.

Canonical route transition sequence for every case:

```text
MANIFEST_ESTABLISHED
SDK_ENTERED
INGESTION_ENTERED
CGE_ADMITTED
CGE_ROUTED
MODULE_ENTERED
MODULE_RESULT
CGE_RETURN_INGESTED
ROUTE_CLEARED
RETURNED
```

## Frozen exact-run results

```text
T0
  input amount: 420 USD
  disposition: ALLOW
  consequence executor invoked: true
  manifest_receipt_id: MR-2F21EC98FB60A78DD0135E580DD80B1FE6CEC9C62B905A4F758E5567F1C666E2
  route_manifest_id: MF-BB568741A3673A16D2ECE826F5C2897BFAF017C837FC842F9E25115A37ED78BF
  route transitions: 10

T1-A
  input amount: 420 USD
  current policy state materially changed
  disposition: DENY
  consequence executor invoked: false
  manifest_receipt_id: MR-620DDEE41541E2F787BC2702FE56977F4BB298BC1CE34C4284203A429F5453C8
  route_manifest_id: MF-07817532629DAB0C3E7C51B5A77EE0919B113C416DD8CB1521180903B34781F4
  route transitions: 10

T1-B
  candidate amount: 4200 USD
  earlier 420 USD approval binding retained
  disposition: DENY
  consequence executor invoked: false
  manifest_receipt_id: MR-804AF43FC68949F0BBC4B89E4729CA1880AB5BFA4655185C171CE5D2332487B4
  route_manifest_id: MF-B61BBE8B51DA7791CA3FAC1B60244CAA88C9A396CEE6FDADC2EE4EF08788A6AB
  route transitions: 10
```

## Assertions

```text
T0 ALLOW: PASS
T1-A DENY: PASS
T1-B DENY: PASS
StegCore receipt chain verified for every run: PASS
Master Records exact-run custody for every run: PASS
10 manifested route transitions for every run: PASS
one transaction identity across each route: PASS
production-validation provenance retained: PASS
third-party host required: FALSE
replay operation custody, four transitions per case: PASS
reconstruction operation custody, four transitions per case: PASS
original consequence reexecuted by replay/reconstruction: FALSE
```

The corresponding portable Master Records custody snapshot is retained in `master-records/orchestration` at:

```text
validation/evaluator-frozen-sovereign-custody-2026-08-13.zlib.b64
```

That snapshot contains 3 exact-run records, 30 manifested-route events, and 24 replay/reconstruction operation events. It is portable transport only and grants no authority.

These receipt identifiers supersede earlier local-ephemeral test identifiers for this frozen evaluator validation. They may be supplied as the ordinary SDK T0/T1-A/T1-B `manifest_receipt_id` values. Interpretation of the three cases remains open to the evaluator.
