#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs" / "EXTERNAL_COLLAB_AUTHENTIC_RUNTIME_PROOF_CONTRACT.md"

REQUIRED = (
    "SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003",
    "71000000100110",
    "RESIDENT-EXEC-SDK-WORKSPACE-EXTCOLLAB-CLIENT-SECRET-RESEAL-001",
    "sdk_workspace_external_collab_client_secret_reseal",
    "receipts/sovereign-host/sdk-workspace-external-collab-client-secret-reseal.latest.json",
    "COMPLETED",
    "TARGET_ALREADY_PRESENT",
    "BLOCKED",
    "google_drive.external_collaboration.client_secret",
    "https://stegverse.org/v1/skap/google-drive/external-collaboration/client-secret/ingress",
    "https://stegverse.org/tvc/google-drive/external-collaboration/callback",
    "third_party_tunnel_runtime_required: false",
    "TVC-EXTERNAL-COLLAB-GOOGLE-DRIVE-OWNER-SESSION-001",
    "EXTERNAL_COLLABORATIVE_RESOURCE_READ_ONLY",
    "google_drive_external_collaboration",
    "vault://tvc/providers/google-drive/external-collaboration-session",
    "wsprobe_*",
    "metadata-only/read-only",
    "durable pre-provider replay-consumption",
    "secret-free TVC result",
    "active-probe engine output",
    "OBSERVE -> MATERIALIZE -> REFRESH",
    "REVOKE",
    "EXPIRE",
    "DESTROY",
    "MIR transition reporting",
    "Master Records custody/reconstruction",
    "one-current-device continuity evidence",
    "authority_effect: NONE",
)


def main() -> int:
    text = CONTRACT.read_text(encoding="utf-8")
    missing = [item for item in REQUIRED if item not in text]
    if missing:
        raise SystemExit("missing authentic-runtime proof contract markers: " + ", ".join(missing))
    print("external-collaboration authentic runtime proof contract: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
