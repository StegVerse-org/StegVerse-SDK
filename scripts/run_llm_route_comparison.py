#!/usr/bin/env python3
"""Prepare, submit, or validate governed-vs-recursive comparison artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from stegverse.comparison_transport import (
    build_transport_envelope,
    export_json,
    import_json,
    submit_comparison,
    validate_return_envelope,
)
from stegverse.llm_route_comparison import (
    ComparisonRequest,
    ComparisonRoute,
    required_default_metrics,
)


def _request_from_json(payload: Dict[str, Any]) -> ComparisonRequest:
    routes = [ComparisonRoute(**route) for route in payload["routes"]]
    return ComparisonRequest(
        comparison_id=payload["comparison_id"],
        normalized_input=payload["normalized_input"],
        task_identity=payload["task_identity"],
        output_requirements=payload["output_requirements"],
        routes=routes,
        metrics_requested=payload.get("metrics_requested", required_default_metrics()),
        claim_boundary=payload.get(
            "claim_boundary",
            "SDK preparation is not runtime execution, authority, or proof of superiority.",
        ),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("request", help="JSON request definition")
    parser.add_argument("--endpoint", help="HTTP(S) comparison executor endpoint")
    parser.add_argument("--result", help="Existing result envelope to validate")
    parser.add_argument("--out", required=True, help="Output JSON path")
    args = parser.parse_args()

    request = _request_from_json(import_json(args.request))
    if args.endpoint and args.result:
        parser.error("choose either --endpoint or --result")

    if args.endpoint:
        output = submit_comparison(request, args.endpoint)
    elif args.result:
        output = validate_return_envelope(request, import_json(args.result))
    else:
        output = build_transport_envelope(request)

    export_json(output, args.out)
    print(json.dumps({"status": "ok", "output": str(Path(args.out))}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
