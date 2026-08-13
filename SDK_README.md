# STEGVERSE SDK

This legacy filename is retained for compatibility with older links.

Canonical documentation:

- `README.md` — current public overview and custody-backed governed TEST quick start
- `docs/SDK_CONSOLE.md` — console/navigation and operational replay/reconstruction reference
- `docs/PUBLIC_INSPECTION_ENTRY.md` — public inspection request and governed TEST instructions
- `docs/PUBLIC_INSPECTION_CUSTODY_REPLAY_MIRROR_HANDOFF.md` — current scoped implementation state
- `SDK_MIRROR_HANDOFF.md` — repository source of truth

Do not use historical examples from older revisions as the current SDK contract.

For an actual governed TEST using canonical StegCore, Python 3.11+, an admitted Master Records endpoint is required:

```bash
export MASTER_RECORDS_URL="<admitted-master-records-base-url>"
export MASTER_RECORDS_AUTH_TOKEN="<authorized-token>"
python -m pip install -e ".[dev,governed-test]"
python -m stegverse.public_inspection_runtime run inspection/examples/governed-test-request.json
```

A governed run is not reported successful until Master Records confirms `custody_status: RECORDED`.

Operational replay and reconstruction:

```bash
python -m stegverse.public_inspection_runtime replay MR-<SHA256>
python -m stegverse.public_inspection_runtime reconstruct MR-<SHA256>
```

Both are read-only and do not re-execute a consequence or mutate the retained Master Record.
