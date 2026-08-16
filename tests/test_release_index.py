import io
import json
from unittest.mock import patch

from stegverse import release_index


def release(version: str, *, complete: bool = True, draft: bool = False):
    assets = []
    classes = ("s", "ns")
    formats = ("zip", "tar.gz") if complete else ("zip",)
    for deployment_class in classes:
        for archive_format in formats:
            name = f"stegverse-sdk-{deployment_class}-micro-ecosystem-v0.{archive_format}"
            assets.append({
                "name": name,
                "size": 100,
                "browser_download_url": f"https://github.com/StegVerse-Labs/StegCore/releases/download/stegverse-portable-v{version}/{name}",
            })
    return {
        "tag_name": f"stegverse-portable-v{version}",
        "name": f"Portable {version}",
        "draft": draft,
        "prerelease": False,
        "published_at": "2026-08-15T00:00:00Z",
        "assets": assets,
    }


def test_release_versions_sort_newest_and_mark_complete_dual_format():
    rows = [release("0.2.0"), release("0.3.0"), {"tag_name": "unrelated-v9"}]
    versions = release_index.versions_from_rows(rows)
    assert [row["version"] for row in versions] == ["0.3.0", "0.2.0"]
    assert all(row["complete_dual_format_release"] is True for row in versions)
    assert set(versions[0]["assets"]["S"]) == {"zip", "tar.gz"}
    assert set(versions[0]["assets"]["NS"]) == {"zip", "tar.gz"}


def test_draft_and_unrelated_releases_are_not_listed():
    rows = [release("0.2.0", draft=True), {"tag_name": "v0.2.0", "assets": []}]
    assert release_index.versions_from_rows(rows) == []


def test_incomplete_release_is_visible_but_not_complete():
    versions = release_index.versions_from_rows([release("0.4.0", complete=False)])
    assert len(versions) == 1
    assert versions[0]["complete_dual_format_release"] is False


def test_fetch_versions_uses_public_index_without_credentials():
    payload = json.dumps([release("0.5.0")]).encode()
    response = io.BytesIO(payload)
    response.__enter__ = lambda self: self
    response.__exit__ = lambda *args: None
    with patch.object(release_index, "urlopen", return_value=response) as fetch:
        result = release_index.fetch_versions()
    assert result["state"] == "PASS"
    assert result["latest_complete_version"] == "0.5.0"
    request = fetch.call_args.args[0]
    assert request.full_url == release_index.RELEASE_API
    assert request.get_header("Authorization") is None


def test_network_failure_degrades_non_authorizing():
    with patch.object(release_index, "urlopen", side_effect=OSError("offline")):
        result = release_index.fetch_versions()
    assert result["state"] == "UNAVAILABLE_NON_AUTHORIZING"
    assert result["versions"] == []
    assert result["authority_effect"] == "NONE"
