#!/usr/bin/env python3
"""Verify documented public imports and retain the first compatibility failure."""

from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path

COMMANDS = [
    "import stegverse; print(stegverse.__version__)",
    "from stegverse import submit_intent, StegVerseLLMAdapter, govern_llm_output, StegVerseSDK",
    "from stegverse import handle_universal_transition_table_package, validate_free_tier_metadata",
    "from stegverse import ExecutorTarget, run_paired_comparison",
    "from stegverse import get_entry_point_role, list_entry_point_roles, build_usage_event, aggregate_session_usage",
    "from stegverse.universal_entry import process_universal_entry, route_universal_entry",
    "from stegverse.universal_entry_dispatch import dispatch_universal_entry",
    "from stegverse.universal_entry_handlers import build_default_handler_registry, conversation_handler, solver_handler",
    "from stegverse.ecosystem_records import AuthoritativeEcosystemRetriever",
    "from stegverse.ecosystem_catalog import build_catalog, validate_catalog",
    "from stegverse.ecosystem_projection import project_record, project_records",
    "from stegverse.canonical_source_collector import CanonicalSourceCollector, validate_collection",
    "from stegverse.repository_source_reader import AllowlistedRepositorySourceReader",
    "from stegverse.github_repository_fetcher import GitHubRepositoryFetcher",
    "from stegverse.governed_conversation import GovernedConversationHandler",
    "from stegverse.http_transport import AuthenticatedJSONTransport, LLMAdapterHTTPTransport",
    "from stegverse.llm_adapter_bridge import GovernedLLMAdapterProvider, normalize_adapter_response",
    "from stegverse.universal_entry_events import build_dispatch_event_chain, validate_event_chain",
    "from stegverse.master_records_custody import MasterRecordsCustodyClient, verify_reconstruction",
    "from stegverse.master_records_http import MasterRecordsHTTPTransport",
    "from stegverse.activation_evidence import evaluate_activation_evidence, validate_activation_evidence",
    "from stegverse.integration_config import build_integration_config, validate_integration_config",
    "from stegverse.spe_allow_consumer import build_progression_packet, validate_spe_receipt",
    "from stegverse.universal_entry_runtime import run_universal_entry",
    "from stegverse.universal_entry_server_runtime import UniversalEntryServerConfig, UniversalEntryServerRuntime",
]


def main() -> int:
    records = []
    failure = None
    for command in COMMANDS:
        try:
            exec(command, {})
            records.append({"command": command, "status": "PASS"})
        except Exception:
            failure = {
                "command": command,
                "status": "FAIL",
                "traceback": traceback.format_exc(),
            }
            records.append(failure)
            break

    payload = {
        "schema_version": "1.0.0",
        "python_version": sys.version,
        "status": "PASS" if failure is None else "FAIL",
        "first_failure": failure,
        "records": records,
        "manual_user_action_required": False,
    }
    output = Path("evidence") / "public-import-diagnostic.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0 if failure is None else 1


if __name__ == "__main__":
    raise SystemExit(main())
