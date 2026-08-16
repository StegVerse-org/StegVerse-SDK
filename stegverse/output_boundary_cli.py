"""CLI for credentialless StegVerse S/NS provider-output proof."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

from .output_boundary_proof import evaluate_output_boundary_proof


def _load(path: str) -> Mapping[str, Any]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"unable to read candidate: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"candidate is not valid JSON: {exc}") from exc
    if not isinstance(value, Mapping):
        raise ValueError("candidate must be a JSON object")
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="stegverse-output-proof",
        description="Govern and prove an externally generated provider output without giving StegVerse the provider API key.",
    )
    parser.add_argument("--input", required=True, help="candidate JSON file")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = evaluate_output_boundary_proof(_load(args.input))
    except ValueError as exc:
        print(json.dumps({"status": "FAIL_CLOSED", "error": str(exc)}, indent=2, sort_keys=True))
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    proof = result["proof"]
    return 0 if proof["replay_match"] and proof["semantic_reconstruction_match"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
