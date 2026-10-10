from stegverse.release_dependency_alignment import verify_governed_test_dependency_alignment


STEGCORE_TVC_SOURCE_PARENT = "ef38410505b0ef3e84148892b1d6e3cdef20f300"
CORE_LITE_TVC_SOURCE_PARENT = "72bdb0f110031ccc2cd98b8ebb7c22b1ab7326f8"
PRE_TVC_STEGCORE_PROOF_SOURCE = "124ea6b53ff79db8f514cacf1aab295f03cacf74"
# Formerly pinned run-store package; the SDK now keeps its own local run record
# (stegverse.local_run_record), so this pin is no longer expected.
REMOVED_RUN_STORE_PIN = (
    'stegverse-master-records @ git+https://github.com/master-records/orchestration.git@'
    '03312236c115bc814024d700810391340648601f ; extra == "governed-test"'
)

REQUIREMENTS = [
    f'stegcore @ git+https://github.com/StegVerse-Labs/StegCore.git@{STEGCORE_TVC_SOURCE_PARENT} ; extra == "governed-test"',
    f'stegverse-core-lite @ git+https://github.com/Data-Continuation/core-lite.git@{CORE_LITE_TVC_SOURCE_PARENT} ; extra == "governed-test"',
]


def _receipt(stegcore_commit=STEGCORE_TVC_SOURCE_PARENT):
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
                "source_parent_commit": CORE_LITE_TVC_SOURCE_PARENT,
            },
        ]
    }


def test_final_tvc_source_parent_pins_align():
    result = verify_governed_test_dependency_alignment(REQUIREMENTS, _receipt())
    assert result["verified"] is True
    assert result["reasons"] == ["ok"]
    assert all(item["aligned"] is True for item in result["observations"])


def test_pre_tvc_stegcore_proof_source_is_rejected_for_final_receipt():
    result = verify_governed_test_dependency_alignment(
        REQUIREMENTS,
        _receipt(stegcore_commit=PRE_TVC_STEGCORE_PROOF_SOURCE),
    )
    assert result["verified"] is False
    assert "stegcore:commit_mismatch" in result["reasons"]
    assert result["authority_effect"] == "NONE"


def test_removed_run_store_pin_is_rejected_as_unexpected():
    result = verify_governed_test_dependency_alignment([*REQUIREMENTS, REMOVED_RUN_STORE_PIN], _receipt())
    assert result["verified"] is False
    assert "unexpected_governed_test_git_pin:stegverse-master-records" in result["reasons"]


def test_historical_receipt_listing_the_removed_component_still_aligns():
    receipt = _receipt()
    receipt["components"].append(
        {"repository": "master-records/orchestration", "commit_sha": "3" * 40,
         "source_parent_commit": "03312236c115bc814024d700810391340648601f"}
    )
    result = verify_governed_test_dependency_alignment(REQUIREMENTS, receipt)
    assert result["verified"] is True


def test_missing_release_component_fails_closed():
    receipt = _receipt()
    receipt["components"] = [
        item for item in receipt["components"] if item["repository"] != "Data-Continuation/core-lite"
    ]
    result = verify_governed_test_dependency_alignment(REQUIREMENTS, receipt)
    assert result["verified"] is False
    assert "stegverse-core-lite:release_component_missing" in result["reasons"]
