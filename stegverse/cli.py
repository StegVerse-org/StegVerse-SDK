"""Generic command-line entry point for the StegVerse SDK.

The console is intentionally user-neutral. It exposes discoverable, locally
callable SDK surfaces and preserves the SDK's non-authorizing boundary.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

from .sdk_surfaces import canonical_surface_name, get_sdk_surface, list_sdk_surfaces


def _load_json(path: str, label: str) -> Mapping[str, Any]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"unable to read {label}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"{label} is not valid JSON: {exc}") from exc
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must contain a JSON object")
    return value


def list_surfaces(_registry: dict[str, Any] | None = None) -> list[tuple[str, str]]:
    """Compatibility helper returning canonical user-facing surfaces."""
    return [(row["id"], row["summary"]) for row in list_sdk_surfaces()]


def print_help_for_surface(name: str, _registry: dict[str, Any] | None = None) -> int:
    surface = get_sdk_surface(name)
    if surface is None:
        print(f"Unknown surface: {name}")
        print("Run 'stegverse surfaces' to discover available SDK surfaces.")
        return 2
    print(surface["id"])
    print(f"  {surface['summary']}")
    print(f"  mode: {surface['mode']}")
    print(f"  input: {surface['input']}")
    print(f"  command: {surface['command']}")
    print(f"  module: {surface['module']}")
    if surface.get("repository_examples"):
        print("  repository examples:")
        for path in surface["repository_examples"]:
            print(f"    {path}")
    print("  authority effect: NONE")
    return 0


def _run_surface(args: argparse.Namespace) -> int:
    surface = canonical_surface_name(args.surface)

    if surface == "admissibility":
        if not args.input:
            raise ValueError("admissibility requires --input <packet.json>")
        from .admissibility import evaluate_admissibility_packet
        result = evaluate_admissibility_packet(_load_json(args.input, "tester packet"))

    elif surface == "llm-admissibility":
        required = {"provider": args.provider, "model": args.model, "prompt": args.prompt, "output": args.output}
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise ValueError("llm-admissibility requires: " + ", ".join(f"--{name}" for name in missing))
        from .llm_admissibility import evaluate_llm_output_admissibility
        result = evaluate_llm_output_admissibility(
            provider=args.provider,
            model=args.model,
            prompt=args.prompt,
            output=args.output,
            declared_intent=args.intent or "research_note",
            consequence_level=args.consequence or "medium",
            include_receipt_reference=True,
        )

    elif surface == "math-admissibility":
        required = {
            "formalism": args.formalism,
            "artifact-type": args.artifact_type,
            "summary": args.summary,
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise ValueError("math-admissibility requires: " + ", ".join(f"--{name}" for name in missing))
        from .math_admissibility import evaluate_math_artifact_admissibility
        result = evaluate_math_artifact_admissibility(
            formalism_id=args.formalism,
            artifact_type=args.artifact_type,
            artifact_summary=args.summary,
            include_receipt_reference=True,
        )

    elif surface == "admittedcode":
        if not args.input:
            raise ValueError("admittedcode requires --input <receipt.json>")
        from .admittedcode_receipt import verify_admittedcode_receipt
        result = verify_admittedcode_receipt(_load_json(args.input, "AdmittedCode receipt"))

    elif surface == "universal-entry":
        if not args.input or not args.registry:
            raise ValueError("universal-entry requires --input <envelope.json> --registry <capabilities.json>")
        from .universal_entry import process_universal_entry
        result = process_universal_entry(
            _load_json(args.input, "universal-entry envelope"),
            _load_json(args.registry, "capability registry"),
        )

    elif surface == "bridges":
        from .bridge_registry import list_dynamic_bridges
        result = {"bridges": list_dynamic_bridges()}

    elif surface == "entry-points":
        from .entry_point_roles import list_entry_point_roles
        result = {"entry_points": list_entry_point_roles()}

    else:
        print(f"Unknown or non-runnable surface: {args.surface}")
        print("Run 'stegverse surfaces' to discover available SDK surfaces.")
        return 2

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="stegverse",
        description="Discover and use allowed local StegVerse SDK surfaces",
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("surfaces", help="list callable SDK surfaces")
    sub.add_parser("capabilities", help="print the user-facing surface registry as JSON")

    help_parser = sub.add_parser("help-surface", help="show help for a named SDK surface")
    help_parser.add_argument("surface")

    run_parser = sub.add_parser("run", help="run an allowed local SDK surface")
    run_parser.add_argument("surface")
    run_parser.add_argument("--input")
    run_parser.add_argument("--registry")
    run_parser.add_argument("--provider")
    run_parser.add_argument("--model")
    run_parser.add_argument("--prompt")
    run_parser.add_argument("--output")
    run_parser.add_argument("--intent")
    run_parser.add_argument("--consequence")
    run_parser.add_argument("--formalism")
    run_parser.add_argument("--artifact-type")
    run_parser.add_argument("--summary")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command is None:
            parser.print_help()
            print("\nStart with: stegverse surfaces")
            return 0
        if args.command == "surfaces":
            print("StegVerse SDK callable surfaces")
            for name, summary in list_surfaces():
                print(f"  {name:<24} {summary}")
            print("\nHelp: stegverse help-surface <name>")
            print("Run:  stegverse run <name> [options]")
            return 0
        if args.command == "capabilities":
            print(json.dumps({"surfaces": list_sdk_surfaces(), "authority_effect": "NONE"}, indent=2, sort_keys=True))
            return 0
        if args.command == "help-surface":
            return print_help_for_surface(args.surface)
        if args.command == "run":
            return _run_surface(args)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
