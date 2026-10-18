# InTr destination hop lane

A diagnostic of one-way InTr integrity and organization-ledger receipt integrity. It is also the SDK test lane that CI runs in fabricated mode.

Fabricated mode discovers peers from each checkout's own advertisement. Live mode asks the GitHub API for the same advertisement on each of these organizations' `<org>/.github` repositories:

`StegVerse-org`, `StegVerse-Labs`, `SV-LLM`, `SV-011`, `GCAT-BCAT-Engine`, `Admissible-Existence`, `StegVerse-002`, `StegGhost`.

An advertisement is an overlay binding whose `profile_id` is `intr-destination`, and a service row whose `service_id` is `<slug>.<profile_id>`. Slug is the organization kernel's slug (`organization_slug`). `org-boundary/registry/federation.json` is not a peer source and is not read. The hop matrix is every ordered pair. A peer does not send a diagnostic to itself.

An organization whose advertisement cannot be read stays in that matrix. Every hop where it is sender or destination is `UNREACHABLE`. It is not dropped because one machine could not clone the repository.

Routing and governance are out of scope. A disposition on this lane is transition evidence. Authority is the constraint `NONE`. Time is the constraint `SUPPLIED_HB_EPOCH` (a supplied heartbeat epoch, not a clock reading).

## What one hop checks

1. Emit a manifested `ecosystem.communication` whose body schema is `stegverse.org-intr-destination-diagnostic/v1`. The manifest sits in that body, so the payload digest binds it.
2. Resolve the destination from the advertisement: `<destination-slug>.intr-destination`.
3. Close on the responded request class (`ecosystem.communication`, acknowledged as `ecosystem.communication.ack`) and the hop's `communication_id`.
4. Read both ledgers back. The sender must hold an egress emission and a closure. The destination must hold an ingress repository receipt and the organization receipt that consumes it. The hash chain must verify, the communication id must match, and the chains must not contain a duplicate or an orphan receipt.

## Fabricated mode

CI default. Mesh and ledger roots are temporary directories.

The far side is `kernel.receipt` / `build_control_response` from the merged organization contract. It is labeled non-authentic. It is not a live peer, and the lane does not claim those receipts were read from `refs/stegverse/organization-ledger`.

Peer checkouts supply advertisements. The hop runs on a temporary copy of the merged `StegVerse-org/.github` ledger and kernel contract, with that peer's organization identity stamped onto the copy. In-flight ledger writers in other organizations are not imported.

```bash
python -m stegverse.intr_destination_hop_lane \
  --mode fabricated \
  --reference-root /path/to/StegVerse-org/.github \
  --org-root /path/to/StegVerse-org/.github \
  --org-root /path/to/StegVerse-Labs/.github \
  --org-root /path/to/SV-LLM/.github \
  --org-root /path/to/Admissible-Existence/.github \
  --out-dir /tmp/intr-hop-lane
```

After `pip install -e .` the same entry point is `stegverse-intr-hop-lane`.

Outputs:

- `/tmp/intr-hop-lane/intr-destination-hop-lane.md` — matrix and one block per hop
- `/tmp/intr-hop-lane/intr-destination-hop-lane.json` — the same report (`stegverse.sdk.intr-destination-hop-lane/v1`)

Exit status is 0 only when every hop is `PASS`.

## Live mode

`workflow_dispatch` only. This mode does not append. It discovers the eight organizations above at run time:

- `GET https://api.github.com/repos/<org>/.github/contents/org-runtime/interlock-intr.json`
- `GET https://api.github.com/repos/<org>/.github/contents/org-boundary/registry/services.json`

Public repositories are read with no credential. When `FEDERATION_READ_TOKEN` is set, that value is sent as a bearer token so a private `<org>/.github` can be read. The token is optional. It is not written into the report. The workflow passes the repository secret `FEDERATION_READ_TOKEN` into the live job; leave the secret unset to read public repositories only.

For each organization whose advertisement was read, the lane then reads `refs/stegverse/organization-ledger` (and the repository-ledger namespace named by that organization's contract, when the contract was read). A local `--org-root` whose slug matches a read advertisement is used as that ledger checkout. Otherwise `--fetch-ledger-refs` fetches the ref from `https://github.com/<org>/.github`.

```bash
# Public advertisements, no token.
python -m stegverse.intr_destination_hop_lane \
  --mode live \
  --fetch-ledger-refs \
  --out-dir /tmp/intr-hop-lane-live

# Include private repositories the token can read.
FEDERATION_READ_TOKEN="$FEDERATION_READ_TOKEN" \
  python -m stegverse.intr_destination_hop_lane \
  --mode live \
  --fetch-ledger-refs \
  --out-dir /tmp/intr-hop-lane-live
```

| Status | Meaning |
| --- | --- |
| `PASS` | Both ledgers were read, the chains verify, and this ordered pair has one correlated egress emission, closure, and destination ingress for the same `communication_id`. Authenticity is claimed only for that read-back. |
| `FAIL` | A ledger was read and the chain or the correlation does not hold. |
| `UNREACHABLE` | An advertisement could not be read, or a ledger ref could not be read, or the ref has no head. The hop stays in the matrix and the lane continues. |

Exit status is 0 when no hop is `FAIL`. `UNREACHABLE` is a reported gap, not a crash, and not a reason to remove the organization from the peer set. A missing advertisement or ledger is not described as a verified receipt.

## CI

`.github/workflows/intr-destination-hop-lane.yml` runs fabricated mode on pull requests. That job uses the organization checkouts it was given. Live mode is the separate `workflow_dispatch`-only workflow `.github/workflows/intr-destination-hop-lane-live.yml` and is not run by pull requests. The live job queries all eight organizations through the GitHub API and passes `FEDERATION_READ_TOKEN` when that secret is configured.
