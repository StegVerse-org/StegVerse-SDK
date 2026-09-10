"""Two-layer task security posture semantics.

The ecosystem computes a non-downgradable automatic posture floor from organization,
data class, and channel requirements. A caller may separately select a posture at or
above that floor. The effective posture is the stronger of automatic and selected.
"""
from __future__ import annotations

from typing import Any

from .security_posture import (
    DATA_CLASS_MINIMUM_TIER,
    CHANNEL_MINIMUM_TIER,
    TIER_TO_POSTURE,
    SecurityPostureError,
    _tier_rank,
    resolve_security_posture,
)


def select_posture_stack(
    *,
    organization_minimum_tier: str = "SECURE",
    data_class: str | None = None,
    channel: str | None = None,
    selected_tier: str | None = None,
) -> dict[str, Any]:
    """Return automatic, selected, and effective posture identities separately."""
    automatic_candidates = [organization_minimum_tier]
    if data_class in DATA_CLASS_MINIMUM_TIER:
        automatic_candidates.append(DATA_CLASS_MINIMUM_TIER[data_class])
    if channel in CHANNEL_MINIMUM_TIER:
        automatic_candidates.append(CHANNEL_MINIMUM_TIER[channel])

    automatic_tier = max(automatic_candidates, key=_tier_rank)
    automatic = resolve_security_posture(TIER_TO_POSTURE[automatic_tier])

    chosen_tier = selected_tier or automatic_tier
    if _tier_rank(chosen_tier) < _tier_rank(automatic_tier):
        raise SecurityPostureError("selected_security_posture_below_automatic_floor")
    selected = resolve_security_posture(TIER_TO_POSTURE[chosen_tier])

    effective_tier = max([automatic_tier, chosen_tier], key=_tier_rank)
    effective = resolve_security_posture(TIER_TO_POSTURE[effective_tier])

    selectable_tiers = [tier for tier in TIER_TO_POSTURE if _tier_rank(tier) >= _tier_rank(automatic_tier)]
    return {
        "schema": "stegverse.sdk.security-posture-stack.v1",
        "automatic_posture": {
            "tier": automatic_tier,
            "posture_id": automatic["posture_id"],
            "posture_sha256": automatic["posture_sha256"],
            "basis": {
                "organization_minimum_tier": organization_minimum_tier,
                "data_class_minimum_tier": DATA_CLASS_MINIMUM_TIER.get(data_class),
                "channel_minimum_tier": CHANNEL_MINIMUM_TIER.get(channel),
            },
        },
        "selected_posture": {
            "tier": chosen_tier,
            "posture_id": selected["posture_id"],
            "posture_sha256": selected["posture_sha256"],
            "selection_present": selected_tier is not None,
        },
        "effective_posture": {
            "tier": effective_tier,
            "posture_id": effective["posture_id"],
            "posture_sha256": effective["posture_sha256"],
        },
        "selectable_tiers": selectable_tiers,
        "downgrade_below_automatic_floor_allowed": False,
        "authority_effect": "NONE_ADMISSION_EVIDENCE_ONLY",
    }
