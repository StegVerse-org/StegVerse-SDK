from stegverse.interlock_return import canonical_hash as return_hash, validate_interlock_return
from stegverse.interlock_transition import canonical_hash as ingress_hash, validate_interlock_transition
from stegverse.reference_interlock_participant import (
    acknowledge_interlock_return,
    build_reference_interlock_ingress,
    issue_reference_receipt,
)

H1 = "sha256:" + "1" * 64
H2 = "sha256:" + "2" * 64
H3 = "sha256:" + "3" * 64
H4 = "sha256:" + "4" * 64


def _terminal_receipt():
    return issue_reference_receipt(
        participant_id="external-framework.example",
        state_id="external:s17",
        state_hash=H1,
    )


def _ingress():
    return build_reference_interlock_ingress(
        participant_receipt=_terminal_receipt(),
        package_id="pkg-reference-001",
        transition_id="tx-reference-001",
        run_id="run-reference-001",
        governance_mode="DEFAULT_STEGVERSE",
        governance_profiles=[{
            "profile_id": "stegverse.default.reference.v1",
            "issuer": "StegVerse",
            "profile_hash": H2,
            "source": "STEGVERSE",
        }],
    )


def _pending_return():
    ingress = _ingress()
    egress_manifest_hash = H3
    return {
        "schema": "stegverse.interlock-return.v1",
        "package_id": ingress["package_id"],
        "transition_id": ingress["transition_id"],
        "run_id": ingress["run_id"],
        "participant_id": ingress["connection"]["participant_id"],
        "binding": {
            "ingress_interlock_hash": ingress_hash(ingress),
            "governance_record_hash": H4,
            "material_causal_closure_hash": H2,
        },
        "egress": {
            "manifest_hash": egress_manifest_hash,
            "governed_state_hash": H4,
            "receipts": [{
                "receipt_id": "stegverse:r900",
                "issuer": "StegVerse",
                "receipt_hash": H3,
            }],
        },
        "acknowledgement": {
            "state": "PENDING",
            "received_egress_receipt_hash": None,
            "participant_binding_hash": None,
            "participant_successor_receipts": [],
        },
        "relationships": [],
        "reconstruction": {
            "required": True,
            "replay_scope": "MATERIAL_CAUSAL_CLOSURE",
            "egress_manifest_hash": egress_manifest_hash,
        },
        "authority": {
            "sdk_authority": "NONE",
            "participant_truth_assumed": False,
            "return_transfers_authority": False,
            "master_records_custody_claimed": False,
            "execution_authorized": False,
        },
    }


def test_reference_terminal_receipt_is_deterministic():
    left = _terminal_receipt()
    right = _terminal_receipt()
    assert left == right
    assert left["issuer"] == "external-framework.example"
    assert left["authority"]["stegverse_authority_transferred"] is False


def test_reference_ingress_uses_public_interlock_contract():
    ingress = _ingress()
    assert validate_interlock_transition(ingress) == ingress
    terminal = _terminal_receipt()
    assert ingress["connection"]["participant_boundary_receipt_hash"] == terminal["receipt_hash"]
    assert ingress["manifest"]["predecessor_receipts"][0]["receipt_hash"] == terminal["receipt_hash"]
    assert ingress["connection"]["class"] == "INTERLOCK"


def test_reference_participant_binds_return_into_successor_receipt():
    pending = _pending_return()
    assert validate_interlock_return(pending) == pending
    result = acknowledge_interlock_return(
        pending,
        successor_state_id="external:s18",
        successor_state_hash=H1,
    )
    resolved = result["return_record"]
    successor = result["participant_successor_receipt"]
    assert validate_interlock_return(resolved) == resolved
    assert resolved["acknowledgement"]["state"] == "ACKNOWLEDGED"
    assert H3 in successor["predecessor_receipt_hashes"]
    assert resolved["relationships"][0]["to_receipt_hash"] == successor["receipt_hash"]


def test_return_acknowledgement_changes_return_record_hash():
    pending = _pending_return()
    resolved = acknowledge_interlock_return(
        pending,
        successor_state_id="external:s18",
        successor_state_hash=H1,
    )["return_record"]
    assert return_hash(pending) != return_hash(resolved)
