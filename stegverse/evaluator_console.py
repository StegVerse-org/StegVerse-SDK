"""Top-level console wrapper adding evaluator-contract discovery.

All existing commands delegate unchanged to ``stegverse.cli``. The ``contract``
command is intercepted here so an installed SDK can expose the evaluator request
contract without requiring repository browsing.
"""
from __future__ import annotations

import sys

from . import cli
from . import evaluator_contract


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if args and args[0] in {"contract", "evaluator-contract"}:
        return evaluator_contract.main(args[1:])
    result = cli.main(args)
    if not args:
        print("Evaluator contract: stegverse contract")
        print("Contract schema:   stegverse contract --schema")
        print("Worked example:    stegverse contract --example")
    return result


if __name__ == "__main__":
    raise SystemExit(main())
