from stegverse.proof_release_gate import (
    PROOF_CAPABILITY_SCHEMA,
    REQUIRED_POST_RETURN_CAPABILITIES,
    verify_release_proof_capabilities,
)


def _receipt():
    components = [
        {"repository": "StegVerse-org/StegVerse-SDK", "commit_sha": "1" * 40},
        {"repository": "StegVerse-Labs/StegCore", "commit_sha": "2" * 40},
        {"repository": "master-records/orchestration", "commit_sha": "3" * 40},
    ]
    repository_for = {
        "SDK_POST_RETURN_EVIDENCE_V1": "StegVerse-org/StegVerse-SDK",
        "STEGCORE_SPE_STANDING_BINDING_V1": "StegVerse-Labs/StegCore",
        "MASTER_RECORDS_OPERATION_CUSTODY_V1": "master-records/orchestration",
    }
    release_commit_for = {component["repository"]: component["commit_sha"] for component in components}
    capabilities = []
    for index, capability_id in enumerate(REQUIRED_POST_RETURN_CAPABILITIES, start=4):
        repository = repository_for[capability_id]
        capabilities.append(
            {
                "schema": PROOF_CAPABILITY_SCHEMA,
                "capability_id": capability_id,
                "repository": repository,
                "release_commit_sha": release_commit_for[repository],
                "feature_commit_sha": str(index) * 40,
                "feature_in_release_commit": True,
                "containment_verification": "ANCESTOR_OR_EQUAL",
                "authority_effect": "NONE",
            }
        )
    return {"components": components, "proof_capabilities": capabilities}


def test_release_with_exact_capability_bindings_passes():
    result = verify_release_proof_capabilities(_receipt())
    assert result["verified"] is True
    assert result["authority_effect"] == "NONE"
    assert result["observed"] == sorted(REQUIRED_POST_RETURN_CAPABILITIES)


def test_historical_release_without_proof_capabilities_fails_closed():
    result = verify_release_proof_capabilities({"components": []})
    assert result["verified"] is False
    assert result["reason"] == "proof_capabilities_missing"


def test_release_component_commit_mismatch_fails_closed():
    receipt = _receipt()
    receipt["proof_capabilities"][0]["release_commit_sha"] = "9" * 40
    result = verify_release_proof_capabilities(receipt)
    assert result["verified"] is False
    assert "SDK_POST_RETURN_EVIDENCE_V1:release_commit_mismatch" in result["reasons"]


def test_release_cannot_claim_feature_without_containment_verification():
    receipt = _receipt()
    receipt["proof_capabilities"][1]["feature_in_release_commit"] = False
    result = verify_release_proof_capabilities(receipt)
    assert result["verified"] is False
    assert "STEGCORE_SPE_STANDING_BINDING_V1:feature_not_in_release" in result["reasons"]
