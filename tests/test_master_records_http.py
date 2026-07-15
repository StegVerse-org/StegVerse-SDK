from __future__ import annotations

import json

import pytest

from stegverse.master_records_http import (
    MasterRecordsHTTPError,
    MasterRecordsHTTPTransport,
)


def test_submit_uses_authenticated_https_route_and_session_header():
    calls = []

    def executor(method, url, headers, body, timeout):
        calls.append((method, url, headers, body, timeout))
        return {"schema": "receipt"}

    transport = MasterRecordsHTTPTransport(
        base_url="https://records.example",
        credential_ref="secret://master-records/token",
        token_resolver=lambda ref: "resolved-token",
        executor=executor,
    )
    result = transport.submit({"session_id": "session-1", "submission_id": "sub-1"})

    assert result == {"schema": "receipt"}
    method, url, headers, body, timeout = calls[0]
    assert method == "POST"
    assert url == "https://records.example/api/custody/universal-entry"
    assert headers["Authorization"] == "Bearer resolved-token"
    assert headers["X-SteGVerse-Session"] == "session-1"
    assert json.loads(body.decode("utf-8"))["submission_id"] == "sub-1"
    assert timeout == 15.0


def test_reconstruct_escapes_receipt_identity_and_uses_get():
    calls = []

    def executor(method, url, headers, body, timeout):
        calls.append((method, url, headers, body, timeout))
        return {"schema": "reconstruction"}

    transport = MasterRecordsHTTPTransport(
        base_url="https://records.example/",
        credential_ref="secret://master-records/token",
        token_resolver=lambda ref: "resolved-token",
        executor=executor,
    )
    result = transport.reconstruct("receipt/one two")

    assert result == {"schema": "reconstruction"}
    method, url, headers, body, _ = calls[0]
    assert method == "GET"
    assert url.endswith("/receipts/receipt%2Fone%20two/reconstruction")
    assert body is None
    assert "X-SteGVerse-Session" not in headers


def test_transport_can_bind_transport_neutral_custody_client():
    transport = MasterRecordsHTTPTransport(
        base_url="https://records.example",
        credential_ref="secret://master-records/token",
        token_resolver=lambda ref: "resolved-token",
        executor=lambda *args: {},
    )
    client = transport.as_custody_client()
    assert client.submit_transport == transport.submit
    assert client.reconstruct_transport == transport.reconstruct


def test_rejects_remote_http():
    with pytest.raises(MasterRecordsHTTPError, match="must use HTTPS"):
        MasterRecordsHTTPTransport(
            base_url="http://records.example",
            credential_ref="secret://master-records/token",
            token_resolver=lambda ref: "token",
            executor=lambda *args: {},
        )


def test_allows_localhost_http_only_when_explicit():
    transport = MasterRecordsHTTPTransport(
        base_url="http://localhost:8080",
        credential_ref="secret://master-records/token",
        token_resolver=lambda ref: "token",
        executor=lambda *args: {},
        allow_localhost_http=True,
    )
    assert transport.base_url == "http://localhost:8080"


def test_rejects_url_credentials():
    with pytest.raises(MasterRecordsHTTPError, match="must not contain credentials"):
        MasterRecordsHTTPTransport(
            base_url="https://user:pass@records.example",
            credential_ref="secret://master-records/token",
            token_resolver=lambda ref: "token",
            executor=lambda *args: {},
        )


def test_rejects_empty_credential_resolution():
    transport = MasterRecordsHTTPTransport(
        base_url="https://records.example",
        credential_ref="secret://master-records/token",
        token_resolver=lambda ref: "",
        executor=lambda *args: {},
    )
    with pytest.raises(MasterRecordsHTTPError, match="returned no token"):
        transport.submit({"session_id": "session-1"})


def test_requires_submission_session_identity():
    transport = MasterRecordsHTTPTransport(
        base_url="https://records.example",
        credential_ref="secret://master-records/token",
        token_resolver=lambda ref: "token",
        executor=lambda *args: {},
    )
    with pytest.raises(MasterRecordsHTTPError, match="session_id is required"):
        transport.submit({})


def test_requires_positive_timeout_and_reconstruction_template():
    with pytest.raises(MasterRecordsHTTPError, match="timeout_seconds must be positive"):
        MasterRecordsHTTPTransport(
            base_url="https://records.example",
            credential_ref="secret://master-records/token",
            token_resolver=lambda ref: "token",
            executor=lambda *args: {},
            timeout_seconds=0,
        )
    with pytest.raises(MasterRecordsHTTPError, match="must include"):
        MasterRecordsHTTPTransport(
            base_url="https://records.example",
            credential_ref="secret://master-records/token",
            token_resolver=lambda ref: "token",
            executor=lambda *args: {},
            reconstruction_path_template="/api/reconstruction",
        )


def test_rejects_non_object_responses():
    transport = MasterRecordsHTTPTransport(
        base_url="https://records.example",
        credential_ref="secret://master-records/token",
        token_resolver=lambda ref: "token",
        executor=lambda *args: ["not", "object"],
    )
    with pytest.raises(MasterRecordsHTTPError, match="must be a JSON object"):
        transport.submit({"session_id": "session-1"})
