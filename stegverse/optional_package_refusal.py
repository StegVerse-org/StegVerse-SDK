"""Six-field refusal when an undeclared optional owner package is not installed.

Declared contract: injection-only (SDK#484 V-P4 b; Lane B B-P13; Coordinator decision).
stegos and stegbrowser are private owner repositories, StegBrowser is not pip-installable, and
pinning either would add cryptography and playwright transitively, which the no-new-dependency
directive forbids. So neither is declared in pyproject.toml. The SDK imports each lazily inside
one function, and every caller may inject the callable instead. A call with neither fails
closed with the six fields, never a bare ImportError and never a wait for the package to
appear. tests/test_dependency_inventory_guard.py holds the list below equal to the imports
that actually occur.

The upstream heads below are observation points, not pins: they record which owner source the
injected callables were last read against, and nothing installs or checks out from them.
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

INJECTION_ONLY_CONTRACT = True
# package -> upstream head observed 2026-10-19 (Lane B B-P13, SDK#484 6256984316); not a pin.
UPSTREAM_OBSERVATION_POINTS = {
    "stegos": "StegVerse-Labs/StegOS@e63f7e8",
    "stegbrowser": "StegVerse-Labs/StegBrowser@ac29091",
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


__all__ = ["INJECTION_ONLY_CONTRACT", "OWNING_GOAL", "UNDECLARED_OPTIONAL_PACKAGES", "UPSTREAM_OBSERVATION_POINTS",
           "optional_package_unavailable", "render"]
