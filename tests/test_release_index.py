import io
import json
from unittest.mock import patch

from stegverse import release_index


def release(
    version: str,
    *,
    s_version: str | None = None,
    ns_version: str | None = None,
    complete: bool = True,
    draft: bool = False,
    inconsistent_s: bool = False,
):
    s_version = s_version or version
    ns_version = ns_version or version
    assets = []
    formats = ("zip", "tar.gz") if complete else ("zip",)
    for deployment_class, package_version in (("s", s_version), ("ns", ns_version)):
        for archive_format in formats:
            effective = package_version
            if inconsistent_s and deployment_class == "s" and archive_format == "tar.gz":
                effective = "9.9.9"
            name = f"stegverse-sdk-{deployment_class}-micro-ecosystem-v{effective}.{archive_format}"
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
    assert [row["release_version"] for row in versions] == ["0.3.0", "0.2.0"]
    assert all(row["complete_dual_format_release"] is True for row in versions)
    assert set(versions[0]["assets"]["S"]) == {"zip", "tar.gz"}
    assert set(versions[0]["assets"]["NS"]) == {"zip", "tar.gz"}


def test_release_can_expose_component_package_versions_distinct_from_release_version():
    versions = release_index.versions_from_rows([
        release("1.0.0", s_version="0.3.0", ns_version="0.2.1")
    ])
    assert versions[0]["release_version"] == "1.0.0"
    assert versions[0]["package_versions"] == {"S": "0.3.0", "NS": "0.2.1"}
    assert versions[0]["assets"]["S"]["zip"]["package_version"] == "0.3.0"
    assert versions[0]["assets"]["NS"]["tar.gz"]["package_version"] == "0.2.1"
    assert versions[0]["complete_dual_format_release"] is True


def test_draft_invalid_and_unrelated_releases_are_not_listed():
    rows = [
        release("0.2.0", draft=True),
        {"tag_name": "v0.2.0", "assets": []},
        {"tag_name": "stegverse-portable-vnot-semver", "assets": []},
    ]
    assert release_index.versions_from_rows(rows) == []


def test_incomplete_release_is_visible_but_not_complete():
    versions = release_index.versions_from_rows([release("0.4.0", complete=False)])
    assert len(versions) == 1
    assert versions[0]["complete_dual_format_release"] is False


def test_mixed_package_versions_between_zip_and_tar_are_not_complete():
    versions = release_index.versions_from_rows([release("0.4.0", inconsistent_s=True)])
    assert versions[0]["complete_dual_format_release"] is False


def test_fetch_versions_uses_public_index_without_credentials():
    payload = json.dumps([release("0.5.0", s_version="0.3.0", ns_version="0.2.1")]).encode()
    response = io.BytesIO(payload)
    response.__enter__ = lambda self: self
    response.__exit__ = lambda *args: None
    with patch.object(release_index, "urlopen", return_value=response) as fetch:
        result = release_index.fetch_versions()
    assert result["state"] == "PASS"
    assert result["schema"] == "stegverse.sdk.release-index.v2"
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
