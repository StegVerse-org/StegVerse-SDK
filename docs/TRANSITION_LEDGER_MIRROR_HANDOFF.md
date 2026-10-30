# Transition Ledger Mirror Handoff

Repository: `StegVerse-org/StegVerse-SDK`

Every durable transition owned here is recorded first in this repository ledger. Repo replay/reconstruction must terminate without org/ecosystem replay.

Contract: `.stegverse/transition-ledger/contract.json`  
Emitter: `.stegverse/transition-ledger/emit.py`  
Durable root: `$XDG_STATE_HOME/stegverse/repo-ledgers/StegVerse-org/StegVerse-SDK`

Receipts are append-only/hash-linked. Only evidence needed for organization reconstruction propagates to `StegVerse-org/.github`. Recording grants no authority.

## Durable location and initialization (draft, Lane C)

The local `$XDG_STATE_HOME` root above lives on one host only, so a readback of
the sovereign ledger finds no SDK chain. StegVerse-org/.github
`organization_ledger_readback.repository_readback(..., "repository-ledger/StegVerse-org/StegVerse-SDK", ...)`
refuses with FAIL_CLOSED `REPOSITORY_LEDGER_HEAD_PRESENT`.

The contract now declares `repository_ledger_location` in the same subtree form
StegVerse-org/.github declares for its own chain:
`refs/stegverse/organization-ledger:repository-ledger/StegVerse-org/StegVerse-SDK`
on StegVerse-org/.github, with `new_ledger_root: false`. This is the same pattern
as StegVerse-Labs/TVC#525.

`scripts/initialize_repository_ledger.py` is the manifest-driven
REPOSITORY_LEDGER_INITIALIZATION transition. It applies
`.stegverse/transition-ledger/initialization-manifest.v1.json`, which is bound to
the observed organization ledger head `2acec0e1`.
- `plan` is read-only.
- `apply` writes the genesis receipt and `HEAD.json` as one commit on a **local**
  checkout, with compare-and-swap on the bound head, then reads them back.
- Rerunning with the same manifest is a NOOP ALLOW. An existing chain is never
  re-rooted, and remote locations are refused.
- Time comes from a supplied hb_epoch, and no clock is read. Every non-ALLOW
  carries the six fields.

Cross-check (local, offline): on a local copy of StegVerse-org/.github
`refs/stegverse/organization-ledger` at `2acec0e1`, StegVerse-org's own
`repository_readback` refuses `REPOSITORY_LEDGER_HEAD_PRESENT` before `apply`.
After `apply` it walks the 1-receipt chain with StegVerse-org's `emit.chain` and
refuses only `REPOSITORY_RECEIPT_RETAINED_IN_ORGANIZATION_LEDGER`, which is the
organization's own `source-receipts/` retention step.

### First initialization (FAIL_CLOSED, not performed by any lane)

| field | value |
|---|---|
| failure_code | `REPOSITORY_LEDGER_FIRST_INITIALIZATION_IS_AN_ORGANIZATION_LEDGER_APPEND` |
| failed_predicate | `REPOSITORY_LEDGER_HEAD_PRESENT` for `repository-ledger/StegVerse-org/StegVerse-SDK` on StegVerse-org/.github `refs/stegverse/organization-ledger` |
| required_evidence_or_repair | Run `apply` on the organization's materialized ledger checkout at the bound head. Then, in the same append under ORGANIZATION_LEDGER_LOCK, fast-forward push the ref and retain the genesis under `source-receipts/` with an organization receipt. The evidence is a fresh-fetch `repository_readback` ALLOW. |
| retry_entrypoint | `scripts/initialize_repository_ledger.py --mode apply`, then StegVerse-org/.github `.github/workflows/organization-ledger-transition.yml` |
| owning_existing_goal | ORGANIZATION-BATCH-CUSTODY-REPLAY-001 |
| next_attempt | Once this is on SDK main and the organization's ledger writer runs it. If the head moves first, re-bind `expected_organization_ledger_head`. |

## Recording an SDK push: `sv-push-receipt.v1`

A push to this repository is recorded on the ledger of the organization that owns it. StegVerse-SDK is in StegVerse-org, so its
`stegverse.sv_push_receipt.v1` belongs on the StegVerse-org ledger (StegVerse-org/.github `refs/stegverse/organization-ledger`), one per push
range `(repository, ref, old_sha, new_sha)`. Each organization keeps its own ledger. The producer and the writer operation live in
StegVerse-org/.github (`resident-runtime/sv_push_receipt.py` and the `sv_push_receipt` operation of its organization-ledger writer,
declared in `.stegverse/organization-ledger-ingest/operations.json`); the SDK has no copy of either, and nothing in this repository appends,
dispatches or polls. What an SDK contributor does:

1. Before pushing a branch, read the ref value it will move from. For a new branch that is the fork base on `origin/main`
   (`resident-runtime/sv_push_receipt.py read-ref --repository . --ref refs/remotes/origin/main`, run from a StegVerse-org/.github checkout
   against this clone).
2. Push with the session's own normal push.
3. After the push, fetch the branch and run `sv_push_receipt.py emit --repository <this clone> --repository-name StegVerse-org/StegVerse-SDK
   --ref refs/heads/<branch> --after-ref refs/remotes/origin/<branch> --old-sha <step 1> --pusher-session <session> --hb-epoch <supplied> --out receipt.json`.
   `hb_epoch` is supplied (ASCII digits >= 32), never read from a clock. A force-push is refused, not receipted.
4. The receipt is committed to StegVerse-org/.github as `.stegverse/organization-ledger-ingest/request.json`
   (`{"schema":"stegverse.organization-ledger-ingest-request/v1","operation":"sv_push_receipt","push_receipt":{...},"hb_epoch":<supplied>}`).
   The organization-ledger writer appends it when that file changes on a push to StegVerse-org/.github `main`; one request holds one receipt.
   A second receipt for the same range is refused with the six fields (`SV_PUSH_RECEIPT_RANGE_ALREADY_RECORDED`) and appends nothing.
5. Read it back from a fresh fetch of `refs/stegverse/organization-ledger`: the repository receipt under
   `repository-ledger/StegVerse-org/StegVerse-SDK` and the organization receipt that retains it.

An SDK push receipt written to the StegVerse-Labs ledger is on the wrong ledger and is not authoritative for LC-GOV-07. It is left in place
(deleting stored ledger data needs the owner) and is not repeated here.

Past ranges are not reconstructed: SDK#567 (`6b3ccee2`) and the other merges that pre-date the operation have no push receipt and stay
`BRANCH_WRITER_UNOBSERVED`. A receipt records the range its session declared; it grants no authority.
