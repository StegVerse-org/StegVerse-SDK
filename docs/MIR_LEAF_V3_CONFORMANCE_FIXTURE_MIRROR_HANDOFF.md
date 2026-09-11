# MIR leaf v3 conformance fixture mirror handoff

Updated: 2026-09-11
Goal Task ID: `MIR-LEAF-V3-CONFORMANCE-FIXTURE-001`
Parent Task ID: `MIR-STEGVERSE-SEPARATION-OF-POWERS-EVIDENCE-CONTRACT-001`
Issue: `StegVerse-org/StegVerse-SDK#213`
PR: `StegVerse-org/StegVerse-SDK#214`
COSV ID: `NOT_YET_ESTABLISHED`
Status: `ACTIVE / FROZEN FIXTURE + STEGVERSE + NEUTRAL REPRODUCTION + COUNTERPART COMPARATOR IMPLEMENTED / MIR REPRODUCTION PENDING`

## Goal

Implement frozen-contract section 12.8: a shared `mir.leaf.v3` fixture whose exact tree and checkpoint can be reproduced independently by MIR, StegVerse, and a neutral third implementation.

Successful three-party reproduction demonstrates proof-format interoperability only. It does not transfer historical custody, governance, transition, credential, witness, or publication authority.

## Contract basis

The frozen v0.3 contract defines:

- leaf: `SHA-256(0x00 || salt || canonicalEventCore)`;
- interior node: `SHA-256(0x01 || leftHashBytes || rightHashBytes)`;
- scheme-bound folding: v3 MUST use the v3 node rule;
- checkpoint tip preimage: UTF-8 `seq:rangeStart:rangeEnd:eventCount:merkleRoot:prevTip` with canonical field formatting;
- unknown schemes fail hard;
- until 12.5/12.6 ship, `witnesses[]` remains empty and proof status remains `NOT_REQUESTED` or `UNAVAILABLE`.

## Fixture design

Canonical fixture:

`fixtures/mir_leaf_v3_conformance_fixture_v1.json`

Frozen expected result:

`fixtures/mir_leaf_v3_conformance_expected_result_v1.json`

The fixture freezes five event inputs. Each event contains exact `salt_base64` and exact `canonical_event_core_base64` bytes. It deliberately does **not** invent or redefine MIR's semantic event serializer; the event-core bytes are already canonical for this conformance vector.

Tree profile: `rfc6962-mth-v1`.

For a tree with more than one leaf, split at the largest power of two strictly less than the leaf count, recursively compute each subtree, then combine with the v3 `0x01` node prefix. The five-leaf fixture therefore exercises a non-power-of-two tree rather than only the trivial balanced case.

Frozen expected outputs:

- Merkle root: `sha256:bd0eb01fccc1d88942f2fb465d27f212afb98f5b0aee47faf370ea0bf21a5a94`
- Checkpoint tip: `sha256:683eac81cfd934700c7ebe8eb4da668f2d44ae95c0cfe74d6d157993324f2ad8`
- checkpoint seq: `42`
- event count: `5`
- previous tip: `null`

## Independent implementations

### StegVerse reproducer

`stegverse/mir_leaf_v3.py`

Implements the frozen v3 leaf function, v3 node function, deterministic MTH tree construction, checkpoint-tip serialization, expected-vector checking, and honest proof/witness-state enforcement.

### Neutral third implementation

`tools/mir_leaf_v3_neutral_reproducer.mjs`

A standalone JavaScript implementation that imports no StegVerse Python implementation code. It independently decodes the same fixture bytes, recomputes leaves/tree/checkpoint, and emits its own result object.

This provides the third-implementation side of the 12.8 seam without pretending to be MIR.

## Counterpart reproduction and exact comparison

MIR/Richard reproduction instructions are now explicit in:

`docs/MIR_LEAF_V3_COUNTERPART_REPRODUCTION_GUIDE.md`

The guide requires MIR to use its own implementation over the exact frozen fixture bytes and return at least the ordered leaf hashes, Merkle root, and checkpoint tip.

StegVerse-side exact comparison is implemented in:

`tools/compare_mir_leaf_v3_result.py`

The comparator fails closed when any required field is missing or differs from the frozen expected result. It also rejects premature `PROVIDED` proof status or non-empty witnesses before 12.5/12.6 are actually shipped.

No MIR result may be synthesized, copied from the expected vector, or inferred from the StegVerse/neutral result.

## Validation

`tests/test_mir_leaf_v3_conformance.py` covers:

- StegVerse exact frozen-vector reproduction;
- neutral JavaScript exact leaf/root/tip match;
- event-byte mutation fail-closed;
- salt mutation fail-closed;
- event-order mutation fail-closed;
- Merkle-root substitution fail-closed;
- checkpoint-tip substitution fail-closed;
- premature witness claim fail-closed;
- false `PROVIDED` proof claim fail-closed.

`tests/test_compare_mir_leaf_v3_result.py` additionally covers exact counterpart match, leaf mismatch, missing checkpoint tip, premature proof claims, and witness claims.

Dedicated workflow:

`.github/workflows/mir-leaf-v3-conformance.yml`

At head `ebd1afa030563b8e65d81f007581fc7b45e11ffe`, after fixing the initially missing SDK dependency install step:

- MIR Leaf v3 Conformance Validation run `34653016906` — PASS;
- SDK Package Artifact Validation run `34653016856` — PASS.

Subsequent counterpart-comparison additions require fresh exact-head validation before merge.

## Completion boundary

Section 12.8 is **not complete** merely because StegVerse and the neutral implementation match. Completion requires an authentic MIR implementation to consume these exact frozen fixture bytes and independently return the same leaf hashes, Merkle root, and checkpoint tip.

The retained counterpart comparison must then report exact agreement.

## Next actions

1. validate the latest exact branch head after counterpart-comparison additions;
2. reconcile README navigation to the fixture/reproduction documentation;
3. establish canonical COSV/task registration without changing proof authority;
4. deliver the frozen fixture and counterpart reproduction guide to MIR/Richard;
5. retain MIR's authentic result and run the exact comparator;
6. declare 12.8 complete only after all three implementations match.
