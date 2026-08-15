"""Selected-mode console for MCP tests that exercise production StegVerse artifacts."""
from __future__ import annotations

import argparse
import json
from typing import Any

from .mcp_governance import MCPGovernanceError, load_arguments, run_mcp_governed_test
from .mcp_navigation import guidance_for, navigation_text
from .mcp_transport import MCPTransportError, StdioMCPClient, load_descriptor, reference_descriptor
from .sovereign_validation_runtime import reconstruct_sovereign, replay_sovereign


def _choose(prompt: str, allowed: set[str]) -> str:
    while True:
        try:
            value = input(prompt).strip()
        except EOFError as exc:
            raise ValueError("interactive input unavailable; supply the corresponding command option") from exc
        if value in allowed:
            return value
        print("Choose one of: " + ", ".join(sorted(allowed)))


def _resolve_source(args: argparse.Namespace) -> tuple[str, str | None]:
    if args.mcp_source:
        return args.mcp_source, args.mcp_descriptor
    print("MCP source")
    print("  [1] StegVerse General MCP (inspectable reference server)")
    print("  [2] External MCP (provide safe stdio descriptor)")
    choice = _choose("Select source: ", {"1", "2"})
    if choice == "1":
        return "reference", None
    if args.mcp_descriptor:
        return "external", args.mcp_descriptor
    try:
        path = input("External MCP descriptor JSON path: ").strip()
    except EOFError as exc:
        raise ValueError("--mcp-descriptor is required for non-interactive external MCP testing") from exc
    if not path:
        raise ValueError("external MCP descriptor path is required")
    return "external", path


def _descriptor(source: str, path: str | None) -> dict[str, Any]:
    if source == "reference":
        if path:
            raise ValueError("--mcp-descriptor is not used with --mcp-source reference")
        return reference_descriptor()
    if source == "external":
        if not path:
            raise ValueError("--mcp-descriptor is required with --mcp-source external")
        return load_descriptor(path)
    raise ValueError("--mcp-source must be reference or external")


def _choose_tool(args: argparse.Namespace, source: str, descriptor_path: str | None) -> str:
    if args.tool:
        return args.tool
    descriptor = _descriptor(source, descriptor_path)
    with StdioMCPClient(descriptor) as client:
        tools = client.list_tools()
        if not tools:
            raise ValueError("selected MCP server advertised no tools")
        print("Discovered MCP tools")
        for index, tool in enumerate(tools, start=1):
            print(f"  [{index}] {tool.get('name')} - {tool.get('description', '')}")
        try:
            value = input("Select tool number or exact tool name: ").strip()
        except EOFError as exc:
            raise ValueError("--tool is required for non-interactive MCP testing") from exc
        if value.isdigit() and 1 <= int(value) <= len(tools):
            return str(tools[int(value) - 1].get("name"))
        names = {str(tool.get("name")) for tool in tools}
        if value in names:
            return value
        raise ValueError("selected MCP tool was not in the discovered tools/list result")


def _execute(args: argparse.Namespace, selection: str) -> int:
    if selection == "000":
        print(guidance_for(selection))
        return 0
    if selection == "00":
        print(guidance_for(selection))
        print("Current production test returns ALL caller-visible result fields; canonical custody is always retained independently.")
        return 0
    if selection == "1":
        if not args.manifest_receipt_id:
            print(guidance_for(selection))
            print("Execute: stegverse-mcp-test --select 1 --manifest-receipt-id <MR-...>")
            return 0
        result = replay_sovereign(args.manifest_receipt_id, custody_db=args.custody_db)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    if selection == "2":
        if not args.manifest_receipt_id:
            print(guidance_for(selection))
            print("Execute: stegverse-mcp-test --select 2 --manifest-receipt-id <MR-...>")
            return 0
        result = reconstruct_sovereign(args.manifest_receipt_id, custody_db=args.custody_db)
        result.setdefault("manifest_receipt_id", args.manifest_receipt_id.strip().upper())
        result.setdefault("consequence_reexecuted", False)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    if selection != "0":
        raise ValueError("selection must be 000, 00, 0, 1, or 2")

    print(guidance_for(selection))
    source, descriptor_path = _resolve_source(args)
    tool_name = _choose_tool(args, source, descriptor_path)
    arguments = load_arguments(args.arguments)
    result = run_mcp_governed_test(
        source=source,
        descriptor_path=descriptor_path,
        tool_name=tool_name,
        arguments=arguments,
        custody_db=args.custody_db,
        host_identity=args.host_identity,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="stegverse-mcp-test",
        description="Test MCP calls through canonical StegVerse production artifacts",
    )
    parser.add_argument("--select", choices=("000", "00", "0", "1", "2"))
    parser.add_argument("--mcp-source", choices=("reference", "external"))
    parser.add_argument("--mcp-descriptor", help="safe JSON stdio descriptor for an external MCP server")
    parser.add_argument("--tool", help="exact tool name from the MCP tools/list response")
    parser.add_argument("--arguments", help="path to a JSON object containing tools/call arguments")
    parser.add_argument("--manifest-receipt-id", help="MR-* locator used by selected modes 1 and 2")
    parser.add_argument("--custody-db", default="./stegverse-master-records-validation.db")
    parser.add_argument("--host-identity", default="stegverse-sovereign-local")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    print(navigation_text())
    selection = args.select
    if selection is None:
        try:
            selection = input("\nSelect an option: ").strip()
        except EOFError:
            print("\nUse: stegverse-mcp-test --select 000|00|0|1|2")
            return 2
    print()
    try:
        return _execute(args, selection)
    except (ValueError, MCPGovernanceError, MCPTransportError) as exc:
        print(f"ERROR: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
