import hashlib, json
from stegverse.admittedcode_receipt import verify_admittedcode_receipt


def _receipt(decision="ALLOW", key_requested=False):
    body = {
        "schema": "stegverse.provider_harness_receipt.v1",
        "timestamp_utc": "2026-08-07T00:00:00Z",
        "mode": "mock",
        "decision": decision,
        "key_requested": key_requested,
        "replay": {"hit": False},
        "provider": "fixture-provider",
        "model": "fixture-model-v1",
        "purpose": "governed_demo_response",
        "input_state_hash": "sha256:NO_REPO",
        "gates": [{"gate":"consent","decision":"PASS","detail":"fixture"}],
        "enforcement": {"manager":"adapter-bound","note":"fixture"},
        "scope": {"asserts":["reviewed"],"does_not_assert":["execution authority"]},
        "canonicalization": {"method":"stegverse.jcs.v1","hash":"sha256"}
    }
    raw = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    body["receipt_id"] = "sha256:" + hashlib.sha256(raw).hexdigest()
    body["authority_effect"] = "NONE"
    return body


def test_accepts_portable_allow_without_granting_authority():
    result = verify_admittedcode_receipt(_receipt())
    assert result["status"] == "ACCEPTED"
    assert result["decision"] == "ALLOW"
    assert result["sdk_validation_is_execution"] is False
    assert result["sdk_intake_is_authority"] is False
    assert result["receipt_handoff_is_master_record_installation"] is False


def test_rejects_authority_escalation():
    receipt = _receipt(); receipt["authority_effect"] = "EXECUTION"
    assert verify_admittedcode_receipt(receipt)["reason"] == "authority_escalation"


def test_rejects_refusal_that_reached_key():
    receipt = _receipt("DENY", True)
    assert verify_admittedcode_receipt(receipt)["reason"] == "refusal_reached_key"


def test_rejects_tampered_receipt():
    receipt = _receipt(); receipt["purpose"] = "tampered"
    assert verify_admittedcode_receipt(receipt)["reason"] == "receipt_hash_mismatch"
