"""Permanent degraded-mode entry to the canonical sovereign SDK governance runtime.

This module does not implement a second evaluator. It delegates run/replay/
reconstruct operations to ``stegverse.sovereign_validation_runtime`` and returns
that canonical result unchanged. The fallback marker is written to stderr so it
cannot be mistaken for, or mutate, a StegGate governance disposition.

No GitHub token, hosted runtime credential, provider secret, wallet credential,
or non-TV/TVC secret is accepted by this surface.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping

FALLBACK_SCHEMA = "stegverse.sdk.sovereign-fallback-status.v1"
OPERATIONS = ("run", "replay", "reconstruct")


class GovernanceFallbackError(RuntimeError):
    """A classified fallback-entry failure before a canonical result exists."""

    def __init__(self, code: str, detail: str):
        super().__init__(detail)
        self.code = code
        self.detail = detail

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema": FALLBACK_SCHEMA,
            "status": self.code,
            "detail": self.detail,
            "fallback_used": True,
            "authority_effect": "NONE",
        }


def _runtime():
    # Lazy import keeps SDK discovery/help usable when governed-test extras are
    # not installed. Missing canonical components are classified at execution.
    from .sovereign_validation_runtime import (
        SovereignValidationError,
        reconstruct_sovereign,
        replay_sovereign,
        run_sovereign_validation,
    )
    from .public_inspection import load_public_inspection_request

    return (
        SovereignValidationError,
        load_public_inspection_request,
        run_sovereign_validation,
        replay_sovereign,
        reconstruct_sovereign,
    )


def _classify(exc: Exception, sovereign_error_type: type[Exception]) -> GovernanceFallbackError:
    detail = str(exc).strip() or exc.__class__.__name__
    if isinstance(exc, sovereign_error_type):
        if "canonical stegcore, core-lite and master records packages are required" in detail.lower():
            return GovernanceFallbackError("RUNTIME_COMPONENT_UNAVAILABLE", detail)
        return GovernanceFallbackError("GOVERNANCE_RUNTIME_ERROR", detail)
    if isinstance(exc, (FileNotFoundError, json.JSONDecodeError, ValueError, KeyError, TypeError)):
        return GovernanceFallbackError("INVALID_REQUEST", detail)
    return GovernanceFallbackError("FALLBACK_FAILED", detail)


def execute_fallback(
    operation: str,
    target: str,
    *,
    custody_db: str | Path = "./stegverse-master-records-validation.db",
    host_identity: str = "stegverse-sovereign-local",
) -> Mapping[str, Any]:
    """Execute the canonical local path and return its result unchanged.

    ``run`` expects the same public-inspection request accepted by
    ``stegverse.public_inspection_runtime``. ``replay`` and ``reconstruct``
    expect a canonical ``manifest_receipt_id``. This function never converts a
    genuine governance disposition into a fallback/error state.
    """
    op = str(operation).strip().lower()
    if op not in OPERATIONS:
        raise GovernanceFallbackError("INVALID_REQUEST", "operation must be run, replay, or reconstruct")
    target = str(target).strip()
    if not target:
        raise GovernanceFallbackError("INVALID_REQUEST", "target is required")

    (SovereignValidationError, load_request, run, replay, reconstruct) = _runtime()
    try:
        if op == "run":
            return run(load_request(target), custody_db=custody_db, host_identity=host_identity)
        if op == "replay":
            return replay(target, custody_db=custody_db)
        return reconstruct(target, custody_db=custody_db)
    except GovernanceFallbackError:
        raise
    except Exception as exc:  # classification is the public fail-closed boundary
        raise _classify(exc, SovereignValidationError) from exc


def _status(operation: str) -> dict[str, Any]:
    return {
        "schema": FALLBACK_SCHEMA,
        "status": "CANONICAL_SOVEREIGN_FALLBACK_SELECTED",
        "operation": operation,
        "fallback_used": True,
        "canonical_runtime": "stegverse.sovereign_validation_runtime",
        "credential_authority": "TV/TVC",
        "github_token_required": False,
        "non_tv_tvc_secret_or_token_required": False,
        "authority_effect": "NONE",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m stegverse.governance_fallback",
        description="Permanent degraded-mode entry to canonical sovereign StegGate execution",
    )
    parser.add_argument("operation", choices=OPERATIONS)
    parser.add_argument("target", help="request JSON path for run, or manifest_receipt_id for replay/reconstruct")
    parser.add_argument("--custody-db", default="./stegverse-master-records-validation.db")
    parser.add_argument("--host-identity", default="stegverse-sovereign-local")
    args = parser.parse_args(argv)

    print(json.dumps(_status(args.operation), sort_keys=True), file=sys.stderr)
    try:
        result = execute_fallback(
            args.operation,
            args.target,
            custody_db=args.custody_db,
            host_identity=args.host_identity,
        )
    except GovernanceFallbackError as exc:
        print(json.dumps(exc.as_dict(), indent=2, sort_keys=True))
        return 2

    # Canonical result is deliberately not wrapped or rewritten.
    print(json.dumps(dict(result), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
