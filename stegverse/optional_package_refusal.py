"""Six-field refusal when an undeclared optional owner package is not installed.

stegos and stegbrowser are owner packages the SDK cannot declare: neither has a public,
pinnable source the SDK can name in pyproject.toml. The SDK therefore imports each lazily
inside one function, and every caller may inject the callable instead. When neither is
present the call fails closed with the six fields, never a bare ImportError and never a wait
for the package to appear. tests/test_dependency_inventory_guard.py holds the list below
equal to the imports that actually occur (SDK#484 V-P4).
"""
from __future__ import annotations

import json
from typing import Any

OWNING_GOAL = "SDK-STRUCTURAL-VALIDATOR-CONSOLIDATION-001"

# package -> the one module the SDK imports from it, and the call site that imports it.
UNDECLARED_OPTIONAL_PACKAGES = {
    "stegos": ("stegos.intr_security_posture_resolution", "stegverse/evaluator_governance_runtime.py"),
    "stegbrowser": ("stegbrowser.llm_browser_execution", "stegverse/governed_llm_fan.py"),
}


def optional_package_unavailable(failure_code: str, module: str, repair: str, retry_entrypoint: str) -> dict[str, Any]:
    """FAIL_CLOSED record for an owner package that is neither installed nor injected."""
    return {
        "disposition": "FAIL_CLOSED",
        "failure_code": failure_code,
        "failed_predicate": f"OPTIONAL_OWNER_MODULE_PRESENT_OR_INJECTED:{module}",
        "required_evidence_or_repair": repair,
        "retry_entrypoint": retry_entrypoint,
        "owning_existing_goal": OWNING_GOAL,
        "next_attempt": "rerun the same manifest after the owner package is installed or the callable is injected",
        "authority_effect": "NONE",
    }


def render(record: dict[str, Any]) -> str:
    return json.dumps(record, sort_keys=True)


__all__ = ["OWNING_GOAL", "UNDECLARED_OPTIONAL_PACKAGES", "optional_package_unavailable", "render"]
