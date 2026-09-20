"""Execute one validated manifest through its published installed SDK route."""
from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path
from typing import Any, Mapping

from .manifest_contract import validate_ingress_manifest
from .route_resolution import route_from_manifest
from .sdk_event_custody import DEFAULT_CUSTODY_DB, retain_replay_reconstruct


def execute_manifest(manifest: Mapping[str, Any], *, custody_db: str | Path = DEFAULT_CUSTODY_DB) -> dict[str, Any]:
    canonical = validate_ingress_manifest(manifest)
    route = route_from_manifest(canonical)
    binding = route.get("runtime_binding")
    if not isinstance(binding, str) or "." not in binding:
        raise ValueError("installed route does not expose an executable runtime binding")
    module_name, function_name = binding.rsplit(".", 1)
    if not module_name.startswith("stegverse."):
        raise ValueError("runtime binding must resolve inside the installed StegVerse SDK")
    module = importlib.import_module(module_name)
    function = getattr(module, function_name, None)
    if not callable(function):
        raise ValueError(f"installed runtime binding is not callable: {binding}")
    result = function(manifest)
    if not isinstance(result, Mapping):
        raise ValueError("manifest processor returned a non-object result")
    processor_result = dict(result)
    custody = retain_replay_reconstruct(canonical, processor_result, custody_db=custody_db)
    returned = dict(processor_result)
    returned["sdk_event_custody"] = custody
    returned["manifest_receipt_id"] = custody["manifest_receipt_id"]
    returned["master_records_custody_status"] = custody["master_records_custody_status"]
    returned["required_evidence_validation_status"] = custody["required_evidence_validation_status"]
    returned["replay_status"] = custody["replay"]["status"]
    returned["reconstruction_status"] = custody["reconstruction"]["status"]
    returned["receipt_sha256"] = custody["receipt_sha256"]
    returned["reconstructed_receipt_sha256"] = custody["reconstruction"]["reconstructed_receipt_sha256"]
    returned["receipt_reconstruction_digest_equal"] = custody["reconstruction"]["receipt_reconstruction_digest_equal"]
    return returned


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="stegverse run-manifest",
        description="Execute one canonical SDK manifest through its declared installed processor route.",
    )
    parser.add_argument("--manifest", required=True, help="canonical manifest JSON produced by Manifest Builder")
    parser.add_argument("--output", help="write result JSON; default stdout")
    parser.add_argument("--custody-db", default=DEFAULT_CUSTODY_DB, help="canonical Master Records custody database")
    args = parser.parse_args(argv)
    try:
        manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
        result = execute_manifest(manifest, custody_db=args.custody_db)
    except (OSError, json.JSONDecodeError, ValueError, ImportError, AttributeError) as exc:
        parser.error(str(exc))
    text = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
