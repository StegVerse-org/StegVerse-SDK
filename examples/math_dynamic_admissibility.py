"""Example math-solver dynamic admissibility bridge usage.

This example converts a formalism artifact summary into a dynamic tester
packet and evaluates what that artifact is allowed to become.
"""

from __future__ import annotations

import json

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
    )
    summary = summarize_math_admissibility(bridge)

    print("# math admissibility bridge result")
    print(json.dumps(bridge, indent=2, sort_keys=True))
    print("\n# compact summary")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
