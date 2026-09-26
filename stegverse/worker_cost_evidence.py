"""Qualify cost evidence without promoting SDK demos to measured runtime economics.

A source-only qualifier: never substitutes estimated or fixture values for
original provider, sandbox, resident, Actions, governance or custody evidence.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

COMPONENTS = (
    "provider", "sandbox", "resident_node", "github_actions",
    "governance", "custody",
)
SCHEMA = "stegverse.worker-cost-evidence.v1"


def qualify_worker_cost(packet: Mapping[str, Any]) -> dict[str, Any]:
    """Return an explicit, non-authorizing qualification of one workflow."""
    if not isinstance(packet, Mapping) or packet.get("schema") != SCHEMA:
        raise ValueError("unsupported worker cost evidence schema")
    workflow_id = packet.get("workflow_id")
    if not isinstance(workflow_id, str) or not workflow_id.strip():
        raise ValueError("nonempty workflow_id required")
    components = packet.get("components")
    if not isinstance(components, Mapping):
        raise ValueError("components object required")
    if set(components) != set(COMPONENTS):
        raise ValueError("exactly six cost components required")
    findings = {}
    total = 0
    complete = True
    for name in COMPONENTS:
        row = components[name]
        if not isinstance(row, Mapping):
            raise ValueError(f"{name}: component must be object")
        amount = row.get("amount_minor_units")
        currency = row.get("currency")
        evidence = row.get("original_evidence_sha256")
        measured = row.get("classification") == "MEASURED"
        valid_amount = type(amount) is int and amount >= 0
        valid_currency = isinstance(currency, str) and len(currency) == 3 and currency.isalpha() and currency.isupper()
        valid_evidence = isinstance(evidence, str) and len(evidence) == 64 and all(c in "0123456789abcdef" for c in evidence)
        accepted = measured and valid_amount and valid_currency and valid_evidence
        findings[name] = {
            "qualified": accepted,
            "reason": "SOURCE_DECLARED_MEASUREMENT_UNVERIFIED" if accepted else "MISSING_OR_UNQUALIFIED_EVIDENCE",
            "amount_minor_units": amount if valid_amount else None,
            "currency": currency if valid_currency else None,
            "original_evidence_sha256": evidence if valid_evidence else None,
        }
        complete &= accepted
        if accepted:
            total += amount
    currencies = {v["currency"] for v in findings.values() if v["qualified"]}
    if len(currencies) != 1:
        complete = False
    result = {
        "schema": "stegverse.worker-cost-qualification.v1",
        "workflow_id": workflow_id,
        "component_findings": findings,
        "source_declarations_complete": complete,
        "independently_verified": False,
        "runtime_evidence_verified": False,
        "benchmark_promotion_authorized": False,
        "measured_total_minor_units": None,
        "authority_effect": "NONE",
        "next_action": "INDEPENDENT_ORIGINAL_EVIDENCE_RETRIEVAL" if complete else "REMEDIATE_MISSING_COMPONENT_EVIDENCE",
    }
    result["qualification_sha256"] = hashlib.sha256(
        json.dumps(result, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return result
