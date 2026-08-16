"""Top-level console wrapper adding evaluator contract and release discovery."""
from __future__ import annotations

import sys

from . import cli
from . import evaluator_contract
from . import production_release_set
from . import test_procedure


def _install_versioned_governance_wrapper() -> None:
    """Route canonical CLI imports through release-set-aware wrappers."""
    from . import sovereign_validation_runtime as canonical
    from . import versioned_sovereign_runtime as versioned
    canonical.run_sovereign_validation = versioned.run_sovereign_validation
    canonical.replay_sovereign = versioned.replay_sovereign
    canonical.reconstruct_sovereign = versioned.reconstruct_sovereign


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if args and args[0] in {"contract", "evaluator-contract"}:
        return evaluator_contract.main(args[1:])
    if args and args[0] in {"production-releases", "release-set"}:
        return production_release_set.main(args[1:])
    if args and args[0] in {"test-procedure", "procedure"}:
        return test_procedure.main(args[1:])
    if args and args[0] == "governance":
        _install_versioned_governance_wrapper()
    result = cli.main(args)
    if not args:
        print("Evaluator contract:    stegverse contract")
        print("Test procedure:        stegverse test-procedure")
        print("Contract schema:       stegverse contract --schema")
        print("Worked example:        stegverse contract --example")
        print("Current releases:      stegverse production-releases catalog")
        print("Installed release set: stegverse production-releases installed")
    return result


if __name__ == "__main__":
    raise SystemExit(main())
