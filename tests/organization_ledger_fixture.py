"""Organization-ledger readback fixture shared by SDK-MR-A tests (#452).

The shape is what StegVerse-org/.github resident-runtime/organization_ledger_readback.py
emits with --ingress-result. It is test input only; nothing here is a receipt.
"""
import hashlib
import json

READBACK_SCHEMA = "stegverse.organization-ledger-readback/v1"
MANIFEST = "a" * 64
OTHER_MANIFEST = "b" * 64


def _sha(value):
    body = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(body).hexdigest()


def _readback(*, refused=False):
    # Shape emitted by StegVerse-org/.github resident-runtime/organization_ledger_readback.py
    # with --ingress-result: a two-receipt chain whose tip binds the submitted manifest.
    genesis = {"receipt_sha256": _sha("genesis"), "previous_receipt_sha256": None,
               "source_transition_id": "t-0", "predecessor_org_state_sha256": _sha("s0"),
               "successor_org_state_sha256": _sha("s1")}
    tip = {"receipt_sha256": _sha("tip"), "previous_receipt_sha256": genesis["receipt_sha256"],
           "source_transition_id": "t-1", "predecessor_org_state_sha256": "sha256:" + MANIFEST,
           "successor_org_state_sha256": _sha("s2")}
    return {
        "schema": READBACK_SCHEMA,
        "location": "git+StegVerse-org/.github#refs/stegverse/organization-ledger",
        "disposition": "ALLOW",
        "head_receipt_sha256": tip["receipt_sha256"],
        "chain_length": 2,
        "genesis_receipt_sha256": genesis["receipt_sha256"],
        "chain": [genesis, tip],
        "every_receipt_verifies_against_its_body": True,
        "every_source_receipt_retained_and_verifies": True,
        "authority_effect": "NONE_READBACK_ONLY",
        "ingress_disposition": "DENY" if refused else "ALLOW",
        "ingress_refused": refused,
        "ingress_organization_receipt_sha256": tip["receipt_sha256"],
        "ingress_receipt_in_chain": True,
        "ingress_receipt_bound_to_manifest": True,
        "canonical_manifest_sha256": MANIFEST,
        "organization_transition_id": "org-transition-1",
        "master_records_awaited": False,
    }
