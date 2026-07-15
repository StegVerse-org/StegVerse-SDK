import json
from io import BytesIO

import pytest

from stegverse.ecosystem_projection import (
    EcosystemProjectionError,
    project_record,
    project_records,
)
from stegverse.http_transport import (
    AuthenticatedJSONTransport,
    HTTPTransportError,
    LLMAdapterHTTPTransport,
)


class FakeResponse:
    def __init__(self, payload, status=200):
        self.status = status
        self._raw = json.dumps(payload).encode("utf-8")

    def read(self):
        return self._raw

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def test_authenticated_transport_preserves_headers_and_payload():
    observed = {}

    def opener(req, timeout):
        observed["url"] = req.full_url
        observed["headers"] = dict(req.header_items())
        observed["body"] = json.loads(req.data.decode("utf-8"))
        observed["timeout"] = timeout
        return FakeResponse({"ok": True})

    transport = AuthenticatedJSONTransport(
        "https://gateway.example",
        bearer_token="server-secret",
        session_header="session-1",
        opener=opener,
    )
    result = LLMAdapterHTTPTransport(transport)({"message": "hello"})
    assert result == {"ok": True}
    assert observed["url"] == "https://gateway.example/api/ecosystem-chat"
    assert observed["headers"]["Authorization"] == "Bearer server-secret"
    assert observed["headers"]["X-stegverse-session"] == "session-1"
    assert observed["body"] == {"message": "hello"}


def test_transport_rejects_insecure_remote_http():
    with pytest.raises(HTTPTransportError):
        AuthenticatedJSONTransport("http://example.com")


def test_transport_rejects_non_object_response():
    def opener(req, timeout):
        return FakeResponse([1, 2, 3])

    transport = AuthenticatedJSONTransport("https://gateway.example", opener=opener)
    with pytest.raises(HTTPTransportError, match="RESPONSE_MUST_BE_OBJECT"):
        transport.post("/api/ecosystem-chat", {})


def canonical_source(**overrides):
    value = {
        "canonical": True,
        "authoritative": True,
        "repository": "StegVerse-Labs/Site",
        "source": "docs/SITE_MIRROR_HANDOFF.md",
        "record_type": "handoff",
        "title": "Site handoff",
        "text": "Current activation state.",
        "observed_at": "2026-07-14T20:00:00Z",
        "lifecycle_state": "CURRENT",
        "tags": ["site", "handoff"],
    }
    value.update(overrides)
    return value


def test_projection_requires_explicit_canonical_authority():
    with pytest.raises(EcosystemProjectionError, match="canonical"):
        project_record(canonical_source(canonical=False))
    with pytest.raises(EcosystemProjectionError, match="authoritative"):
        project_record(canonical_source(authoritative=False))


def test_projection_is_deterministic_and_sorted():
    a = canonical_source(repository="B/repo", source="b.md", title="B")
    b = canonical_source(repository="A/repo", source="a.md", title="A")
    first = project_records([a, b])
    second = project_records([b, a])
    assert first == second
    assert [record["repository"] for record in first] == ["A/repo", "B/repo"]
    assert all(record["canonical_source_declared"] is True for record in first)


def test_projection_rejects_duplicate_identity():
    source = canonical_source(record_id="record-1")
    with pytest.raises(EcosystemProjectionError, match="duplicate"):
        project_records([source, source])
