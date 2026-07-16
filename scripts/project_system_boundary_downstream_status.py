#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

OUTPUT = Path(__file__).resolve().parents[1] / "evidence" / "system-boundary-downstream-status.v0.1.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--conclusion", required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--source-branch", required=True)
    args = parser.parse_args()

    passed = args.conclusion == "success" and args.source_branch == "main"
    payload = {
        "schema_version": "stegverse.system_boundary.downstream_status.v0.1",
        "status_only": True,
        "repository": "StegVerse-org/StegVerse-SDK",
        "source_workflow": "StegVerse SDK Validation",
        "source_branch": args.source_branch,
        "source_commit": args.source_commit,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "activation_state": "VERIFIED" if passed else "PENDING_VALIDATION",
        "verified": passed,
        "downstream_propagation_allowed": passed,
        "targets": ["StegVerse-Labs/Site"],
        "production_binding_enabled": False,
        "release_authorized": False,
        "execution_authority_granted": False,
        "custody_transferred": False,
        "admissibility_determined": False,
        "manual_user_action_required": False,
        "evidence": {
            "latest_observed_workflow_run_id": int(args.run_id),
            "latest_observed_conclusion": args.conclusion,
            "current_main_validation_observed": True,
            "current_main_validation_passed": passed
        }
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(payload["activation_state"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
