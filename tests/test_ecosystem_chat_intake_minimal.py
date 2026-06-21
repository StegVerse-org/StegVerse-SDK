from stegverse.ecosystem_chat_intake import validate_ecosystem_chat_payload


def payload():
    return {
        "fields": {
            "target_entry_point": "StegVerse-org/SDK",
            "input_mode": "text_form",
            "requested_route": "Site",
            "receipt_expectation": "sdk_intake_receipt_requested",
            "submission_posture": "ready_for_submission",
            "user_request": "continue building Site",
            "declared_goal": "text-only ecosystem command console",
            "operator_note": "",
        },
        "manifest": {
            "target_entry_point": "StegVerse-org/SDK",
            "input_mode": "text_form",
            "requested_route": "Site",
            "user_request": "continue building Site",
            "declared_goal": "text-only ecosystem command console",
            "operator_note": "",
            "source_surface": "StegVerse-Labs/Site/ecosystem-chat.html",
        },
        "receipt_window": {
            "receipt_expectation": "sdk_intake_receipt_requested",
            "submission_posture": "ready_for_submission",
            "site_receipt_authority": False,
            "manifest_correct_at_submission": True,
            "submission_target": "StegVerse-org/SDK",
            "correctness_errors": [],
        },
    }


def test_valid_payload_is_accepted_without_receipt_id():
    result = validate_ecosystem_chat_payload(payload()).to_dict()
    assert result["accepted"] is True
    assert result["routed_module"] == "Site"
    assert result["receipt_id"] is None
    assert result["errors"] == []


def test_changed_manifest_route_is_rejected():
    data = payload()
    data["manifest"]["requested_route"] = "Continuity"
    result = validate_ecosystem_chat_payload(data).to_dict()
    assert result["accepted"] is False
    assert result["receipt_id"] is None
    assert result["errors"]
