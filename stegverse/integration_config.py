"""Non-secret external integration configuration for universal-entry servers.

This module records endpoint identities, immutable source bindings, and credential
references without storing credential values or authorizing deployment. Validation is
deterministic and fail closed; a valid packet is configuration evidence only.
"""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Mapping, Sequence
from urllib.parse import urlparse


class IntegrationConfigError(ValueError):
    """Raised when an integration configuration violates a safety boundary."""


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(value: Any) -> str:
    return "sha256:" + sha256(_canonical(value).encode("utf-8")).hexdigest()


def _required_text(raw: Mapping[str, Any], name: str) -> str:
    value = str(raw.get(name, "")).strip()
    if not value:
        raise IntegrationConfigError(f"{name} is required")
    return value


def _credential_ref(raw: Mapping[str, Any]) -> str | None:
    forbidden = {
        "credential",
        "credential_value",
        "token",
        "api_key",
        "secret",
        "password",
        "authorization",
        "bearer_token",
    }
    present = sorted(name for name in forbidden if raw.get(name) not in (None, ""))
    if present:
        raise IntegrationConfigError(
            "embedded credential material is prohibited: " + ", ".join(present)
        )
    value = raw.get("credential_ref")
    return str(value).strip() if value not in (None, "") else None


def _https_endpoint(value: str, *, allow_localhost_http: bool = False) -> str:
    parsed = urlparse(value)
    if not parsed.scheme or not parsed.netloc:
        raise IntegrationConfigError("endpoint must be an absolute URL")
    localhost = parsed.hostname in {"localhost", "127.0.0.1", "::1"}
    if parsed.scheme != "https" and not (
        allow_localhost_http and localhost and parsed.scheme == "http"
    ):
        raise IntegrationConfigError("remote integration endpoints must use HTTPS")
    if parsed.username or parsed.password:
        raise IntegrationConfigError("endpoint URLs must not contain credentials")
    return value.rstrip("/")


def _source_binding(raw: Mapping[str, Any]) -> dict[str, Any]:
    allowed = {
        "source_id",
        "repository",
        "path",
        "ref",
        "expected_blob_sha",
        "expected_content_digest",
        "read_receipt_required",
        "credential_ref",
    }
    unknown = sorted(set(raw) - allowed)
    if unknown:
        raise IntegrationConfigError(
            "unknown source binding fields: " + ", ".join(unknown)
        )
    return {
        "source_id": _required_text(raw, "source_id"),
        "repository": _required_text(raw, "repository"),
        "path": _required_text(raw, "path"),
        "ref": _required_text(raw, "ref"),
        "expected_blob_sha": (
            str(raw["expected_blob_sha"]) if raw.get("expected_blob_sha") else None
        ),
        "expected_content_digest": (
            str(raw["expected_content_digest"])
            if raw.get("expected_content_digest")
            else None
        ),
        "read_receipt_required": raw.get("read_receipt_required", True) is True,
        "credential_ref": _credential_ref(raw),
    }


def _service_binding(
    raw: Mapping[str, Any],
    *,
    service: str,
    required_path: str,
    allow_localhost_http: bool,
) -> dict[str, Any]:
    allowed = {
        "enabled",
        "base_url",
        "credential_ref",
        "expected_service",
        "expected_schema_version",
        "session_identity_required",
        "required_path",
    }
    unknown = sorted(set(raw) - allowed)
    if unknown:
        raise IntegrationConfigError(
            f"unknown {service} binding fields: " + ", ".join(unknown)
        )
    supplied_path = raw.get("required_path")
    if supplied_path is not None and str(supplied_path) != required_path:
        raise IntegrationConfigError(f"{service} required path mismatch")
    enabled = raw.get("enabled") is True
    if not enabled:
        return {
            "enabled": False,
            "base_url": None,
            "credential_ref": None,
            "expected_service": None,
            "expected_schema_version": None,
            "session_identity_required": True,
            "required_path": required_path,
        }
    base_url = _https_endpoint(
        _required_text(raw, "base_url"), allow_localhost_http=allow_localhost_http
    )
    return {
        "enabled": True,
        "base_url": base_url,
        "credential_ref": _credential_ref(raw),
        "expected_service": _required_text(raw, "expected_service"),
        "expected_schema_version": _required_text(raw, "expected_schema_version"),
        "session_identity_required": raw.get("session_identity_required", True) is True,
        "required_path": required_path,
    }


def build_integration_config(
    *,
    environment: str,
    source_bindings: Sequence[Mapping[str, Any]] = (),
    provider: Mapping[str, Any] | None = None,
    custody: Mapping[str, Any] | None = None,
    site_same_origin_route: str | None = None,
    allow_localhost_http: bool = False,
) -> dict[str, Any]:
    """Build a deterministic non-authorizing integration configuration packet."""
    environment = environment.strip()
    if not environment:
        raise IntegrationConfigError("environment is required")
    sources = [_source_binding(raw) for raw in source_bindings]
    source_ids = [item["source_id"] for item in sources]
    locations = [(item["repository"], item["path"], item["ref"]) for item in sources]
    if len(source_ids) != len(set(source_ids)):
        raise IntegrationConfigError("duplicate source_id")
    if len(locations) != len(set(locations)):
        raise IntegrationConfigError("duplicate repository/path/ref binding")
    sources.sort(key=lambda item: (item["repository"], item["path"], item["ref"]))

    provider_binding = _service_binding(
        provider or {},
        service="provider",
        required_path="/api/ecosystem-chat",
        allow_localhost_http=allow_localhost_http,
    )
    custody_binding = _service_binding(
        custody or {},
        service="custody",
        required_path="/api/custody/universal-entry",
        allow_localhost_http=allow_localhost_http,
    )
    if site_same_origin_route is not None:
        route = str(site_same_origin_route).strip()
        if not route.startswith("/") or "://" in route:
            raise IntegrationConfigError("Site route must be a same-origin absolute path")
    else:
        route = None

    body: dict[str, Any] = {
        "schema": "stegverse.universal_entry_integration_config.v0.1",
        "environment": environment,
        "source_bindings": sources,
        "provider": provider_binding,
        "custody": custody_binding,
        "site_same_origin_route": route,
        "credentials_embedded": False,
        "credentials_exposed_to_entry_adapter": False,
        "deployment_authorized": False,
        "activation_performed": False,
        "release_authorized": False,
        "authorizing": False,
        "execution_authority_granted": False,
        "admissibility_determined": False,
    }
    body["config_id"] = _digest(body)
    return body


def validate_integration_config(packet: Mapping[str, Any]) -> dict[str, Any]:
    if packet.get("schema") != "stegverse.universal_entry_integration_config.v0.1":
        raise IntegrationConfigError("unsupported integration configuration schema")
    for field in (
        "credentials_embedded",
        "credentials_exposed_to_entry_adapter",
        "deployment_authorized",
        "activation_performed",
        "release_authorized",
        "authorizing",
        "execution_authority_granted",
        "admissibility_determined",
    ):
        if packet.get(field) is not False:
            raise IntegrationConfigError(f"integration configuration escalated {field}")
    expected = dict(packet)
    config_id = expected.pop("config_id", None)
    if config_id != _digest(expected):
        raise IntegrationConfigError("integration configuration digest mismatch")
    rebuilt = build_integration_config(
        environment=str(packet.get("environment", "")),
        source_bindings=list(packet.get("source_bindings", [])),
        provider=dict(packet.get("provider", {})),
        custody=dict(packet.get("custody", {})),
        site_same_origin_route=packet.get("site_same_origin_route"),
        allow_localhost_http=True,
    )
    if rebuilt != dict(packet):
        raise IntegrationConfigError("integration configuration normalization mismatch")
    return dict(packet)
