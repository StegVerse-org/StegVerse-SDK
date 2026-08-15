"""Interactive credential-free connector for a user-controlled LLM."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .llm_connection import (
    DEFAULT_ADAPTER_URLS,
    LLMConnectionError,
    build_connection_descriptor,
    discover_adapter,
    probe_adapter,
    save_connection_descriptor,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="stegverse-connect-llm",
        description=(
            "Connect a user-controlled LLM to StegVerse through the canonical LLM-adapter. "
            "Provider/API/GitHub secrets are not accepted."
        ),
    )
    parser.add_argument("--adapter-url", help="LLM-adapter user-LLM base URL; omit to discover a local adapter")
    parser.add_argument("--user-id", help="local user/participant identifier")
    parser.add_argument("--llm-id", help="stable local name for the connected LLM")
    parser.add_argument("--provider", help="descriptive provider/runtime name; not a credential")
    parser.add_argument("--model", help="model name exposed by the user's LLM")
    parser.add_argument("--scope", action="append", default=[], help="requested non-authorizing scope; demo:read is always retained")
    parser.add_argument("--connection-id", help="optional stable connection descriptor id")
    parser.add_argument("--output-dir", default=".stegverse/llm-connections", help="credential-free descriptor directory")
    parser.add_argument("--no-save", action="store_true", help="probe and print without persisting the descriptor")
    parser.add_argument("--json", action="store_true", help="print the result as JSON")
    return parser


def _prompt(value: str | None, label: str, default: str | None = None) -> str:
    if value:
        return value
    suffix = f" [{default}]" if default else ""
    entered = input(f"{label}{suffix}: ").strip()
    return entered or (default or "")


def _connection_result(args: argparse.Namespace) -> dict:
    if args.adapter_url:
        probe = probe_adapter(args.adapter_url)
    else:
        probe = discover_adapter(DEFAULT_ADAPTER_URLS)
    if probe.state != "CONNECTED":
        raise LLMConnectionError(f"adapter_not_connected:state={probe.state}")

    user_id = _prompt(args.user_id, "User id", "local-user")
    llm_id = _prompt(args.llm_id, "LLM name", "my-llm")
    provider = _prompt(args.provider, "Provider/runtime", "local")
    model = _prompt(args.model, "Model", "local-model")

    descriptor = build_connection_descriptor(
        adapter_url=probe.base_url,
        user_id=user_id,
        llm_id=llm_id,
        provider=provider,
        model=model,
        scopes=args.scope,
        connection_id=args.connection_id,
    )
    saved_path: Path | None = None
    if not args.no_save:
        saved_path = save_connection_descriptor(descriptor, root=args.output_dir)

    return {
        "state": "CONNECTED",
        "adapter_probe": probe.as_dict(),
        "connection": descriptor,
        "saved_path": str(saved_path) if saved_path else None,
        "next": {
            "capabilities": descriptor["endpoints"]["capabilities"],
            "submit_every_llm_request_to": descriptor["endpoints"]["submit"],
            "request_identity": descriptor["identity"],
        },
        "credential_authority": "TV/TVC",
        "non_tv_tvc_secret_or_token_used": False,
        "github_token_required": False,
        "authority_effect": "NONE",
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = _connection_result(args)
    except (LLMConnectionError, EOFError) as exc:
        print(f"ERROR: {exc}")
        print("Start the canonical LLM-adapter user-LLM surface or pass --adapter-url to an admitted instance.")
        return 2

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0

    connection = result["connection"]
    print("CONNECTED")
    print(f"Adapter: {connection['adapter_base_url']}")
    print(f"LLM: {connection['identity']['llm_id']} ({connection['identity']['provider']} / {connection['identity']['model']})")
    if result["saved_path"]:
        print(f"Saved credential-free descriptor: {result['saved_path']}")
    print(f"Capabilities: {connection['endpoints']['capabilities']}")
    print(f"Send every StegVerse LLM submission to: {connection['endpoints']['submit']}")
    print("Credentials: none accepted by the SDK; protected credential authority remains TV/TVC.")
    print("Connection does not itself grant governance, execution, publication, or custody authority.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
