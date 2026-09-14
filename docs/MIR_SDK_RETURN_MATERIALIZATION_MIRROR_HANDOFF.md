# MIR SDK return materialization mirror handoff

Updated: 2026-09-14
Goal Task ID: `MIR-ROUNDTRIP-EGRESS-AUTHENTICITY-001`
Parent Goal Task ID: `MIR-CONNECTION-ROUNDTRIP-TECHNICAL-GUIDE-001`
COSV ID: `50000000100000`
Canonical registry issue: `StegVerse-Labs/.github#1891`
Canonical Site handoff: `StegVerse-Labs/Site/docs/MIR_ROUNDTRIP_EGRESS_AUTHENTICITY_MIRROR_HANDOFF.md`
SDK issue: `StegVerse-org/StegVerse-SDK#244`
Predecessor return-continuity merge: `StegVerse-org/StegVerse-SDK@b4927ed277c4993662f9e7e4ffd717f677ad5459`
Status: `ACTIVE / CHECKED_OUT / EXACT SDK RETURN MATERIALIZATION REPAIR`

## Purpose

Repair only the missing materialization/export/retention seam between the existing canonical SDK `assemble_publisher_return()` implementation and the existing LLM Adapter `RTC-STEGVERSE-EGRESS-007` consumer.

The canonical current Site handoff has already classified the first missing predicate: no eligible predecessor-produced exact `stegverse.sdk.publisher-return-binding/v1` artifact is observable in the inspected repository/carrier surfaces. Current SDK code exposes the assembler but has no non-test caller that retains its exact canonical output for downstream consumption.

## Required input

The repair may consume only caller-supplied exact inputs from the same authorized execution chain:

- original admitted manifest JSON;
- original `stegverse.sdk.downstream-completion-capsule/v1` JSON when the Publisher return carries MIR round-trip continuity;
- exact canonical `stegverse.publisher.artifact-return/v1` bytes;
- the authentic `manifest_receipt_id` associated with the original manifest.

It must call the existing `assemble_publisher_return()` implementation. It must not reconstruct equivalent Publisher bytes, infer a completion capsule, invent a receipt ID, or synthesize MIR provenance.

## Required output

- exact canonical bytes of `stegverse.sdk.publisher-return-binding/v1`;
- `communication_state = READY_FOR_FINAL_STEGVERSE_EGRESS_TRANSITION`;
- `sdk_return_binding_observed = true` for the SDK assembly artifact represented by those bytes;
- deterministic binding SHA-256 already carried by the canonical binding;
- a non-authorizing materialization receipt containing only output path, exact byte SHA-256, schema/state, and authority/completion observations.

The retained output must be suitable for direct exact-byte input to the existing LLM Adapter `RTC-STEGVERSE-EGRESS-007` consumer.

## Authority boundary

This repair does not invoke Publisher, LLM Adapter, Interlock/InTr, far-side transition, MIR, release, deployment, or communication completion. GitHub Actions remains validation/evidence transport only. `authority_effect = NONE` throughout.

## Validation boundary

Source/CI may prove deterministic exact-byte materialization and fail-closed behavior. It does not prove that authentic predecessor runtime inputs were supplied or that an eligible live SDK return artifact exists after merge.

## Next bounded steps

1. Add an SDK-owned exact materialization function/CLI that calls the canonical assembler and writes only canonical output bytes.
2. Add fail-closed tests for exact output retention, MIR capsule requirement, and refusal to overwrite an existing artifact unless explicitly requested.
3. Document the local materialization surface in `README.md` without promoting it to runtime evidence.
4. Validate an exact PR head and merge only if green.
5. Reconcile this handoff and the canonical Site handoff; keep runtime consumption and all downstream transition predicates false until authentic same-execution evidence exists.
