"""Governance tightness profiles for ingestion-controlled work."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, Mapping, Union

TIGHTNESS_SCHEMA = "stegverse.governance.tightness_profile.v1"


@dataclass(frozen=True)
class TightnessProfile:
    schema: str
    label: str
    scale: int
    allow_threshold: int
    review_threshold: int
    fail_closed_threshold: int
    require_receipt: bool
    require_replay: bool
    require_human_review: bool
    allow_cross_repo_write: bool
    allow_cross_org_write: bool
    default_route: str


def _clamp_scale(value: int) -> int:
    return max(0, min(100, int(value)))


def label_for_scale(scale: int) -> str:
    scale = _clamp_scale(scale)
    if scale <= 20:
        return "observe"
    if scale <= 40:
        return "assist"
    if scale <= 60:
        return "balanced"
    if scale <= 80:
        return "strict"
    return "fail_closed"


def scale_for_label(label: str) -> int:
    normalized = str(label).strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "open": "observe",
        "low": "observe",
        "observe": "observe",
        "advisory": "observe",
        "assist": "assist",
        "review_light": "assist",
        "medium": "balanced",
        "balanced": "balanced",
        "default": "balanced",
        "strict": "strict",
        "high": "strict",
        "fail": "fail_closed",
        "fail_closed": "fail_closed",
        "max": "fail_closed",
    }
    mapped = aliases.get(normalized)
    if mapped is None:
        raise ValueError(f"unknown governance tightness label: {label}")
    return {
        "observe": 10,
        "assist": 35,
        "balanced": 55,
        "strict": 75,
        "fail_closed": 95,
    }[mapped]


def resolve_tightness(value: Union[int, str, Mapping[str, Any], None] = None) -> TightnessProfile:
    """Resolve a numeric, named, or mapping tightness input into a profile."""
    if value is None:
        scale = 55
    elif isinstance(value, Mapping):
        if "scale" in value:
            scale = _clamp_scale(int(value["scale"]))
        elif "label" in value:
            scale = scale_for_label(str(value["label"]))
        else:
            scale = 55
    elif isinstance(value, str):
        scale = scale_for_label(value)
    else:
        scale = _clamp_scale(int(value))

    label = label_for_scale(scale)
    require_receipt = scale >= 35
    require_replay = scale >= 55
    require_human_review = scale >= 70
    allow_cross_repo_write = scale <= 70
    allow_cross_org_write = scale <= 50

    if scale >= 85:
        route = "fail_closed"
    elif scale >= 70:
        route = "human_review_required"
    elif scale >= 55:
        route = "receipt_and_replay_required"
    elif scale >= 35:
        route = "receipt_required"
    else:
        route = "observe_only"

    return TightnessProfile(
        schema=TIGHTNESS_SCHEMA,
        label=label,
        scale=scale,
        allow_threshold=max(0, 70 - scale // 4),
        review_threshold=max(0, 45 - scale // 5),
        fail_closed_threshold=max(0, 90 - scale // 3),
        require_receipt=require_receipt,
        require_replay=require_replay,
        require_human_review=require_human_review,
        allow_cross_repo_write=allow_cross_repo_write,
        allow_cross_org_write=allow_cross_org_write,
        default_route=route,
    )


def tightness_to_dict(profile: TightnessProfile) -> Dict[str, Any]:
    return asdict(profile)


def resolve_tightness_dict(value: Union[int, str, Mapping[str, Any], None] = None) -> Dict[str, Any]:
    return tightness_to_dict(resolve_tightness(value))


def apply_tightness_to_ingestion_packet(packet: Mapping[str, Any], tightness: Union[int, str, Mapping[str, Any], None] = None) -> Dict[str, Any]:
    """Attach a governance tightness profile to an ingestion packet copy."""
    output = dict(packet)
    output["governance_tightness"] = resolve_tightness_dict(tightness)
    return output
