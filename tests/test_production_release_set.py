import json
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
