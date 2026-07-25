import pytest

from stegverse.review_authority import (
    ReviewAuthorityError,
    authorize_transition,
    build_acknowledgement_receipt,
    validate_review_manifest,
)


def manifest():
    return {
        "schema_version": "1.0.0",
        "artifact_id": "manifest-receipt-boundary",
        "artifact_version": "0.3",
        "visibility_state": "PUBLICLY_VISIBLE",
        "process_state": "REVIEW_ONLY",
        "claim_authority": False,
        "publication_authority": False,
        "attribution_authority": False,
        "public_association_authority": False,
        "endorsement": "NONE",
        "compatibility": "NONE",
        "interoperability": "NONE",
        "external_references": [
            {"name": "GLM", "association_status": "REFERENCE_ONLY"},
            {"name": "EVIDE", "association_status": "REFERENCE_ONLY"},
        ],
    }


def test_public_visibility_does_not_grant_authority():
    validated = validate_review_manifest(manifest())
    assert validated["visibility_state"] == "PUBLICLY_VISIBLE"
    assert validated["publication_authority"] is False
    assert validated["attribution_authority"] is False
    assert len(validated["manifest_sha256"]) == 64


def test_review_only_claim_inference_fails_closed():
    value = manifest()
    value["interoperability"] = "ASSERTED"
    with pytest.raises(ReviewAuthorityError, match="review-only"):
        validate_review_manifest(value)


def test_visibility_cannot_be_authority_source():
    value = manifest()
    value["authority_source"] = "VISIBILITY"
    with pytest.raises(ReviewAuthorityError, match="visibility"):
        validate_review_manifest(value)


def test_external_association_requires_explicit_authority():
    value = manifest()
    value["external_references"][0]["association_status"] = "AUTHORIZED_ASSOCIATION"
    with pytest.raises(ReviewAuthorityError, match="public_association_authority"):
        validate_review_manifest(value)


def test_acknowledgement_is_not_endorsement_or_attribution():
    receipt = build_acknowledgement_receipt(manifest(), reviewer_id="reviewer-001")
    assert receipt["acknowledgement"] == "UNDERSTOOD_NOT_ENDORSED"
    assert receipt["authority_granted"] is False
    assert receipt["endorsement_granted"] is False
    assert receipt["attribution_granted"] is False
    assert receipt["public_association_granted"] is False
    assert len(receipt["receipt_sha256"]) == 64


def test_transition_requires_declared_authorizer_authority():
    request = {
        "transition_id": "transition-001",
        "target_process_state": "ADOPTED",
        "authorizer_id": "owner-001",
        "authorizer_authority_ref": "delegation:artifact-owner-v1",
        "requested_authorities": {
            "claim_authority": True,
            "publication_authority": True,
            "attribution_authority": False,
            "public_association_authority": False,
        },
    }
    result = authorize_transition(manifest(), request)
    assert result["manifest"]["process_state"] == "ADOPTED"
    assert result["manifest"]["publication_authority"] is True
    assert result["receipt"]["visibility_was_authority_source"] is False
    assert result["receipt"]["decision"] == "ALLOW"


def test_transition_fails_without_complete_authority_dimensions():
    request = {
        "transition_id": "transition-002",
        "target_process_state": "ADOPTED",
        "authorizer_id": "owner-001",
        "authorizer_authority_ref": "delegation:artifact-owner-v1",
        "requested_authorities": {"publication_authority": True},
    }
    with pytest.raises(ReviewAuthorityError, match="all authority dimensions"):
        authorize_transition(manifest(), request)


def test_supplied_manifest_hash_is_verified():
    value = validate_review_manifest(manifest())
    value["artifact_version"] = "tampered"
    with pytest.raises(ReviewAuthorityError, match="hash mismatch"):
        validate_review_manifest(value)
