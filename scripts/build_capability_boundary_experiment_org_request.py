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
from pathlib import Path
from scripts.build_mir_sv_exp3_manifest import build_exp3_manifest
from stegverse.manifest_state_transition_runtime import derive_execution_request

REQUEST_ID = "MIR-SV-CAPABILITY-BOUNDARY-EXPERIMENT-003-001"
REQUEST_PATH = f".stegverse/transition-requests/{REQUEST_ID}.json"
MANIFEST_FILE_SHA256 = "e1b05a082ce19d3d254e3cde1dced03019174a94287724959672c9e65510c8f3"
WIRE_MANIFEST_SHA256 = "ad9b8b8aab2beeea04bff2aac34fd2e7bfa5915133bcaef9209c16de7d9bea68"
CANONICAL_MANIFEST_SHA256 = "f0fa715e6a25e7fbf57cf4075ff664751b7606cab93ecdbb59f560e90ae510c6"
REQUEST_FILE_SHA256 = "b5f0f546ea93d8643c77bd1ad5338aaccbd8d2e8875c59438c0380dbeb10bb48"

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


def build_exp3_org_request():
    # Key order of the manifest file, so the request reproduces byte for byte.
    manifest = json.loads(manifest_file_bytes(build_exp3_manifest()))
    return {
        "schema": "stegverse.organization-transition-request/v1",
        "request_id": REQUEST_ID,
        "owning_existing_goal": "MIR-SV-CAPABILITY-BOUNDARY-EXPERIMENT-003",
        "purpose": PURPOSE,
        "manifest": manifest,
        "expected_canonical_manifest_sha256": derive_execution_request(manifest)["canonical_manifest_sha256"],
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
    data = request_file_bytes(build_exp3_org_request())
    digest = hashlib.sha256(data).hexdigest()
    if digest != REQUEST_FILE_SHA256:
        raise SystemExit(f"FAIL_CLOSED: EXP3_ORG_REQUEST_DIGEST_MISMATCH {digest}")
    out = a.organization_root / REQUEST_PATH
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)
    print(f"{REQUEST_PATH} {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
