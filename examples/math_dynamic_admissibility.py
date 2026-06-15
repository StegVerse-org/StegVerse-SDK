"""Example math-solver dynamic admissibility bridge usage.

This example converts a formalism artifact summary into a dynamic tester
packet, evaluates what that artifact is allowed to become, includes a local
admissibility receipt reference, and exports a Governed Admissibility Bundle.
"""

from __future__ import annotations

import json

from stegverse.admissibility_bundle import build_bundle_from_bridge_result, verify_admissibility_bundle
from stegverse.math_admissibility import (
    evaluate_math_artifact_admissibility,
    summarize_math_admissibility,
)


def main() -> None:
    bridge = evaluate_math_artifact_admissibility(
        formalism_id="RTG-STCM",
        artifact_type="solver_artifact",
        artifact_summary="Placeholder derivation attempt for RTG/STCM observer-window relationship.",
        declared_intent="formalism_support_claim",
        include_receipt_reference=True,
    )
    summary = summarize_math_admissibility(bridge)
    bundle = build_bundle_from_bridge_result(bridge)

    print("# math admissibility bridge result")
    print(json.dumps(bridge, indent=2, sort_keys=True))
    print("\n# compact summary")
    print(json.dumps(summary, indent=2, sort_keys=True))
    print("\n# governed admissibility bundle")
    print(json.dumps({"bundle_valid": verify_admissibility_bundle(bundle), "bundle": bundle}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
