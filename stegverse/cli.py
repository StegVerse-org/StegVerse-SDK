"""Generic command-line discovery surface for the StegVerse SDK.

This interface is intentionally user-neutral: no evaluator, customer, or person
receives a bespoke route.  Installed SDK capabilities are discovered from the
repository capability registry and bounded demo/help routes are exposed here.
"""
from __future__ import annotations

import argparse
import json
from importlib import resources
from pathlib import Path
from typing import Any


def _registry_path() -> Path:
    repo_registry = Path(__file__).resolve().parent.parent / "sdk.capabilities.json"
    if repo_registry.exists():
        return repo_registry
    raise FileNotFoundError("sdk.capabilities.json is not available in this installation")


def load_capabilities() -> dict[str, Any]:
    return json.loads(_registry_path().read_text(encoding="utf-8"))


def _flatten(prefix: str, value: Any, rows: list[tuple[str, str]]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            _flatten(f"{prefix}.{key}" if prefix else key, child, rows)
    elif isinstance(value, list):
        rows.append((prefix, ", ".join(str(v) for v in value)))
    else:
        rows.append((prefix, str(value)))


def list_surfaces(registry: dict[str, Any]) -> list[tuple[str, str]]:
    surfaces: list[tuple[str, str]] = []
    for key, value in registry.items():
        if key in {"schema_version", "repo", "status", "validation_posture", "authority_boundaries", "primary_validation", "activation_definition"}:
            continue
        if isinstance(value, dict):
            surfaces.append((key.replace("_", "-"), "available"))
    return surfaces


def print_help_for_surface(name: str, registry: dict[str, Any]) -> int:
    key = name.replace("-", "_")
    value = registry.get(key)
    if value is None:
        lowered = name.lower()
        # Generic discovery aliases. AdmittedCode consumes governed receipt and
        # admissibility contracts; it is never a person-specific SDK mode.
        if lowered in {"admittedcode", "admitted-code", "admissibility"}:
            print("AdmittedCode / admissibility integration")
            print("  SDK role: construct/consume bounded governance and receipt contracts.")
            print("  Discover: stegverse capabilities | grep -i admiss")
            print("  Documentation: docs/SDK_CONSOLE.md")
            print("  This route grants no execution, mutation, custody, or deployment authority.")
            return 0
        print(f"Unknown surface: {name}")
        print("Run 'stegverse surfaces' to discover available SDK surfaces.")
        return 2
    rows: list[tuple[str, str]] = []
    _flatten(key, value, rows)
    print(name)
    for path, status in rows:
        print(f"  {path}: {status}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="stegverse", description="Discover and use allowed StegVerse SDK surfaces")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("surfaces", help="list discoverable SDK surfaces")
    sub.add_parser("capabilities", help="print the complete machine-readable capability registry")
    help_parser = sub.add_parser("help-surface", help="show help for a named SDK surface")
    help_parser.add_argument("surface")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    registry = load_capabilities()
    if args.command is None:
        build_parser().print_help()
        print("\nStart with: stegverse surfaces")
        return 0
    if args.command == "surfaces":
        print("StegVerse SDK surfaces")
        for name, status in list_surfaces(registry):
            print(f"  {name:<32} {status}")
        print("\nFor a surface: stegverse help-surface <name>")
        return 0
    if args.command == "capabilities":
        print(json.dumps(registry, indent=2, sort_keys=True))
        return 0
    if args.command == "help-surface":
        return print_help_for_surface(args.surface, registry)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
