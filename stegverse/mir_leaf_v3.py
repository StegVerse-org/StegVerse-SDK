from __future__ import annotations

import base64
import hashlib
from typing import Any, Mapping, Sequence

LEAF_SCHEME = "mir.leaf.v3"
TREE_PROFILE = "rfc6962-mth-v1"
CHECKPOINT_PROFILE = "mir.checkpoint-tip.v0.3"


class MirLeafV3Error(ValueError):
    pass


def _sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def leaf_hash(*, salt: bytes, canonical_event_core: bytes) -> bytes:
    return _sha256(b"\x00" + salt + canonical_event_core)


def node_hash(left_hash: bytes, right_hash: bytes) -> bytes:
    if len(left_hash) != 32 or len(right_hash) != 32:
        raise MirLeafV3Error("node inputs must be 32-byte SHA-256 digests")
    return _sha256(b"\x01" + left_hash + right_hash)


def _largest_power_of_two_less_than(n: int) -> int:
    if n < 2:
        raise MirLeafV3Error("tree split requires at least two leaves")
    return 1 << ((n - 1).bit_length() - 1)


def merkle_tree_hash(leaf_hashes: Sequence[bytes]) -> bytes:
    count = len(leaf_hashes)
    if count == 0:
        return _sha256(b"")
    if count == 1:
        if len(leaf_hashes[0]) != 32:
            raise MirLeafV3Error("leaf hash must be 32 bytes")
        return leaf_hashes[0]
    split = _largest_power_of_two_less_than(count)
    return node_hash(
        merkle_tree_hash(leaf_hashes[:split]),
        merkle_tree_hash(leaf_hashes[split:]),
    )


def checkpoint_tip_preimage(checkpoint: Mapping[str, Any], merkle_root: str) -> bytes:
    seq = checkpoint.get("seq")
    event_count = checkpoint.get("eventCount")
    range_start = checkpoint.get("rangeStart")
    range_end = checkpoint.get("rangeEnd")
    prev_tip = checkpoint.get("prevTip")
    if not isinstance(seq, int) or seq < 0:
        raise MirLeafV3Error("checkpoint seq must be an unsigned integer")
    if not isinstance(event_count, int) or event_count < 0:
        raise MirLeafV3Error("checkpoint eventCount must be an unsigned integer")
    if not isinstance(range_start, str) or not range_start:
        raise MirLeafV3Error("checkpoint rangeStart required")
    if not isinstance(range_end, str) or not range_end:
        raise MirLeafV3Error("checkpoint rangeEnd required")
    if not isinstance(merkle_root, str) or not merkle_root.startswith("sha256:"):
        raise MirLeafV3Error("checkpoint merkleRoot invalid")
    prev_text = "null" if prev_tip is None else str(prev_tip)
    preimage = f"{seq}:{range_start}:{range_end}:{event_count}:{merkle_root}:{prev_text}"
    return preimage.encode("utf-8")


def reproduce_fixture(fixture: Mapping[str, Any]) -> dict[str, Any]:
    if fixture.get("leaf_scheme") != LEAF_SCHEME:
        raise MirLeafV3Error("unsupported leaf scheme")
    if fixture.get("tree_profile") != TREE_PROFILE:
        raise MirLeafV3Error("unsupported tree profile")
    if fixture.get("checkpoint_profile") != CHECKPOINT_PROFILE:
        raise MirLeafV3Error("unsupported checkpoint profile")

    events = fixture.get("events")
    if not isinstance(events, list) or not events:
        raise MirLeafV3Error("fixture events required")

    leaf_bytes: list[bytes] = []
    leaf_text: list[str] = []
    for expected_index, event in enumerate(events):
        if not isinstance(event, Mapping) or event.get("event_index") != expected_index:
            raise MirLeafV3Error("event indexes must be contiguous and ordered")
        try:
            salt = base64.b64decode(str(event["salt_base64"]), validate=True)
            core = base64.b64decode(str(event["canonical_event_core_base64"]), validate=True)
        except Exception as exc:
            raise MirLeafV3Error("fixture base64 invalid") from exc
        digest = leaf_hash(salt=salt, canonical_event_core=core)
        digest_text = "sha256:" + digest.hex()
        if digest_text != event.get("expected_leaf_hash"):
            raise MirLeafV3Error(f"leaf mismatch at event {expected_index}")
        leaf_bytes.append(digest)
        leaf_text.append(digest_text)

    checkpoint = fixture.get("checkpoint")
    if not isinstance(checkpoint, Mapping):
        raise MirLeafV3Error("checkpoint required")
    if checkpoint.get("eventCount") != len(events):
        raise MirLeafV3Error("checkpoint eventCount mismatch")

    root = "sha256:" + merkle_tree_hash(leaf_bytes).hex()
    if root != checkpoint.get("expected_merkle_root"):
        raise MirLeafV3Error("merkle root mismatch")

    tip = "sha256:" + _sha256(checkpoint_tip_preimage(checkpoint, root)).hex()
    if tip != checkpoint.get("expected_tip"):
        raise MirLeafV3Error("checkpoint tip mismatch")

    if fixture.get("witnesses") != []:
        raise MirLeafV3Error("witnesses must remain empty until witness surface is shipped")
    if fixture.get("proof_status") not in {"NOT_REQUESTED", "UNAVAILABLE"}:
        raise MirLeafV3Error("proof_status must remain honest before proof surface shipment")

    return {
        "schema": "stegverse.mir-leaf-v3-conformance-result/v1",
        "fixture_id": fixture.get("fixture_id"),
        "leaf_scheme": LEAF_SCHEME,
        "tree_profile": TREE_PROFILE,
        "leaf_hashes": leaf_text,
        "merkle_root": root,
        "checkpoint_tip": tip,
        "proof_status": fixture.get("proof_status"),
        "witnesses": [],
        "authority_effect": "NONE_CONFORMANCE_EVIDENCE_ONLY",
    }


__all__ = [
    "LEAF_SCHEME",
    "TREE_PROFILE",
    "CHECKPOINT_PROFILE",
    "MirLeafV3Error",
    "leaf_hash",
    "node_hash",
    "merkle_tree_hash",
    "checkpoint_tip_preimage",
    "reproduce_fixture",
]
