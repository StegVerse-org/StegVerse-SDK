# MIR destination profile propagation mirror handoff

Goal Task ID: `MIR-ROUNDTRIP-EGRESS-AUTHENTICITY-001`
COSV ID: `50000000100000`

## Purpose

Preserve the manifest-declared Interlock/InTr destination profile through SDK completion, Publisher-return binding, and the existing LLM Adapter `RTC-STEGVERSE-EGRESS-007` handoff without creating another transport/runtime plane.

Required invariant:

```text
completion.egress.destination_profile
-> stegverse.sdk.publisher-return-binding/v1.egress.destination_profile
-> stegverse.llm-adapter.southbound-intr-egress-handoff/v1.destination_profile
```

The destination profile is routing/transport intent only. It grants no governance, credential, execution, admission, or completion authority.

## Source change

The SDK manifest contract now permits a non-empty optional `completion.egress.destination_profile`. The Manifest Builder exposes it as `destination_profile` / `--destination-profile`. The existing `assemble_publisher_return()` path already copies the manifest egress declaration into `stegverse.sdk.publisher-return-binding/v1`; therefore no second SDK return seam is introduced.

For the owned MIR mirror exercise the declared destination profile is the canonical external-counterpart profile ID `MIR` from `StegVerse-Labs/StegOS/config/external_counterpart_profiles/mir.json`.

## Validation requirement

Source validation must prove:

- `destination_profile=MIR` survives manifest validation unchanged;
- the SDK Publisher-return binding retains the exact `MIR` value unchanged;
- empty destination-profile substitution fails closed;
- no downstream transport/runtime predicate is promoted by source construction.

Runtime evidence remains pending until exact-head source validation passes and the existing governed InTr path is exercised against the owned MIR mirror.
