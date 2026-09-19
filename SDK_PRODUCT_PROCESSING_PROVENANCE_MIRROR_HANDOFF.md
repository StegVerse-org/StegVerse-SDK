# SDK Product Processing Provenance Mirror Handoff

Goal Task ID: `SDK-PRODUCT-PROCESSING-PROVENANCE-001`
Parent Goal Task ID: `SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003`
Adjacent runtime coordination: `SDK-EVALUATOR-GOVERNANCE-POSTURE-RUNTIME-PROOF-001`
Repository: `StegVerse-org/StegVerse-SDK`
Branch: `feat/sdk-product-processing-provenance-001`
Status: `SOURCE_IMPLEMENTATION_IN_PROGRESS`

## Objective

Define one generic, non-authorizing SDK result provenance envelope that attributes only the exact portion of a submission/result processed by each genuine StegVerse product boundary. AdmittedCode is the first required typed projection. LLM-adapter, SDK, Core-Lite, StegCore, Interlock/InTr, StegAgents/runtime, Master Records, and future product boundaries must use the same contribution semantics rather than parallel result schemas.

## Canonical rules

```text
product attribution follows actual processing evidence, not branding or routing
a product may not claim another product's processing
input/output bindings are hash- or receipt-bound where available
authority effect is explicit per product contribution
admission is not execution
custody is not execution authority
SDK composition is not governance authority
missing/unobserved product processing is explicit rather than silently omitted
caller-supplied upstream product provenance is labeled as declared unless independently verified
no duplicate evaluator, runtime, dispatcher, custody store, or authority plane
```

## Current ownership

```text
SDK -> result composition / product-processing projection
AdmittedCode -> named admission/evidence product projection
StegCore/StegGate -> canonical governance implementation
Core-Lite -> manifested route carrier where actually traversed
Interlock/InTr -> governed transition authority; must remain NOT_OBSERVED unless authentic evidence is present
StegAgents/runtime -> bounded execution product; must remain NOT_OBSERVED unless authentic worker/runtime evidence is present
Master Records -> custody/reconstruction product evidence
LLM-adapter -> upstream product contribution only from bound source/product provenance; SDK does not infer adapter internals
TV/TVC -> credential authority; not replaced by this envelope
```

## Implementation target

- add reusable `stegverse.product_processing` composition;
- attach `product_processing` to canonical governed SDK results;
- expose `admittedcode_processing` as a typed projection of the AdmittedCode contribution;
- preserve the existing canonical runtime `result_binding_hash` and add a separate SDK-return binding over the enriched result;
- cover LLM-adapter-origin manifests through the existing ingress-manifest identity without claiming unverified adapter internals;
- apply the same envelope to the currently installed non-governance `ecosystem_diagnostic` processor, explicitly marking AdmittedCode `NOT_PROCESSED` on a route that does not traverse it;
- add regression tests for attribution, non-attribution, authority separation, and deterministic binding;
- update README and repository handoff.

## Authority effect

`NONE`. This task changes observable result provenance only.
