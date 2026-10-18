"""Emit the organization transition request that records MIR/SV Experiment 3.

StegVerse-org/.github's organization-ledger-transition.yml receives a request
committed under .stegverse/transition-requests/ and appends the organization
receipt by manifest. This writes that request deterministically: the frozen
Experiment 3 manifest from build_mir_sv_exp3_manifest, unchanged, with the
canonical digest the organization ingress recomputes under this SDK. It grants
nothing; the ingress decides the disposition and the ledger records it.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from pathlib import Path
from scripts.build_mir_sv_exp3_manifest import build_exp3_manifest
from stegverse.manifest_state_transition_runtime import derive_execution_request

REQUEST_ID = "MIR-SV-CAPABILITY-BOUNDARY-EXPERIMENT-003-001"
REQUEST_PATH = f".stegverse/transition-requests/{REQUEST_ID}.json"
MANIFEST_FILE_SHA256 = "e1b05a082ce19d3d254e3cde1dced03019174a94287724959672c9e65510c8f3"
WIRE_MANIFEST_SHA256 = "ad9b8b8aab2beeea04bff2aac34fd2e7bfa5915133bcaef9209c16de7d9bea68"
CANONICAL_MANIFEST_SHA256 = "f0fa715e6a25e7fbf57cf4075ff664751b7606cab93ecdbb59f560e90ae510c6"
REQUEST_FILE_SHA256 = "b5f0f546ea93d8643c77bd1ad5338aaccbd8d2e8875c59438c0380dbeb10bb48"
OWNING_EXISTING_GOAL = "MIR-SV-CAPABILITY-BOUNDARY-EXPERIMENT-003"
RETRY_ENTRYPOINT = "python -m scripts.build_capability_boundary_experiment_org_request"

PURPOSE = (
    "Record the frozen MIR/SV Experiment 3 SDK diagnostic manifest (COSV 50000000100000; owner "
    "StegVerse-Labs/.github#2682) as an organization transition by manifest on this organization's "
    "ingress, so the Experiment 3 organization receipt is appended to refs/stegverse/organization-ledger "
    "and read back from a fresh fetch. The exact already-built manifest is submitted unchanged "
    "(StegVerse-org/StegVerse-SDK scripts/build_mir_sv_exp3_manifest.py; file sha256 "
    f"{MANIFEST_FILE_SHA256}, wire sha256 {WIRE_MANIFEST_SHA256}); read-only ecosystem_diagnostic, "
    "no Publisher distribution, no external egress or physical execution is claimed."
)


def manifest_file_bytes(manifest):
    """The manifest file exactly as build_mir_sv_exp3_manifest writes it."""
    return (json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


class FailClosed(Exception):
    """A pinned digest did not reproduce; carries the six-field failure record."""

    def __init__(self, record):
        super().__init__(record["failure_code"])
        self.record = record


def failure_record(failure_code, failed_predicate, required_evidence_or_repair, next_attempt):
    return {
        "failure_code": failure_code,
        "failed_predicate": failed_predicate,
        "required_evidence_or_repair": required_evidence_or_repair,
        "retry_entrypoint": RETRY_ENTRYPOINT,
        "owning_existing_goal": OWNING_EXISTING_GOAL,
        "next_attempt": next_attempt,
    }


def pinned_canonical_manifest_sha256(manifest):
    """The canonical digest, derived here and required to equal the pinned constant.

    The organization ingress (StegVerse-org/.github organization-ledger-transition.yml)
    recomputes this as derive_execution_request(manifest, boundary())["canonical_manifest_sha256"]
    with its own Interlock/InTr boundary, whereas this derives it with no boundary.
    The digest comes from validate_ingress_manifest and is boundary-independent: the
    boundary only selects manifest_declared_destination. Tests prove the digest is
    identical with organization_boundary=None and with a boundary shaped like the
    organization's boundary(), and this fails closed if the derivation ever drifts.
    """
    derived = derive_execution_request(manifest)["canonical_manifest_sha256"]
    if derived != CANONICAL_MANIFEST_SHA256:
        raise FailClosed(failure_record(
            "EXP3_ORG_REQUEST_CANONICAL_MANIFEST_MISMATCH",
            f"derive_execution_request(manifest).canonical_manifest_sha256 == {CANONICAL_MANIFEST_SHA256} "
            f"(derived {derived})",
            "Restore the frozen Experiment 3 manifest or the SDK canonicalization it was pinned "
            "under; re-pin CANONICAL_MANIFEST_SHA256 only through a reviewed change that also "
            "proves the organization ingress recomputes the same digest.",
            "Re-run the retry entrypoint after the manifest or canonicalization is restored; "
            "no request is written until the derived canonical digest equals the pin."))
    return derived


def build_exp3_org_request():
    # Key order of the manifest file, so the request reproduces byte for byte.
    manifest = json.loads(manifest_file_bytes(build_exp3_manifest()))
    return {
        "schema": "stegverse.organization-transition-request/v1",
        "request_id": REQUEST_ID,
        "owning_existing_goal": "MIR-SV-CAPABILITY-BOUNDARY-EXPERIMENT-003",
        "purpose": PURPOSE,
        "manifest": manifest,
        "expected_canonical_manifest_sha256": pinned_canonical_manifest_sha256(manifest),
        "standing": {
            "mode": "ESTABLISH_GENESIS",
            "node_ref": "StegVerse-org/StegVerse-SDK",
            "predecessor": None,
            "_declared_not_authenticated": (
                "A declared standing is not authenticated standing; the ingress decides "
                "the disposition and the organization ledger records it either way."),
        },
    }


def request_file_bytes(request):
    return (json.dumps(request, indent=2) + "\n").encode("utf-8")


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--organization-root", type=Path, required=True,
                   help="StegVerse-org/.github checkout the request is written into")
    a = p.parse_args(argv)
    try:
        data = request_file_bytes(build_exp3_org_request())
        digest = hashlib.sha256(data).hexdigest()
        if digest != REQUEST_FILE_SHA256:
            raise FailClosed(failure_record(
                "EXP3_ORG_REQUEST_DIGEST_MISMATCH",
                f"sha256(request file bytes) == {REQUEST_FILE_SHA256} (observed {digest})",
                "Restore the request builder, purpose text or manifest so the request file "
                "reproduces byte for byte; re-pin REQUEST_FILE_SHA256 only through a reviewed change.",
                "Re-run the retry entrypoint after the request reproduces; nothing is written "
                "into the organization checkout until the digest equals the pin."))
    except FailClosed as exc:
        sys.stderr.write(json.dumps(exc.record, sort_keys=True) + "\n")
        return 1
    out = a.organization_root / REQUEST_PATH
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)
    print(f"{REQUEST_PATH} {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
