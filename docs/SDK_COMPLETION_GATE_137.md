# SDK Completion Gate #137

This document tracks the final SDK-only completion work for external-framework testing.

## Scope

The SDK is complete for this gate when an external framework can:

1. preserve its source-native payload semantics;
2. construct a `stegverse.ingress-manifest.v1` without hand-authoring the envelope;
3. pre-register evaluator expectations and requested evidence;
4. select the installed governance processor/route;
5. select caller-facing return depth;
6. submit through the canonical local governance runtime;
7. receive a `manifest_receipt_id` plus the requested artifact projection;
8. replay and reconstruct the retained transaction;
9. fail closed on unsupported/incomplete/conflicting route or processor requests.

## Non-blocking downstream work

The public `https://stegverse.org/` submission UI is downstream Site work and is not a prerequisite for SDK package completion. The SDK itself must remain usable locally and programmatically without Site.

## Release readiness

A release/tag is warranted only after exact-head validation demonstrates the full path above and the canonical mirror handoff records that evidence.
