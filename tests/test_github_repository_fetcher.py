import base64

import pytest

from stegverse.github_repository_fetcher import (
    GitHubRepositoryFetcher,
    GitHubRepositoryFetcherError,
)
from stegverse.repository_source_reader import RepositorySourceBinding


def binding(**overrides):
    raw = {
        "source_id": "sdk-handoff",
        "repository": "StegVerse-org/StegVerse-SDK",
        "path": "SDK_MIRROR_HANDOFF.md",
        "ref": "main",
    }
    raw.update(overrides)
    return RepositorySourceBinding.from_mapping(raw)


def response(text="# SDK Mirror Handoff\n", **overrides):
    raw = {
        "type": "file",
        "path": "SDK_MIRROR_HANDOFF.md",
        "sha": "blob-123",
        "encoding": "base64",
        "content": base64.b64encode(text.encode("utf-8")).decode("ascii"),
    }
    raw.update(overrides)
    return raw


def test_fetches_public_file_without_authorization_and_emits_receipt():
    observed = {}

    def execute(request, timeout):
        observed["url"] = request.full_url
        observed["headers"] = {key.lower(): value for key, value in request.header_items()}
        observed["timeout"] = timeout
        return response()

    result = GitHubRepositoryFetcher(http_executor=execute)(binding())

    assert result["text"].startswith("# SDK Mirror Handoff")
    assert result["blob_sha"] == "blob-123"
    assert result["receipt_ref"] == result["read_receipt"]["receipt_id"]
    assert result["read_receipt"]["authorizing"] is False
    assert result["read_receipt"]["custody_transferred"] is False
    assert result["read_receipt"]["credential_requirement"] == "NONE"
    assert result["read_receipt"]["credential_authority"] == "TV/TVC"
    assert result["credentials_exposed"] is False
    assert "authorization" not in observed["headers"]
    assert observed["url"].endswith("/contents/SDK_MIRROR_HANDOFF.md?ref=main")
    assert observed["headers"]["x-github-api-version"] == "2022-11-28"
    assert observed["timeout"] == 15.0


def test_constructor_has_no_github_token_interface():
    with pytest.raises(TypeError):
        GitHubRepositoryFetcher(credential_ref="secret://github/source-reader")
    with pytest.raises(TypeError):
        GitHubRepositoryFetcher(token_resolver=lambda ref: "token")


def test_rejects_non_file_response():
    fetcher = GitHubRepositoryFetcher(
        http_executor=lambda request, timeout: response(type="dir")
    )
    with pytest.raises(GitHubRepositoryFetcherError, match="did not resolve to a file"):
        fetcher(binding())


def test_rejects_response_path_mismatch():
    fetcher = GitHubRepositoryFetcher(
        http_executor=lambda request, timeout: response(path="README.md")
    )
    with pytest.raises(GitHubRepositoryFetcherError, match="path mismatch"):
        fetcher(binding())


def test_rejects_expected_blob_mismatch():
    fetcher = GitHubRepositoryFetcher(
        http_executor=lambda request, timeout: response(sha="different")
    )
    with pytest.raises(GitHubRepositoryFetcherError, match="blob sha mismatch"):
        fetcher(binding(expected_blob_sha="expected"))


def test_rejects_content_digest_mismatch():
    fetcher = GitHubRepositoryFetcher(
        http_executor=lambda request, timeout: response()
    )
    with pytest.raises(GitHubRepositoryFetcherError, match="content digest mismatch"):
        fetcher(binding(expected_content_digest="sha256:not-the-content"))


def test_rejects_non_base64_encoding():
    fetcher = GitHubRepositoryFetcher(
        http_executor=lambda request, timeout: response(encoding="utf-8")
    )
    with pytest.raises(GitHubRepositoryFetcherError, match="base64 encoding"):
        fetcher(binding())


def test_rejects_invalid_utf8_file_content():
    bad = response()
    bad["content"] = base64.b64encode(b"\xff\xfe").decode("ascii")
    fetcher = GitHubRepositoryFetcher(http_executor=lambda request, timeout: bad)
    with pytest.raises(GitHubRepositoryFetcherError, match="valid UTF-8"):
        fetcher(binding())


def test_rejects_non_github_api_base():
    fetcher = GitHubRepositoryFetcher(
        api_base="https://example.invalid",
        http_executor=lambda request, timeout: response(),
    )
    with pytest.raises(GitHubRepositoryFetcherError, match="API base"):
        fetcher(binding())
