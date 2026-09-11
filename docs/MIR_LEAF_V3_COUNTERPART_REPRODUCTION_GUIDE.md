# MIR leaf v3 counterpart reproduction guide

Goal Task ID: `MIR-LEAF-V3-CONFORMANCE-FIXTURE-001`
Contract basis: MIR × StegVerse Separation-of-Powers Evidence Contract v0.3 §12.8

## Purpose

This package gives MIR the exact frozen bytes needed for the third independent reproduction required by section 12.8. MIR should compute the result with its own implementation and return the resulting leaf hashes, Merkle root, and checkpoint tip. MIR should not import or invoke the StegVerse Python or neutral JavaScript implementations.

## Frozen inputs

Use exactly:

`fixtures/mir_leaf_v3_conformance_fixture_v1.json`

The fixture contains five ordered entries. For each entry, decode `salt_base64` and `canonical_event_core_base64` to raw bytes.

The fixture intentionally freezes already-canonical event-core bytes. It does not ask MIR to reinterpret or regenerate event semantics for this vector.

## Required computation

For every event:

```text
leafHash = SHA-256(0x00 || saltBytes || canonicalEventCoreBytes)
```

Construct the tree using `rfc6962-mth-v1`:

- a single-leaf tree returns that leaf hash;
- for N > 1, split the ordered leaf list at the largest power of two strictly less than N;
- recursively hash each side;
- combine subtrees as:

```text
nodeHash = SHA-256(0x01 || leftHashBytes || rightHashBytes)
```

For the checkpoint, serialize exactly:

```text
seq:rangeStart:rangeEnd:eventCount:merkleRoot:prevTip
```

as UTF-8 with the field values already frozen in the fixture and `null` as the literal text for a null previous tip, then compute SHA-256 over those bytes.

## MIR return shape

Return a JSON object containing at least:

```json
{
  "fixture_id": "MIR-LEAF-V3-CONFORMANCE-FIXTURE-001-F1",
  "leaf_scheme": "mir.leaf.v3",
  "tree_profile": "rfc6962-mth-v1",
  "leaf_hashes": ["sha256:..."],
  "merkle_root": "sha256:...",
  "checkpoint_tip": "sha256:..."
}
```

MIR may include implementation/runtime metadata in additional fields. Those fields are retained as provenance but are not used to manufacture a match.

Until 12.5/12.6 are actually shipped, any included `proof_status` must remain `NOT_REQUESTED` or `UNAVAILABLE`, and any included `witnesses` value must remain an empty array.

## Frozen expected vector

The comparison target is retained separately at:

`fixtures/mir_leaf_v3_conformance_expected_result_v1.json`

MIR should preferably compute first and compare after computation rather than coding the expected root/tip into its implementation.

## Comparison

After receiving MIR's result JSON, StegVerse can compare it with:

```bash
python tools/compare_mir_leaf_v3_result.py mir-result.json
```

Exit code `0` means every required frozen field matches exactly. Exit code `1` means one or more required fields are missing or mismatched.

## Completion rule

Section 12.8 is complete only when:

1. StegVerse independently reproduces the vector;
2. the neutral third implementation independently reproduces the vector;
3. MIR independently reproduces the same vector; and
4. the retained comparison shows exact agreement on ordered leaf hashes, Merkle root, and checkpoint tip.

A mismatch is conformance evidence to investigate. It is not a governance verdict and must not be converted into one.
