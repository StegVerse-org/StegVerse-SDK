from stegverse.release_dependency_alignment import verify_governed_test_dependency_alignment


REQUIREMENTS = [
    'stegcore @ git+https://github.com/StegVerse-Labs/StegCore.git@083557adec1bdbace09ebd10fb0765eb8e9a9d08 ; extra == "governed-test"',
    'stegverse-core-lite @ git+https://github.com/Data-Continuation/core-lite.git@72bdb0f110031ccc2cd98b8ebb7c22b1ab7326f8 ; extra == "governed-test"',
    'stegverse-master-records @ git+https://github.com/master-records/orchestration.git@6626c6a7f1df6bf531940c165b2f4db374e08b92 ; extra == "governed-test"',
]


def _receipt(stegcore_commit="083557adec1bdbace09ebd10fb0765eb8e9a9d08"):
    return {
        "components": [
            {
                "repository": "StegVerse-Labs/StegCore",
                "commit_sha": "1" * 40,
                "source_parent_commit": stegcore_commit,
            },
            {
                "repository": "Data-Continuation/core-lite",
                "commit_sha": "2" * 40,
                "source_parent_commit": "72bdb0f110031ccc2cd98b8ebb7c22b1ab7326f8",
            },
            {
                "repository": "master-records/orchestration",
                "commit_sha": "3" * 40,
                "source_parent_commit": "6626c6a7f1df6bf531940c165b2f4db374e08b92",
            },
        ]
    }


def test_historical_pins_align_to_historical_executable_coordinates():
    result = verify_governed_test_dependency_alignment(REQUIREMENTS, _receipt())
    assert result["verified"] is True
    assert result["reasons"] == ["ok"]
    assert all(item["aligned"] is True for item in result["observations"])


def test_successor_receipt_rejects_old_stegcore_pin():
    result = verify_governed_test_dependency_alignment(
        REQUIREMENTS,
        _receipt("f09eb36abcd3b317f35638e5c0b0c4a802d0aecf"),
    )
    assert result["verified"] is False
    assert "stegcore:commit_mismatch" in result["reasons"]
    assert result["authority_effect"] == "NONE"


def test_missing_release_component_fails_closed():
    receipt = _receipt()
    receipt["components"] = [
        item for item in receipt["components"] if item["repository"] != "master-records/orchestration"
    ]
    result = verify_governed_test_dependency_alignment(REQUIREMENTS, receipt)
    assert result["verified"] is False
    assert "stegverse-master-records:release_component_missing" in result["reasons"]
