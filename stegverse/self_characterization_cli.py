"""CLI for the reusable Self-Characterization Trajectory SDK lane."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

from .self_characterization_lane import (
    derive_viewer_operation_id,
    score_experiment,
    validate_lane_profile,
)


def _load(path: str) -> Mapping[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, Mapping):
        raise ValueError("input JSON must be an object")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="stegverse-self-characterization")
    sub = parser.add_subparsers(dest="command", required=True)

    prepare = sub.add_parser("prepare", help="validate and normalize one S0 lane profile")
    prepare.add_argument("--input", required=True)

    score = sub.add_parser("score", help="score one completed experiment evidence packet")
    score.add_argument("--input", required=True)

    for name in ("viewer-replay", "viewer-reconstruct"):
        op = sub.add_parser(name, help=f"run canonical {name.split('-')[1]} with viewer-bound correlation")
        op.add_argument("--manifest-receipt-id", required=True)
        op.add_argument("--viewer-node-id", required=True)
        op.add_argument("--custody-db", default="./stegverse-master-records-validation.db")

    args = parser.parse_args(argv)
    if args.command == "prepare":
        result = validate_lane_profile(_load(args.input))
    elif args.command == "score":
        payload = _load(args.input)
        result = score_experiment(
            trajectory=payload["trajectory"],
            governance=payload["governance"],
            accountability=payload["accountability"],
            autonomous_initiative_observed=bool(payload.get("autonomous_initiative_observed")),
            consequential_boundary_bypass_observed=bool(payload.get("consequential_boundary_bypass_observed")),
            reconstruction_blocked_by_evidence_gap=bool(payload.get("reconstruction_blocked_by_evidence_gap")),
            undeclared_governance_modification_observed=bool(payload.get("undeclared_governance_modification_observed")),
        )
    else:
        operation = "REPLAY" if args.command == "viewer-replay" else "RECONSTRUCT"
        binding = derive_viewer_operation_id(
            manifest_receipt_id=args.manifest_receipt_id,
            viewer_node_id=args.viewer_node_id,
            operation=operation,
        )
        from .sovereign_validation_runtime import replay_sovereign, reconstruct_sovereign
        if operation == "REPLAY":
            artifact = replay_sovereign(
                args.manifest_receipt_id,
                custody_db=args.custody_db,
                viewer_node_id=args.viewer_node_id,
                viewer_operation_id=binding["viewer_operation_id"],
            )
        else:
            artifact = reconstruct_sovereign(
                args.manifest_receipt_id,
                custody_db=args.custody_db,
                viewer_node_id=args.viewer_node_id,
                viewer_operation_id=binding["viewer_operation_id"],
            )
        result = {"viewer_binding": binding, "artifact": artifact}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
