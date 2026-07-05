from stegverse.ai_entry_receipt_capture import preview_ai_entry_receipt_capture


def test_ai_entry_receipt_capture_is_preview_only():
    preview = preview_ai_entry_receipt_capture(
        user_input="How do I access the SDK?",
        route_id="sdk_access_guidance",
        response_id="preview-sdk-access-guidance",
    )
    assert preview.preview_only is True
    assert preview.receipt_capture_enabled is False
    assert preview.real_receipt_issued is False
    assert preview.master_record_persisted is False
    assert preview.execution_authority_granted is False
    assert preview.credential_surface_enabled is False


def test_ai_entry_receipt_capture_preserves_route_and_hash():
    preview = preview_ai_entry_receipt_capture(
        user_input="Compare StegVerse with Claude",
        route_id="llm_comparison",
        response_id="preview-llm-comparison",
    )
    assert preview.schema_version == "stegverse.sdk.ai_entry_receipt_capture.v0.1"
    assert len(preview.input_hash) == 64
    assert preview.route_id == "llm_comparison"
    assert preview.response_id == "preview-llm-comparison"
    assert preview.reconstruction_metadata_required is True
