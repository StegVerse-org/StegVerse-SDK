"""Credential-free executable entry for SDK governance option 000.

Option 0B is deliberately not accepted here (SDK#368). The former module 0B
entry ran the local sovereign lane (``governance_ingress_runtime.run_external_manifest``)
without readiness qualification and printed its result unlabelled, so it did
not converge on the canonical manifest entrypoint the primary console uses.
An explicit ``0B`` invocation is refused with a pointer to that console.
"""
from __future__ import annotations

import argparse
import json
import sys

from .governance_ingress_runtime import run_000_demo

CANONICAL_0B_ENTRY = "stegverse governance --select 0B --manifest <stegverse.ingress-manifest.v1.json>"
REMOVED_0B_LANE = "stegverse.governance_ingress_runtime.run_external_manifest"


def _first_positional(argv: list[str]) -> str | None:
    """Return the option operand without parsing, so 0B is refused before any file is read."""
    expects_value = False
    for token in argv:
        if expects_value:
            expects_value = False
            continue
        if token.startswith("-"):
            expects_value = token.startswith("--") and "=" not in token
            continue
        return token
    return None


def _refuse_0b() -> dict[str, object]:
    from .cli import CANONICAL_MANIFEST_ENTRYPOINT

    return {
        "status": "REFUSED",
        "failed_predicate": "NON_CONVERGENT_0B_MODULE_ENTRY",
        "error": (
            "option 0B is not accepted by python -m stegverse.governance_ingress_cli: that entry bound "
            f"the local lane {REMOVED_0B_LANE} without readiness qualification and did not converge on "
            "the canonical manifest entrypoint; submit the manifest through the primary console"
        ),
        "canonical_entry": CANONICAL_0B_ENTRY,
        "canonical_entrypoint": CANONICAL_MANIFEST_ENTRYPOINT,
        "authority_effect": "NONE",
    }


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if (_first_positional(argv) or "").upper() == "0B":
        print(json.dumps(_refuse_0b(), indent=2, sort_keys=True))
        return 2
    parser = argparse.ArgumentParser(
        prog="python -m stegverse.governance_ingress_cli",
        description=(
            "Execute SDK governance option 000 through the canonical sovereign runtime. "
            f"Option 0B is served only by: {CANONICAL_0B_ENTRY}"
        ),
    )
    parser.add_argument("option", choices=("000",))
    parser.add_argument("target", nargs="?", help=argparse.SUPPRESS)
    parser.add_argument("--records-db", "--custody-db", dest="custody_db", default=None)
    parser.add_argument("--host-identity", default="stegverse-sovereign-local")
    args = parser.parse_args(argv)
    try:
        if args.target:
            raise ValueError("option 000 does not accept an external target")
        result = run_000_demo(custody_db=args.custody_db, host_identity=args.host_identity)
    except ValueError as exc:
        print(json.dumps({"status": "INVALID_REQUEST", "error": str(exc), "authority_effect": "NONE"}, indent=2, sort_keys=True))
        return 2
    print(json.dumps(dict(result), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
