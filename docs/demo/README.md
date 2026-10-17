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

Public repositories are read with no credential. When `FEDERATION_READ_TOKEN` is set, that value is sent as a bearer token so a private `<org>/.github` can be read. When it is unset, reads fall back to `FEDERATION_HOP_TOKEN`. The token is optional. It is not written into the report. The workflow passes the repository secret `FEDERATION_READ_TOKEN` into the live job; leave the secret unset to read public repositories only.

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
| `DURABLE_QUEUE_OR_EVENT_EPHEMERAL_MATERIALIZATION` | The sender recorded the emission and no closure is in the read ledgers yet. `always_on_receiver_required: false`; not a failure. |

`FAIL` and `UNREACHABLE` carry the six non-ALLOW fields.

### Ledger integrity: LEGACY and duplicates

History is not rewritten. Each organization's ledger is classified against its **writer introduction**: the earliest default-branch commit whose `.github/workflows/organization-ledger-transition.yml` takes `hb_epoch` as a dispatch input and runs the self-closure. It is read from the local checkout's history, or from the GitHub API (`commits?path=` and `contents?ref=`). `--writer-introduced ORG=<unix seconds | ISO 8601>` overrides it, and `--no-writer-lookup` turns the lookup off.

A receipt is `LEGACY` when the ledger-ref commit that added it is older than the writer introduction. The full ref history is fetched so that commit can be found. These findings on legacy receipts are reported under **Ledger integrity**, and they do not fail the lane:

- orphan
- duplicate
- source mismatch
- clock-derived time
- authority-effect

Repository receipts that repeat one `transition_id` with identical evidence are reported as `IDENTICAL_DUPLICATE_REPOSITORY_RECEIPT`. Divergent duplicates fail unless every copy is legacy. An organization receipt that names no source receipt is reported, and is not compared against a source copy. Chain-shape findings always fail: missing receipts, broken links, and bodies that do not verify.

## Orchestrate mode

`workflow_dispatch` only, and run only on Rigel's go. It needs `FEDERATION_HOP_TOKEN`, and it needs `intr-destination-hop.yml` on `main` in all eight organizations.

```bash
FEDERATION_HOP_TOKEN="$FEDERATION_HOP_TOKEN" \
  python -m stegverse.intr_destination_hop_lane \
  --mode orchestrate \
  --hb-epoch 40000 \
  --out-dir /tmp/intr-hop-lane-orchestrate
```

**Manifest-directed, no waiting.** One orchestrate run is one transition. It first reads every organization ledger (the live readback) and derives each ordered pair's ledger state: `CLOSED`, `REFUSED`, `OPEN` (sent, not yet closed) or `UNSENT`. It then records one disposition per pair. An `UNSENT` pair whose sender and destination hold no open hop, and are not already in a hop dispatched by this run, is dispatched. Every ledger writer in an organization shares the `organization-ledger` concurrency group, and GitHub cancels a second pending run in a group, so no organization appears in two dispatched hops. A later run, at a later supplied `--hb-epoch`, selects the next hops from ledger state.

**One hop.** A hop dispatched at epoch `E` has communication id `intr-hop:<sender>:<destination>:<E>`:

1. The lane dispatches the sender's `phase=send`. It records `ORGANIZATION_EGRESS_EMITTED` at `E`.
2. The destination's own `intr-destination` ingress records `ORGANIZATION_INTR_DESTINATION_INGRESS` at `E+1`.
3. The sender records `ORGANIZATION_EGRESS_CLOSED` at `E+2`, only for the responded request class.

**Dispositions.** A dispatched or `OPEN` hop is `DURABLE_QUEUE_OR_EVENT_EPHEMERAL_MATERIALIZATION` with `always_on_receiver_required: false`: the destination's receive and the sender's close materialize from the dispatched events, and the next readback evaluates whatever receipts exist then. Nothing polls, sleeps or times out. Every non-ALLOW outcome (`UNREACHABLE`, `NOT_DISPATCHED`, `FAIL`, `CLOSURE_REFUSED`, `DEFERRED_ORGANIZATION_LEDGER_CONCURRENCY`) carries `failure_code`, `failed_predicate`, `required_evidence_or_repair`, `retry_entrypoint`, `owning_existing_goal` (StegVerse-Labs/.github#2897 / StegVerse-org/.github#162 P0-runtime-and-custody) and `next_attempt`. Exit status is 1 when a dispatch was not accepted, or a hop is `FAIL` for a reason other than not yet being sent.

The credential path is a pending owner decision: TV/TVC least-privilege issuance per StegVerse-Labs/.github#2897.

Exit status is 0 when no hop is `FAIL`. `UNREACHABLE` is a reported gap, not a crash, and not a reason to remove the organization from the peer set. A missing advertisement or ledger is not described as a verified receipt.

## CI

`.github/workflows/intr-destination-hop-lane.yml` runs fabricated mode on pull requests. That job uses the organization checkouts it was given. Live mode is a `workflow_dispatch` input and is not run by pull requests. The live job queries all eight organizations through the GitHub API and passes `FEDERATION_READ_TOKEN` when that secret is configured. Orchestrate mode is a separate `workflow_dispatch` input (`mode=orchestrate`, `hb_epoch`), and it fails closed without `FEDERATION_HOP_TOKEN`. Pull requests never dispatch a hop.
