# InTr destination hop lane

A diagnostic of one-way InTr integrity and organization-ledger receipt integrity. It is also the SDK test lane that CI runs in fabricated mode.

The lane discovers peers from each checkout's own advertisement: an overlay binding whose `profile_id` is `intr-destination`, and a service row whose `service_id` is `<slug>.<profile_id>`. Slug is the organization kernel's slug (`organization_slug`). `org-boundary/registry/federation.json` is not a peer source and is not read. The hop matrix is every ordered pair of discovered peers. A peer does not send a diagnostic to itself.

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

`workflow_dispatch` only. This mode does not append. It reads `refs/stegverse/organization-ledger` on each peer checkout (and the repository-ledger namespace named by that checkout's merged contract, when the file is present).

```bash
python -m stegverse.intr_destination_hop_lane \
  --mode live \
  --fetch-ledger-refs \
  --org-root /path/to/each/.github \
  --out-dir /tmp/intr-hop-lane-live
```

| Status | Meaning |
| --- | --- |
| `PASS` | Both ledgers were read, the chains verify, and this ordered pair has one correlated egress emission, closure, and destination ingress for the same `communication_id`. Authenticity is claimed only for that read-back. |
| `FAIL` | A ledger was read and the chain or the correlation does not hold. |
| `UNREACHABLE` | A peer has no ledger ref, or the ref has no head. The hop is reported and the lane continues. |

Exit status is 0 when no hop is `FAIL`. `UNREACHABLE` is a reported gap, not a crash. A missing ledger is not described as a verified receipt.

## CI

`.github/workflows/intr-destination-hop-lane.yml` checks out the organization repositories it can read, discovers peers from those advertisements, and runs fabricated mode. A repository that cannot be read is listed on the report as an advertisement that was not readable. It is not added to the peer set. Live mode is a `workflow_dispatch` input and is not run by pull requests.
