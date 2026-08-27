"""Generic command-line entry point for the StegVerse SDK.

The console is intentionally user-neutral. It exposes discoverable, locally
callable SDK surfaces and preserves the SDK's non-authorizing boundary.
"""
from __future__ import annotations

import argparse
from importlib import resources
import json
from pathlib import Path
import sys
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


def _load_demo_json(filename: str) -> Mapping[str, Any]:
    try:
        text = resources.files("stegverse.demo_data").joinpath(filename).read_text(encoding="utf-8")
        value = json.loads(text)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"bundled demo fixture is unavailable or invalid: {filename}: {exc}") from exc
    if not isinstance(value, Mapping):
        raise ValueError(f"bundled demo fixture must contain a JSON object: {filename}")
    return value


def list_surfaces(_registry: dict[str, Any] | None = None) -> list[tuple[str, str]]:
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
    if surface.get("demo_command"):
        print(f"  demo: {surface['demo_command']}")
    print(f"  module: {surface['module']}")
    if surface.get("documentation"):
        print(f"  documentation: {surface['documentation']}")
    if surface.get("result_semantics"):
        print(f"  result semantics: {surface['result_semantics']}")
    if surface.get("repository_examples"):
        print("  repository examples:")
        for path in surface["repository_examples"]:
            print(f"    {path}")
    print("  authority effect: NONE")
    return 0


def _record_navigation_usage(selection: str) -> None:
    """Best-effort usage observation that never becomes an authority dependency."""
    try:
        from .sdk_usage_observability import record_navigation_selection
        key = selection.strip().upper()
        record_navigation_selection("0" if key in {"0A", "0B"} else selection)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"WARNING: SDK usage observation unavailable: {exc}", file=sys.stderr)


def _run_governance_fallback(args: argparse.Namespace) -> int:
    """Run the permanent degraded-mode path without rewriting its canonical result."""
    from .governance_fallback import GovernanceFallbackError, execute_fallback

    if not args.fallback_target:
        raise ValueError("--fallback-target is required with --fallback-operation")
    try:
        result = execute_fallback(
            args.fallback_operation,
            args.fallback_target,
            custody_db=args.custody_db,
            host_identity=args.host_identity,
        )
    except GovernanceFallbackError as exc:
        print(json.dumps(exc.as_dict(), indent=2, sort_keys=True))
        return 2
    print(json.dumps(dict(result), indent=2, sort_keys=True))
    return 0


def _canonical_governed_operations(args: argparse.Namespace):
    """Bind ordinary options 0A/1/2 to the canonical sovereign runtime.

    The SDK supplies no credential and creates no second evaluator. The existing
    ``GovernedOperations`` adapter records only bounded usage observations after
    canonical run identity/evidence has been returned.
    """
    from .governed_operations import GovernedOperations
    from .sovereign_validation_runtime import (
        reconstruct_sovereign,
        replay_sovereign,
        run_sovereign_validation,
    )

    def submit(request: Mapping[str, Any], **_kwargs: Any) -> Mapping[str, Any]:
        return run_sovereign_validation(
            request,
            custody_db=args.custody_db,
            host_identity=args.host_identity,
        )

    def replay(manifest_receipt_id: str, **_kwargs: Any) -> Mapping[str, Any]:
        return replay_sovereign(manifest_receipt_id, custody_db=args.custody_db)

    def reconstruct(manifest_receipt_id: str, **_kwargs: Any) -> Mapping[str, Any]:
        result = dict(reconstruct_sovereign(manifest_receipt_id, custody_db=args.custody_db))
        # Reconstruction is defined by the canonical runtime as non-consequential.
        # Supply the adapter's explicit proof field without changing the retained
        # reconstruction artifact or creating execution authority.
        result.setdefault("manifest_receipt_id", manifest_receipt_id.strip().upper())
        result.setdefault("consequence_reexecuted", False)
        return result

    return GovernedOperations(
        submit_handler=submit,
        replay_handler=replay,
        reconstruct_handler=reconstruct,
    )


def _execute_selected_governance(args: argparse.Namespace, key: str) -> int | None:
    """Execute ordinary 0A/0B/1/2 when the caller supplied the required operand."""
    operations = _canonical_governed_operations(args)
    if key in {"0", "0A"} and args.input:
        from .public_inspection import load_public_inspection_request
        result = operations.submit(load_public_inspection_request(args.input))
    elif key == "0B" and args.manifest:
        from .governance_ingress_runtime import run_external_manifest
        result = run_external_manifest(
            _load_json(args.manifest, "ingress manifest"),
            custody_db=args.custody_db,
            host_identity=args.host_identity,
        )
    elif key == "1" and args.manifest_receipt_id:
        result = operations.replay(args.manifest_receipt_id)
    elif key == "2" and args.manifest_receipt_id:
        result = operations.reconstruct(args.manifest_receipt_id)
    else:
        return None
    print(json.dumps(dict(result), indent=2, sort_keys=True))
    return 0


def _governance_guide(args: argparse.Namespace) -> int:
    if args.fallback_operation:
        return _run_governance_fallback(args)

    from .governance_navigation import demo_output_manifest_shape, guidance_for, navigation_text
    print(navigation_text())
    selection = args.select
    if selection is None:
        try:
            selection = input("\nSelect an option: ").strip()
        except EOFError:
            print("\nUse: stegverse governance --select 000|00|0|0A|0B|1|2")
            print("Execute 0A: stegverse governance --select 0A --input <public-inspection-request.json>")
            print("Execute 0B: stegverse governance --select 0B --manifest <stegverse.ingress-manifest.v1.json>")
            print("Replay: stegverse governance --select 1 --manifest-receipt-id <MR-...>")
            print("Reconstruct: stegverse governance --select 2 --manifest-receipt-id <MR-...>")
            print("Fallback: stegverse governance --fallback-operation run|replay|reconstruct --fallback-target <target>")
            return 2
    print()
    # Validate through canonical guidance first, then observe the accepted selection.
    guidance = guidance_for(selection)
    _record_navigation_usage(selection)
    print(guidance)
    key = selection.strip().upper()

    executed = _execute_selected_governance(args, key)
    if executed is not None:
        return executed

    if key == "000":
        print("\nDEMO SELF-DESCRIBING OUTPUT SHAPE")
        print(json.dumps(demo_output_manifest_shape(), indent=2, sort_keys=True))
        print("\nThis demonstration output is explanatory and non-authorizing. A new manifest must still be submitted through the normal governed path.")
    elif key == "00":
        print("Next: define permitted run preferences, including ALL, SELECTED, or NONE user-return transition projection.")
        print("Master Records custody remains independent of the user-return projection.")
    elif key == "0":
        print("Next: choose 0A for raw/user data or 0B for a preformatted machine manifest.")
        print("Execute 0A: stegverse governance --select 0A --input <public-inspection-request.json>")
        print("Execute 0B: stegverse governance --select 0B --manifest <stegverse.ingress-manifest.v1.json>")
    elif key == "0A":
        print("Provide --input <public-inspection-request.json> to execute option 0A.")
    elif key == "0B":
        print("Provide --manifest <stegverse.ingress-manifest.v1.json> to validate, canonicalize, and execute option 0B.")
    elif key == "1":
        print("Next: provide the manifest_receipt_id returned by the original run.")
        print("Execute: stegverse governance --select 1 --manifest-receipt-id <MR-...>")
    elif key == "2":
        print("Next: provide the manifest_receipt_id returned by the original run.")
        print("Execute: stegverse governance --select 2 --manifest-receipt-id <MR-...>")
    return 0


def _verify_admittedcode(receipt: Mapping[str, Any]) -> dict[str, Any]:
    from .admittedcode_receipt import verify_admittedcode_receipt
    return verify_admittedcode_receipt(receipt)


def _demo_surface(args: argparse.Namespace) -> int:
    surface = canonical_surface_name(args.surface)
    if surface == "manifold-governance":
        from .manifold_governance import evaluate_manifold_governance
        result = evaluate_manifold_governance(
            _load_demo_json("manifold_governance_reviewable.json")
        )
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0

    if surface != "admittedcode":
        print(f"No bundled demo is registered for: {args.surface}")
        print("Run 'stegverse surfaces' and 'stegverse help-surface <name>' for available local operations.")
        return 2

    cases = {"allow": "admittedcode_allow.json", "deny": "admittedcode_deny.json"}
    selected = [args.case] if args.case in cases else ["allow", "deny"]
    results: dict[str, Any] = {}
    for case in selected:
        fixture = cases[case]
        results[case] = {
            "fixture": f"stegverse.demo_data/{fixture}",
            "verification": _verify_admittedcode(_load_demo_json(fixture)),
        }
    print(json.dumps({
        "surface": "admittedcode",
        "demo": "portable receipt verification",
        "authority_effect": "NONE",
        "results": results,
    }, indent=2, sort_keys=True))
    return 0

def _run_surface(args: argparse.Namespace) -> int:
    surface = canonical_surface_name(args.surface)
    if surface == "manifold-governance":
        if not args.input:
            raise ValueError("manifold-governance requires --input <packet.json>")
        from .manifold_governance import evaluate_manifold_governance
        result = evaluate_manifold_governance(_load_json(args.input, "manifold governance packet"))
    elif surface == "admissibility":
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
        required = {"formalism": args.formalism, "artifact-type": args.artifact_type, "summary": args.summary}
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
            raise ValueError("admittedcode requires --input <receipt.json>; for bundled examples run 'stegverse demo admittedcode'")
        result = _verify_admittedcode(_load_json(args.input, "AdmittedCode receipt"))
    elif surface == "universal-entry":
        if not args.input or not args.registry:
            raise ValueError("universal-entry requires --input <envelope.json> --registry <capabilities.json>")
        from .universal_entry import process_universal_entry
        result = process_universal_entry(_load_json(args.input, "universal-entry envelope"), _load_json(args.registry, "capability registry"))
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
    parser = argparse.ArgumentParser(prog="stegverse", description="Discover and use allowed local StegVerse SDK surfaces")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("surfaces", help="list callable SDK surfaces")
    sub.add_parser("capabilities", help="print the user-facing surface registry as JSON")
    governance = sub.add_parser("governance", help="guided demo/parameter/submit/replay/reconstruct governance navigation")
    governance.add_argument("--select", choices=("000", "00", "0", "0A", "0B", "1", "2"), help="show guidance or execute one canonical governance option")
    governance.add_argument("--input", help="option 0A public-inspection request JSON to execute through the canonical sovereign runtime")
    governance.add_argument("--manifest", help="option 0B stegverse.ingress-manifest.v1 JSON to validate/canonicalize and execute through the canonical sovereign runtime")
    governance.add_argument("--manifest-receipt-id", help="canonical MR-* locator for option 1 replay or option 2 reconstruction")
    governance.add_argument("--fallback-operation", choices=("run", "replay", "reconstruct"), help="use the permanent canonical sovereign degraded-mode path")
    governance.add_argument("--fallback-target", help="request JSON path for fallback run, or manifest_receipt_id for replay/reconstruct")
    governance.add_argument("--custody-db", default="./stegverse-master-records-validation.db", help="local canonical Master Records custody database")
    governance.add_argument("--host-identity", default="stegverse-sovereign-local", help="local sovereign execution host identity")
    help_parser = sub.add_parser("help-surface", help="show help for a named SDK surface")
    help_parser.add_argument("surface")
    demo_parser = sub.add_parser("demo", help="run a bundled, credential-free demonstration")
    demo_parser.add_argument("surface")
    demo_parser.add_argument("--case", choices=("allow", "deny", "all"), default="all")
    run_parser = sub.add_parser("run", help="run an allowed local SDK surface")
    run_parser.add_argument("surface")
    for option in ("input", "registry", "provider", "model", "prompt", "output", "intent", "consequence", "formalism", "artifact-type", "summary"):
        run_parser.add_argument(f"--{option}", dest=option.replace("-", "_"))
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command is None:
            parser.print_help()
            print("\nStart with: stegverse governance")
            print("Discover surfaces: stegverse surfaces")
            print("Bundled demos: stegverse demo admittedcode | stegverse demo manifold-governance")
            return 0
        if args.command == "governance":
            return _governance_guide(args)
        if args.command == "surfaces":
            print("StegVerse SDK callable surfaces")
            for name, summary in list_surfaces():
                print(f"  {name:<24} {summary}")
            print("\nHelp: stegverse help-surface <name>")
            print("Run:  stegverse run <name> [options]")
            print("Governance: stegverse governance")
            print("Demo: stegverse demo admittedcode | stegverse demo manifold-governance")
            return 0
        if args.command == "capabilities":
            print(json.dumps({"surfaces": list_sdk_surfaces(), "authority_effect": "NONE"}, indent=2, sort_keys=True))
            return 0
        if args.command == "help-surface":
            return print_help_for_surface(args.surface)
        if args.command == "demo":
            return _demo_surface(args)
        if args.command == "run":
            return _run_surface(args)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
