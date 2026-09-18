# SDK Product Processing Provenance

Every governed SDK result exposes product-scoped provenance without collapsing product or authority boundaries.

## Result contract

`product_processing` uses schema `stegverse.sdk.product-processing.v1`. Each contribution records:

- product identity and role;
- processing status;
- the exact processing scope attributed to that product;
- input and output bindings;
- evidence references;
- authority effect;
- provenance basis;
- a deterministic contribution hash.

`admittedcode_processing` is a typed projection of the AdmittedCode contribution using schema `stegverse.sdk.product-processing.admittedcode.v1`.

## Attribution rules

A product is marked `PROCESSED` only from evidence already present in the canonical SDK/runtime result. An upstream product named by a submitted manifest is `DECLARED_UPSTREAM_PROVENANCE` unless the SDK independently has evidence of its internal processing. Expected downstream products such as Interlock/InTr or StegAgents/runtime are `NOT_OBSERVED` when authentic evidence is absent.

The current canonical governed SDK route therefore distinguishes:

```text
StegVerse-SDK -> manifestation / route binding / result composition
Core-Lite -> manifested route carriage
AdmittedCode -> governance/admission decision and reasons
StegCore -> canonical transaction/governance implementation
Interlock/InTr -> transition authority (not inferred from route traversal)
StegAgents/runtime -> bounded worker execution (not inferred from a generic consequence)
Master Records -> custody/reconstruction evidence
LLM-adapter or another source product -> declared upstream provenance when carried by the ingress manifest
```

## Binding

The existing canonical runtime `result_binding_hash` remains the hash of the underlying runtime result before product-provenance projection. The enriched SDK return adds `sdk_return_binding_hash`, covering the result plus `product_processing` and `admittedcode_processing`.

This envelope grants no execution, credential, transition, publication, or custody authority and creates no parallel evaluator.

### Non-governance processor behavior

The same envelope is applied to the currently installed `ecosystem_diagnostic` processor. Its own processing contribution is `PROCESSED`; AdmittedCode is explicitly `NOT_PROCESSED` with provenance basis `ROUTE_DID_NOT_TRAVERSE_ADMITTEDCODE`; Interlock/InTr, StegAgents/runtime, and Master Records remain `NOT_OBSERVED` unless their own authentic evidence exists. This demonstrates that product attribution follows the selected processor route rather than assuming every SDK submission traverses governance.
