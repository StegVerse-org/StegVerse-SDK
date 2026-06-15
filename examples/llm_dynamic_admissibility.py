"""Example LLM dynamic admissibility bridge usage.

This example converts LLM text into a dynamic tester packet, evaluates what
that text is allowed to become, and includes a local admissibility receipt
reference that can be attached later to review or execution records.
"""

from __future__ import annotations

import json

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

    print("# llm admissibility bridge result")
    print(json.dumps(bridge, indent=2, sort_keys=True))
    print("\n# compact summary")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
