from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence


REQUIRED_VERIFICATIONS = (
    "manufacturer_identity",
    "orderable_suffix",
    "package_dimensions",
    "electrical_rating",
    "availability_checked",
    "cost_checked",
)


@dataclass(frozen=True)
class ProcurementGateResult:
    ready_to_freeze: bool
    blockers: tuple[str, ...]


def evaluate_procurement_candidate_bom(packet: Mapping[str, object]) -> ProcurementGateResult:
    """Fail-closed gate for converting an engineering candidate BOM into a frozen BOM.

    This gate is informational only. Passing it does not purchase parts, authorize spend,
    establish physical compatibility, or create runtime/governance authority.
    """

    blockers: list[str] = []
    if packet.get("schema") != "stegverse.mhia.procurement_candidate_bom.v0":
        blockers.append("invalid_schema")

    if packet.get("freeze_state") not in {"NOT_FROZEN", "FROZEN"}:
        blockers.append("invalid_freeze_state")

    items = packet.get("items")
    if not isinstance(items, Sequence) or isinstance(items, (str, bytes)) or not items:
        blockers.append("missing_items")
        return ProcurementGateResult(False, tuple(blockers))

    roles: set[str] = set()
    for index, raw_item in enumerate(items):
        if not isinstance(raw_item, Mapping):
            blockers.append(f"item[{index}].invalid")
            continue
        role = raw_item.get("role")
        if not isinstance(role, str) or not role:
            blockers.append(f"item[{index}].role_missing")
            role = f"index_{index}"
        elif role in roles:
            blockers.append(f"{role}.duplicate_role")
        else:
            roles.add(role)

        for field in ("manufacturer", "family", "orderable_candidate", "package"):
            value = raw_item.get(field)
            if not isinstance(value, str) or not value.strip():
                blockers.append(f"{role}.{field}_unresolved")

        verification = raw_item.get("verification")
        if not isinstance(verification, Mapping):
            blockers.append(f"{role}.verification_missing")
            continue
        for check in REQUIRED_VERIFICATIONS:
            if verification.get(check) is not True:
                blockers.append(f"{role}.{check}_not_verified")

    ready = not blockers
    if packet.get("freeze_state") == "FROZEN" and not ready:
        blockers.append("frozen_state_without_complete_evidence")
        ready = False

    return ProcurementGateResult(ready, tuple(sorted(set(blockers))))


def assert_procurement_freeze_ready(packet: Mapping[str, object]) -> None:
    result = evaluate_procurement_candidate_bom(packet)
    if not result.ready_to_freeze:
        raise ValueError("MHIA procurement freeze blocked: " + ", ".join(result.blockers))
