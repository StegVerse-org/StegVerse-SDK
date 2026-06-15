"""Example LLM dynamic admissibility bridge usage.

This example converts LLM text into a dynamic tester packet, evaluates what
that text is allowed to become, includes a local admissibility receipt
reference, and exports a Governed Admissibility Bundle.
"""

from __future__ import annotations

import json

from stegverse.admissibility_bundle import build_bundle_from_bridge_result, verify_admissibility_bundle
from stegverse.llm_admissibility import (
    evaluate_llm_output_admissibility,
    summarize_llm_admissibility,
)


def main() -> None:
    bridge = evaluate_llm_output_admissibility(
        provider="openai",
        model="gpt-test",
        prompt="Draft a governance note about commit-time admissibility.",
        output="Commit-time admissibility asks what an output is allowed to become.",
        declared_intent="research_note",
        include_receipt_reference=True,
    )
    summary = summarize_llm_admissibility(bridge)
    bundle = build_bundle_from_bridge_result(bridge)

    print("# llm admissibility bridge result")
    print(json.dumps(bridge, indent=2, sort_keys=True))
    print("\n# compact summary")
    print(json.dumps(summary, indent=2, sort_keys=True))
    print("\n# governed admissibility bundle")
    print(json.dumps({"bundle_valid": verify_admissibility_bundle(bundle), "bundle": bundle}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
