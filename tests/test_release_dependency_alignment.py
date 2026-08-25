from stegverse.release_dependency_alignment import verify_governed_test_dependency_alignment


STEGCORE_TVC_SOURCE_PARENT = "ef38410505b0ef3e84148892b1d6e3cdef20f300"
CORE_LITE_TVC_SOURCE_PARENT = "72bdb0f110031ccc2cd98b8ebb7c22b1ab7326f8"
MASTER_RECORDS_TVC_SOURCE_PARENT = "03312236c115bc814024d700810391340648601f"
PRE_TVC_STEGCORE_PROOF_SOURCE = "124ea6b53ff79db8f514cacf1aab295f03cacf74"
PRE_TVC_MASTER_RECORDS_PROOF_SOURCE = "3dae8832a167359612a15ccfde99a9f22b77fc8a"

REQUIREMENTS = [
    f'stegcore @ git+https://github.com/StegVerse-Labs/StegCore.git@{STEGCORE_TVC_SOURCE_PARENT} ; extra == "governed-test"',
    f'stegverse-core-lite @ git+https://github.com/Data-Continuation/core-lite.git@{CORE_LITE_TVC_SOURCE_PARENT} ; extra == "governed-test"',
    f'stegverse-master-records @ git+https://github.com/master-records/orchestration.git@{MASTER_RECORDS_TVC_SOURCE_PARENT} ; extra == "governed-test"',
]


def _receipt(stegcore_commit=STEGCORE_TVC_SOURCE_PARENT, master_records_commit=MASTER_RECORDS_TVC_SOURCE_PARENT):
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
            {
                "repository": "master-records/orchestration",
                "commit_sha": "3" * 40,
                "source_parent_commit": master_records_commit,
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


def test_pre_tvc_master_records_proof_source_is_rejected_for_final_receipt():
    result = verify_governed_test_dependency_alignment(
        REQUIREMENTS,
        _receipt(master_records_commit=PRE_TVC_MASTER_RECORDS_PROOF_SOURCE),
    )
    assert result["verified"] is False
    assert "stegverse-master-records:commit_mismatch" in result["reasons"]
    assert result["authority_effect"] == "NONE"


def test_missing_release_component_fails_closed():
    receipt = _receipt()
    receipt["components"] = [
        item for item in receipt["components"] if item["repository"] != "master-records/orchestration"
    ]
    result = verify_governed_test_dependency_alignment(REQUIREMENTS, receipt)
    assert result["verified"] is False
    assert "stegverse-master-records:release_component_missing" in result["reasons"]
