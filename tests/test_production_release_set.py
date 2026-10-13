import json
from pathlib import Path
from types import SimpleNamespace

from stegverse import production_release_set as prs


class FakeDistribution:
    version = "2.3.4"

    def __init__(self, direct_url):
        self.direct_url = direct_url

    def read_text(self, name):
        assert name == "direct_url.json"
        return json.dumps(self.direct_url)


def test_release_tag_is_distinct_from_commit_pin(monkeypatch):
    tagged = FakeDistribution({
        "url": "https://github.com/example/repo.git",
        "vcs_info": {"vcs": "git", "commit_id": "a" * 40, "requested_revision": "v2.3.4"},
    })
    monkeypatch.setattr(prs.metadata, "distribution", lambda _name: tagged)
    row = prs._installed_component({"role": "x", "distribution": "x", "repository": "example/repo"})
    assert row["release_tag"] == "v2.3.4"
    assert row["release_binding_status"] == "RELEASE_TAG_BOUND"
    assert row["changelog_url"].endswith("/releases/tag/v2.3.4")


def test_commit_pin_is_not_misrepresented_as_release(monkeypatch):
    sha = "b" * 40
    pinned = FakeDistribution({
        "url": "https://github.com/example/repo.git",
        "vcs_info": {"vcs": "git", "commit_id": sha, "requested_revision": sha},
    })
    monkeypatch.setattr(prs.metadata, "distribution", lambda _name: pinned)
    row = prs._installed_component({"role": "x", "distribution": "x", "repository": "example/repo"})
    assert row["commit_sha"] == sha
    assert row["release_tag"] is None
    assert row["release_binding_status"] == "COMMIT_OR_PACKAGE_ONLY"
    assert row["changelog_url"] is None


def test_release_set_hash_changes_when_component_set_changes(monkeypatch):
    calls = iter([
        FakeDistribution({"url": "u", "vcs_info": {"commit_id": "a" * 40, "requested_revision": "v1"}}),
        FakeDistribution({"url": "u", "vcs_info": {"commit_id": "b" * 40, "requested_revision": "v1"}}),
        FakeDistribution({"url": "u", "vcs_info": {"commit_id": "c" * 40, "requested_revision": "v1"}}),
        FakeDistribution({"url": "u", "vcs_info": {"commit_id": "d" * 40, "requested_revision": "v1"}}),
    ])
    monkeypatch.setattr(prs.metadata, "distribution", lambda _name: next(calls))
    first = prs.installed_release_set()
    assert first["all_components_release_tag_bound"] is True
    assert first["all_components_commit_bound"] is True
    assert first["release_set_hash"].startswith("sha256:")

    changed = dict(first)
    changed["release_set_hash"] = "sha256:changed"
    comparison = prs.compare_release_sets(first, changed)
    assert comparison["same_installed_release_set"] is False
    assert comparison["release_set_changed_since_original_run"] is True


def test_public_catalog_retains_release_changelog(monkeypatch):
    payload = [{
        "tag_name": "v1.2.3",
        "name": "Release 1.2.3",
        "published_at": "2026-08-16T00:00:00Z",
        "prerelease": False,
        "draft": False,
        "html_url": "https://github.com/example/repo/releases/tag/v1.2.3",
        "body": "Changed governance adapter behavior.",
    }]
    monkeypatch.setattr(prs, "_fetch_json", lambda _url, _timeout: payload)
    catalog = prs.public_release_catalog()
    assert catalog["all_components_have_release"] is True
    assert catalog["components"][0]["latest_release"]["tag"] == "v1.2.3"
    assert "Changed governance" in catalog["components"][0]["latest_release"]["changelog"]


# Produced by the v1 code (main at 3259843d) and kept byte-for-byte: a retained
# historical release set whose hash covers the v1 role labels.
V1_RECORDED = Path(__file__).parent / "fixtures" / "production-release-set.v1.recorded.json"
V1_RECORDED_HASH = "sha256:3c66317186865a54e04c574b1263d0c845d386c50fd4524970286bcd085965d2"


def test_recorded_v1_release_set_still_verifies_exactly_as_recorded():
    recorded = json.loads(V1_RECORDED.read_text(encoding="utf-8"))
    assert recorded["schema"] == prs.SCHEMA_V1
    assert recorded["release_set_hash"] == V1_RECORDED_HASH
    result = prs.verify_release_set(recorded)
    assert result["verified"] is True, result
    assert result["recomputed_release_set_hash"] == V1_RECORDED_HASH
    assert result["authority_effect"] == "NONE"


def test_v1_table_is_frozen():
    assert [spec["role"] for spec in prs.COMPONENTS_V1] == [
        "sdk_entry", "governance_runtime", "manifest_route_carrier", "exact_run_custody",
    ]


def test_tampered_or_relabelled_v1_set_does_not_verify():
    recorded = json.loads(V1_RECORDED.read_text(encoding="utf-8"))
    relabelled = json.loads(json.dumps(recorded))
    relabelled["components"][3]["role"] = "downstream_run_evidence"
    assert prs.verify_release_set(relabelled)["verified"] is False
    tampered = json.loads(json.dumps(recorded))
    tampered["components"][1]["commit_sha"] = "f" * 40
    result = prs.verify_release_set(tampered)
    assert result["verified"] is False
    assert result["reason"] == "release_set_hash_mismatch"


def test_new_release_sets_use_v2_with_the_canonical_label(monkeypatch):
    monkeypatch.setattr(prs.metadata, "distribution", lambda _name: FakeDistribution(
        {"url": "u", "vcs_info": {"commit_id": "a" * 40, "requested_revision": "a" * 40}}))
    current = prs.installed_release_set()
    assert current["schema"] == prs.SCHEMA_V2 == prs.SCHEMA
    roles = {row["role"]: row for row in current["components"]}
    assert "exact_run_custody" not in roles
    assert roles["downstream_run_evidence"]["distribution"] == "stegverse-sdk"
    assert all("master-records" not in row["repository"] for row in current["components"])
    assert prs.verify_release_set(current)["verified"] is True


def test_replay_comparison_reports_the_schema_migration_and_verifies_the_original(monkeypatch):
    recorded = json.loads(V1_RECORDED.read_text(encoding="utf-8"))
    monkeypatch.setattr(prs.metadata, "distribution", lambda _name: FakeDistribution(
        {"url": "u", "vcs_info": {"commit_id": "a" * 40, "requested_revision": "a" * 40}}))
    comparison = prs.compare_release_sets(recorded, prs.installed_release_set())
    assert comparison["original_release_set_hash"] == V1_RECORDED_HASH
    assert comparison["original_release_set_schema"] == prs.SCHEMA_V1
    assert comparison["current_release_set_schema"] == prs.SCHEMA_V2
    assert comparison["release_set_schema_changed"] is True
    assert comparison["original_release_set_verification"]["verified"] is True
    assert comparison["historical_record_mutated"] is False


def test_unknown_schema_is_not_verified():
    result = prs.verify_release_set({"schema": "stegverse.production-release-set.v9", "components": []})
    assert result == {**result, "verified": False, "reason": "unknown_release_set_schema"}


def _only(installed):
    def lookup(name):
        if name in installed:
            return installed[name]
        raise prs.metadata.PackageNotFoundError(name)
    return lookup


def test_public_stegcore_distribution_is_recognised_under_its_source_role(monkeypatch):
    public = FakeDistribution({})
    public.version = "0.3.0"
    monkeypatch.setattr(prs.metadata, "distribution", _only({"stegverse-stegcore": public}))
    row = prs._installed_component({"role": "governance_runtime", "distribution": "stegcore",
                                    "repository": "StegVerse-Labs/StegCore"})
    assert row["installed"] is True
    assert row["version"] == "0.3.0"
    assert row["distribution"] == "stegcore"
    assert row["installed_distribution"] == "stegverse-stegcore"


def test_source_distribution_name_wins_and_leaves_the_row_unchanged(monkeypatch):
    source = FakeDistribution({"url": "u", "vcs_info": {"commit_id": "a" * 40, "requested_revision": "a" * 40}})
    monkeypatch.setattr(prs.metadata, "distribution", _only({"stegcore": source, "stegverse-stegcore": source}))
    row = prs._installed_component({"role": "governance_runtime", "distribution": "stegcore",
                                    "repository": "StegVerse-Labs/StegCore"})
    assert row["installed"] is True
    assert "installed_distribution" not in row


def test_release_set_with_public_stegcore_still_verifies_under_v2(monkeypatch):
    public = FakeDistribution({})
    monkeypatch.setattr(prs.metadata, "distribution", _only({
        "stegverse-sdk": public, "stegverse-stegcore": public, "stegverse-core-lite": public}))
    recorded = prs.installed_release_set()
    assert recorded["all_components_installed"] is True
    assert prs.verify_release_set(recorded)["verified"] is True


def test_absent_stegcore_under_either_name_is_not_installed(monkeypatch):
    monkeypatch.setattr(prs.metadata, "distribution", _only({}))
    row = prs._installed_component({"role": "governance_runtime", "distribution": "stegcore",
                                    "repository": "StegVerse-Labs/StegCore"})
    assert row["installed"] is False
    assert row["release_binding_status"] == "NOT_INSTALLED"
    assert "installed_distribution" not in row
