from scripts.sync_system_boundary_evidence import build_evidence, select_qualifying_run


SOURCE = {
    "repository": "StegVerse-org/StegVerse-SDK",
    "workflow": "sdk-demo-test.yml",
    "workflow_path": ".github/workflows/sdk-demo-test.yml",
    "required_commit": "baseline",
}


def test_selects_first_successful_run_containing_baseline():
    runs = [
        {"status": "completed", "conclusion": "failure", "event": "push", "head_sha": "bad"},
        {"status": "completed", "conclusion": "success", "event": "push", "head_sha": "good", "id": 2, "html_url": "https://example/run/2"},
    ]
    selected = select_qualifying_run(
        runs,
        repository=SOURCE["repository"],
        required_commit="baseline",
        contains=lambda repository, required, observed, token: observed == "good",
    )
    assert selected["head_sha"] == "good"


def test_rejects_successful_run_without_required_baseline():
    runs = [
        {"status": "completed", "conclusion": "success", "event": "push", "head_sha": "unrelated", "id": 3, "html_url": "https://example/run/3"},
    ]
    selected = select_qualifying_run(
        runs,
        repository=SOURCE["repository"],
        required_commit="baseline",
        contains=lambda repository, required, observed, token: False,
    )
    assert selected is None


def test_pending_evidence_retains_baseline_and_null_run_identity():
    evidence = build_evidence(SOURCE, None)
    assert evidence["result"] == "PENDING"
    assert evidence["required_commit"] == "baseline"
    assert evidence["observed_commit"] is None
    assert evidence["run_id"] is None
    assert evidence["run_url"] is None


def test_pass_evidence_binds_exactly_to_successful_run_commit():
    run = {"head_sha": "observed", "id": 42, "html_url": "https://example/run/42"}
    evidence = build_evidence(SOURCE, run)
    assert evidence["result"] == "PASS"
    assert evidence["required_commit"] == "observed"
    assert evidence["observed_commit"] == "observed"
    assert evidence["run_id"] == "42"
    assert evidence["run_url"] == "https://example/run/42"
    assert evidence["production_binding_enabled"] is False
    assert evidence["release_authorized"] is False
