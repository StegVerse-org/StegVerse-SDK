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

from .capability_map import reconcile_capability_map
from .ecosystem_chat_ask import (
    answer_summary,
    ask_governed_question,
    plan_ask_journey,
    verify_planned_journey,
)
from .governed_llm_fan import EXECUTOR_REPAIR, FAILURE_EXECUTOR_UNAVAILABLE, GovernedLlmFanError
from .governed_composite_response import (
    STRATEGIES,
    STRATEGY_UNANIMOUS,
    compose_governed_response,
    reconstruct_governed_response,
)
from .entry_point_parity import reconcile_entry_point_parity
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


CANONICAL_MANIFEST_ENTRYPOINT = "stegverse.manifest_execution.execute_manifest"
RESULT_RETURN_ENTRYPOINT = "stegverse.manifest_state_transition_runtime.admit_runtime_result"
CLI_SUBMISSION_SCHEMA = "stegverse.sdk.cli-governance-submission/v1"
LOCAL_ENCLOSED_LANE = {
    "lane": "SDK_LOCAL_ENCLOSED_VALIDATION",
    "canonical": False,
    "authorizing": False,
    "selected_by_manifest_route": False,
    "canonical_lifecycle_performed": False,
    "custody_store_is_local": True,
    "may_be_promoted_to_canonical_closure": False,
    "authority_effect": "NONE_ENCLOSED_VALIDATION_ONLY",
}


def _local_enclosed_output(operation: str, result: Mapping[str, Any]) -> dict[str, Any]:
    """Label an explicitly local option so it cannot be read as canonical closure."""
    return {"local_operation": operation, "sdk_execution_lane": dict(LOCAL_ENCLOSED_LANE), "result": dict(result)}


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
    output = _local_enclosed_output(f"fallback:{args.fallback_operation}", result)
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


def _local_enclosed_operations(args: argparse.Namespace):
    """Bind options 1/2 to the local enclosed replay/reconstruct libraries.

    These read the caller's local custody store. They are not the canonical
    manifest-route-selected path and never authorize anything; every output is
    labelled SDK_LOCAL_ENCLOSED_VALIDATION.
    """
    from .governed_operations import GovernedOperations
    from .sovereign_validation_runtime import reconstruct_sovereign, replay_sovereign

    def submit(_request: Mapping[str, Any], **_kwargs: Any) -> Mapping[str, Any]:
        raise ValueError("LOCAL_ENCLOSED_SUBMISSION_NOT_EXPOSED: submit through 0A or 0B")

    def replay(manifest_receipt_id: str, **_kwargs: Any) -> Mapping[str, Any]:
        return replay_sovereign(manifest_receipt_id, custody_db=args.custody_db)

    def reconstruct(manifest_receipt_id: str, **_kwargs: Any) -> Mapping[str, Any]:
        result = dict(reconstruct_sovereign(manifest_receipt_id, custody_db=args.custody_db))
        # Reconstruction is defined by the runtime as non-consequential.
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


def _build_0a_manifest(args: argparse.Namespace) -> dict[str, Any]:
    """Option 0A: raw user data becomes a manifest only through the Manifest Builder."""
    import hashlib
    from .manifest_builder import build_manifest

    if not args.processor_request:
        raise ValueError("MANIFEST_BUILDER_PROCESSOR_REQUEST_REQUIRED: 0A requires --processor-request <request.json>")
    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    digest = hashlib.sha256(
        json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()
    return build_manifest(
        data=data,
        source_framework=args.source_framework,
        source_output_id=args.source_output_id or f"cli-0a-{digest[:16]}",
        processor_request=_load_json(args.processor_request, "processor request"),
        process=args.process,
    )


def _submit_canonical_manifest(key: str, args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    """Options 0A and 0B converge here: one manifest-route-selected entrypoint.

    The console selection decides only how the manifest is prepared (built by
    the Manifest Builder for 0A, taken as supplied for 0B). The runtime is
    whatever the manifest's declared route binds; results come back only
    through admit_runtime_result.
    """
    from .manifest_contract import validate_ingress_manifest
    from .manifest_execution import execute_manifest

    built = key != "0B"
    output: dict[str, Any] = {
        "schema": CLI_SUBMISSION_SCHEMA,
        "selection": "0A" if built else "0B",
        "manifest_preparation": "SDK_MANIFEST_BUILDER" if built else "SUPPLIED_MANIFEST_VALIDATED_WITHOUT_REBUILD",
        "canonical_entrypoint": CANONICAL_MANIFEST_ENTRYPOINT,
        "runtime_selected_by": "MANIFEST_ROUTE_RUNTIME_BINDING",
        "console_selection_selects_runtime": False,
        "result_return_entrypoint": RESULT_RETURN_ENTRYPOINT,
        "authority_effect": "NONE",
    }
    try:
        if built:
            manifest = _build_0a_manifest(args)
            if manifest.get("manifest_profile") is None:
                # The builder returned a resolution (unknown, offline or
                # unresolved capability); nothing is dispatched.
                output.update({
                    "disposition": "FAIL_CLOSED",
                    "failed_predicate": "MANIFEST_BUILDER_PRODUCED_EXECUTABLE_MANIFEST",
                    "evidence": manifest,
                })
                return 2, output
            output["manifest"] = manifest
        else:
            manifest = dict(_load_json(args.manifest, "ingress manifest"))
        output["canonical_manifest_sha256"] = validate_ingress_manifest(manifest)["canonical_manifest_sha256"]
        result = execute_manifest(manifest)
    except (OSError, json.JSONDecodeError, ValueError, ImportError, AttributeError) as exc:
        output.update({
            "disposition": "FAIL_CLOSED",
            "failed_predicate": str(exc).split(":", 1)[0] or type(exc).__name__,
            "evidence": f"{type(exc).__name__}: {exc}",
        })
        return 2, output
    lineage = (result.get("manifest_lineage") or {}).get("run_manifest_request") or {}
    output.update({
        "route_id": lineage.get("route_id"),
        "runtime_binding": lineage.get("runtime_binding"),
        "disposition": result.get("disposition"),
        "failed_predicate": result.get("failed_predicate"),
        "result": result,
    })
    return (0 if result.get("disposition") == "ALLOW" else 2), output


def _execute_selected_governance(args: argparse.Namespace, key: str) -> int | None:
    """Execute ordinary 0A/0B/1/2 when the caller supplied the required operand."""
    if (key in {"0", "0A"} and args.input) or (key == "0B" and args.manifest):
        rc, output = _submit_canonical_manifest(key, args)
        print(json.dumps(output, indent=2, sort_keys=True))
        return rc
    if key == "1" and args.manifest_receipt_id:
        output = _local_enclosed_output("replay", _local_enclosed_operations(args).replay(args.manifest_receipt_id))
    elif key == "2" and args.manifest_receipt_id:
        output = _local_enclosed_output("reconstruct", _local_enclosed_operations(args).reconstruct(args.manifest_receipt_id))
    else:
        return None
    print(json.dumps(output, indent=2, sort_keys=True))
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
            print("Execute 0A: stegverse governance --select 0A --input <raw-data.json> --processor-request <request.json>")
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
        print("The Master Records organization record remains independent of the user-return projection.")
    elif key == "0":
        print("Next: choose 0A for raw/user data or 0B for a preformatted machine manifest.")
        print("Execute 0A: stegverse governance --select 0A --input <raw-data.json> --processor-request <request.json>")
        print("Execute 0B: stegverse governance --select 0B --manifest <stegverse.ingress-manifest.v1.json>")
    elif key == "0A":
        print("Provide --input <raw-data.json> --processor-request <request.json> to build and submit option 0A.")
    elif key == "0B":
        print("Provide --manifest <stegverse.ingress-manifest.v1.json> to validate and submit option 0B through its declared route.")
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
    if surface == "self-characterization":
        if not args.input:
            raise ValueError("self-characterization requires --input <profile.json>")
        from .self_characterization_lane import validate_lane_profile
        result = validate_lane_profile(_load_json(args.input, "self-characterization profile"))
    elif surface == "manifold-governance":
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


def _ask_question(args: argparse.Namespace) -> int:
    """Ask from the console entry: plan the journey, run the fan, answer."""

    routes = json.loads(Path(args.routes).read_text(encoding="utf-8"))
    if not isinstance(routes, list):
        print("--routes must hold a JSON list of routes")
        return 2
    journey = plan_ask_journey(args.question, routes, fan_journey_id=args.fan)

    if args.plan_only:
        print(json.dumps({
            "journey": journey,
            "verification": verify_planned_journey(journey),
        }, indent=2, sort_keys=True, default=list))
        return 0

    relation = None
    if args.joint_relation:
        relation = json.loads(Path(args.joint_relation).read_text(encoding="utf-8"))
    try:
        answer = ask_governed_question(
            args.question, journey, strategy=args.strategy, joint_relation=relation,
        )
    except GovernedLlmFanError as error:
        # The node's StegBrowser capability is what performs the branches. When
        # it is not reachable, say so and name the repair rather than traceback.
        print(json.dumps({
            "disposition": "FAN_NOT_ATTEMPTED",
            "failure_code": FAILURE_EXECUTOR_UNAVAILABLE,
            "detail": str(error),
            "required_evidence_or_repair": EXECUTOR_REPAIR,
            "journey_planned": True,
            "authority_effect": "NONE",
        }, indent=2, sort_keys=True))
        return 1
    print(json.dumps({
        "answer": answer,
        "summary": answer_summary(answer),
    }, indent=2, sort_keys=True, default=list))
    return 0 if answer["governed_claim"] else 1


def _compose_response(args: argparse.Namespace) -> int:
    """Compose worker answers from the console entry, optionally replaying them."""

    components = json.loads(Path(args.components).read_text(encoding="utf-8"))
    if not isinstance(components, list):
        print("--components must hold a JSON list of worker results")
        return 2
    relation = None
    if args.joint_relation:
        relation = json.loads(Path(args.joint_relation).read_text(encoding="utf-8"))

    composite = compose_governed_response(
        components,
        composition_id=args.composition_id,
        fan_journey_id=args.fan,
        strategy=args.strategy,
        joint_relation=relation,
    )
    payload = {"composite": composite}
    if args.replay:
        payload["replay"] = reconstruct_governed_response(composite, components)
    print(json.dumps(payload, indent=2, sort_keys=True, default=list))
    return 0 if composite["disposition"] != "FAIL_CLOSED" else 1


def build_parser() -> argparse.ArgumentParser:
    from .machine_contract import MANIFEST_COMMANDS
    parser = argparse.ArgumentParser(
        prog="stegverse", description="Discover and use allowed local StegVerse SDK surfaces",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Manifest commands:\n" + "\n".join(
            f"{name}: {help_text}" for name, help_text in MANIFEST_COMMANDS.items()),
    )
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("surfaces", help="list callable SDK surfaces")
    sub.add_parser("capabilities", help="print the user-facing surface registry as JSON")
    sub.add_parser("entry-point-parity",
                   help="show whether the Chat entry point equates to a console entry")
    sub.add_parser("capability-map",
                   help="reconcile installed routes against what an evaluator can invoke")
    ask = sub.add_parser(
        "ask",
        help="ask the ecosystem a question and get one governed multi-LLM answer",
    )
    ask.add_argument("--question", required=True)
    ask.add_argument("--routes", required=True,
                    help="JSON file holding a list of {provider, model, secure_url} routes")
    ask.add_argument("--fan", required=True, help="fan journey_id for this question")
    ask.add_argument("--strategy", choices=STRATEGIES, default=STRATEGY_UNANIMOUS)
    ask.add_argument("--joint-relation",
                    help="JSON file holding a validated joint-relation record")
    ask.add_argument("--plan-only", action="store_true",
                    help="plan and verify the journey without running the fan")
    compose = sub.add_parser(
        "compose-response",
        help="compose N worker LLM answers into one governed composite response",
    )
    compose.add_argument("--components", required=True,
                        help="JSON file holding a list of stegbrowser.llm-profile-result.v1 results")
    compose.add_argument("--composition-id", required=True, help="caller-chosen composition identity")
    compose.add_argument("--fan", required=True, help="fan journey_id the worker branches were issued under")
    compose.add_argument("--strategy", choices=STRATEGIES, default=STRATEGY_UNANIMOUS)
    compose.add_argument("--joint-relation",
                        help="JSON file holding a validated joint-relation record; without one the composite is RELATION_UNRESOLVED")
    compose.add_argument("--replay", action="store_true",
                        help="also reconstruct the composite from the same components and report whether it matches")
    governance = sub.add_parser("governance", help="guided demo/parameter/submit/replay/reconstruct governance navigation")
    governance.add_argument("--select", choices=("000", "00", "0", "0A", "0B", "1", "2"), help="show guidance or execute one canonical governance option")
    governance.add_argument("--input", help="option 0A raw data JSON; the SDK Manifest Builder builds the manifest, then it is submitted through its declared route")
    governance.add_argument("--processor-request", help="option 0A processor request JSON passed to the SDK Manifest Builder")
    governance.add_argument("--process", default="governance", help="option 0A processing capability declared in the built manifest")
    governance.add_argument("--source-framework", default="stegverse-cli", help="option 0A source_framework recorded in the built manifest")
    governance.add_argument("--source-output-id", help="option 0A source_output_id; default derives from the data digest")
    governance.add_argument("--manifest", help="option 0B stegverse.ingress-manifest.v1 JSON; validated without rebuild and submitted through its declared route")
    governance.add_argument("--manifest-receipt-id", help="MR-* locator for option 1 replay or option 2 reconstruction against the local enclosed custody store (non-canonical)")
    governance.add_argument("--fallback-operation", choices=("run", "replay", "reconstruct"), help="local enclosed degraded-mode path (SDK_LOCAL_ENCLOSED_VALIDATION, non-canonical, non-authorizing)")
    governance.add_argument("--fallback-target", help="request JSON path for fallback run, or manifest_receipt_id for replay/reconstruct")
    governance.add_argument("--records-db", "--custody-db", dest="custody_db", default="./stegverse-master-records-validation.db", help="local enclosed custody store used only by options 1/2 and --fallback-operation (non-canonical)")
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
        if args.command == "entry-point-parity":
            print(json.dumps(reconcile_entry_point_parity(), indent=2, sort_keys=True, default=list))
            return 0

        if args.command == "ask":
            return _ask_question(args)

        if args.command == "compose-response":
            return _compose_response(args)

        if args.command == "capability-map":
            print(json.dumps(reconcile_capability_map(), indent=2, sort_keys=True, default=list))
            return 0

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
            print(json.dumps({
                "surfaces": list_sdk_surfaces(),
                "installed_routes": reconcile_capability_map()["rows"],
                "authority_effect": "NONE",
            }, indent=2, sort_keys=True, default=list))
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
