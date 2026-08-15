"""Credential-free SDK binding to the canonical StegVerse LLM-adapter user-LLM surface.

This module creates no provider runtime and accepts no provider/GitHub credential.
It discovers/probes the adapter's existing ``/user-llm`` HTTP surface and writes
only non-secret connection metadata for a user-controlled LLM.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

CONNECTION_SCHEMA = "stegverse.sdk.llm-adapter-connection.v1"
DEFAULT_ADAPTER_URLS = (
    "http://127.0.0.1:8080",
    "http://127.0.0.1:8000/user-llm",
    "http://127.0.0.1:18080/user-llm",
)
SECRET_FIELD_FRAGMENTS = (
    "api_key",
    "apikey",
    "authorization",
    "bearer",
    "credential",
    "password",
    "private_key",
    "secret",
    "token",
)
# These exact keys describe the *absence/location* of credential authority. Their
# values are validated separately and they never carry credential material.
SAFE_POLICY_METADATA_KEYS = frozenset(
    {
        "credential_authority",
        "credential_fields_permitted",
        "credential_required",
        "github_token_required",
        "github_token_runtime_authority",
    }
)
REQUIRED_SCOPE = "demo:read"


class LLMConnectionError(ValueError):
    """Raised when a connection descriptor violates the SDK boundary."""


@dataclass(frozen=True)
class AdapterProbe:
    base_url: str
    state: str
    health: Mapping[str, Any]
    readiness: Mapping[str, Any]
    capabilities: Mapping[str, Any]
    activation: Mapping[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "base_url": self.base_url,
            "state": self.state,
            "health": dict(self.health),
            "readiness": dict(self.readiness),
            "capabilities": dict(self.capabilities),
            "activation": dict(self.activation),
            "authority_effect": "NONE",
            "credential_required": False,
            "github_token_required": False,
        }


def _secret_shaped_key(key: str) -> bool:
    lowered = key.strip().lower().replace("-", "_")
    if lowered in SAFE_POLICY_METADATA_KEYS:
        return False
    return any(fragment in lowered for fragment in SECRET_FIELD_FRAGMENTS)


def reject_secret_fields(value: Any, path: str = "$") -> None:
    """Reject secret/token-shaped fields while permitting exact policy metadata."""
    if isinstance(value, Mapping):
        for key, nested in value.items():
            text = str(key)
            if _secret_shaped_key(text):
                raise LLMConnectionError(f"secret_or_token_field_rejected:{path}.{text}")
            reject_secret_fields(nested, f"{path}.{text}")
    elif isinstance(value, (list, tuple)):
        for index, nested in enumerate(value):
            reject_secret_fields(nested, f"{path}[{index}]")


def normalize_adapter_url(value: str) -> str:
    raw = value.strip().rstrip("/")
    if not raw:
        raise LLMConnectionError("adapter_url_required")
    parsed = urlparse(raw)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise LLMConnectionError("adapter_url_must_be_http_or_https")
    return raw


def build_connection_descriptor(
    *,
    adapter_url: str,
    user_id: str,
    llm_id: str,
    provider: str,
    model: str,
    scopes: Iterable[str] = (REQUIRED_SCOPE,),
    connection_id: str | None = None,
) -> dict[str, Any]:
    base_url = normalize_adapter_url(adapter_url)
    values = {
        "user_id": user_id.strip(),
        "llm_id": llm_id.strip(),
        "provider": provider.strip(),
        "model": model.strip(),
    }
    missing = [name for name, value in values.items() if not value]
    if missing:
        raise LLMConnectionError("missing_required_fields:" + ",".join(missing))
    normalized_scopes = sorted({str(scope).strip() for scope in scopes if str(scope).strip()})
    if REQUIRED_SCOPE not in normalized_scopes:
        normalized_scopes.append(REQUIRED_SCOPE)
        normalized_scopes.sort()

    identifier = connection_id.strip() if isinstance(connection_id, str) else ""
    if not identifier:
        identifier = f"{values['user_id']}--{values['llm_id']}".replace("/", "_").replace("\\", "_")

    descriptor = {
        "schema": CONNECTION_SCHEMA,
        "connection_id": identifier,
        "adapter_base_url": base_url,
        "identity": {
            **values,
            "scopes": normalized_scopes,
        },
        "endpoints": {
            "health": f"{base_url}/healthz",
            "readiness": f"{base_url}/readyz",
            "capabilities": f"{base_url}/v1/user-llm/capabilities",
            "activation_proof": f"{base_url}/v1/user-llm/activation-proof",
            "submit": f"{base_url}/v1/user-llm/requests",
        },
        "submission_invariant": "ALL_LLM_SUBMISSIONS_ENTER_STEGVERSE_THROUGH_LLM_ADAPTER",
        "credential_authority": "TV/TVC",
        "credential_fields_permitted": False,
        "github_token_runtime_authority": "NONE",
        "authority_effect": "NONE",
    }
    reject_secret_fields(descriptor)
    return descriptor


def validate_connection_descriptor(descriptor: Mapping[str, Any]) -> dict[str, Any]:
    reject_secret_fields(descriptor)
    if descriptor.get("schema") != CONNECTION_SCHEMA:
        raise LLMConnectionError("unsupported_connection_schema")
    identity = descriptor.get("identity")
    endpoints = descriptor.get("endpoints")
    if not isinstance(identity, Mapping) or not isinstance(endpoints, Mapping):
        raise LLMConnectionError("identity_and_endpoints_required")
    expected = build_connection_descriptor(
        adapter_url=str(descriptor.get("adapter_base_url", "")),
        user_id=str(identity.get("user_id", "")),
        llm_id=str(identity.get("llm_id", "")),
        provider=str(identity.get("provider", "")),
        model=str(identity.get("model", "")),
        scopes=identity.get("scopes") if isinstance(identity.get("scopes"), list) else (),
        connection_id=str(descriptor.get("connection_id", "")),
    )
    if descriptor.get("submission_invariant") != expected["submission_invariant"]:
        raise LLMConnectionError("submission_invariant_mismatch")
    if descriptor.get("credential_authority") != "TV/TVC":
        raise LLMConnectionError("credential_authority_must_be_tv_tvc")
    if descriptor.get("credential_fields_permitted") is not False:
        raise LLMConnectionError("credential_fields_must_be_prohibited")
    if descriptor.get("github_token_runtime_authority") != "NONE":
        raise LLMConnectionError("github_token_runtime_authority_must_be_none")
    for key, expected_url in expected["endpoints"].items():
        if endpoints.get(key) != expected_url:
            raise LLMConnectionError(f"endpoint_mismatch:{key}")
    return expected


def _get_json(url: str, opener: Callable[..., Any]) -> dict[str, Any]:
    request = Request(url, headers={"Accept": "application/json"}, method="GET")
    try:
        response = opener(request, timeout=5)
        with response:
            status = getattr(response, "status", 200)
            body = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        raise LLMConnectionError(f"adapter_http_error:{exc.code}") from exc
    except (URLError, TimeoutError, OSError) as exc:
        raise LLMConnectionError(f"adapter_unreachable:{type(exc).__name__}") from exc
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError) as exc:
        raise LLMConnectionError("adapter_response_not_json") from exc
    if status >= 400 or not isinstance(body, dict):
        raise LLMConnectionError(f"adapter_probe_failed:{status}")
    return body


def probe_adapter(adapter_url: str, *, opener: Callable[..., Any] = urlopen) -> AdapterProbe:
    base_url = normalize_adapter_url(adapter_url)
    health = _get_json(f"{base_url}/healthz", opener)
    readiness = _get_json(f"{base_url}/readyz", opener)
    capabilities = _get_json(f"{base_url}/v1/user-llm/capabilities", opener)
    activation = _get_json(f"{base_url}/v1/user-llm/activation-proof", opener)

    authority_attached = any(
        payload.get("authority_attached") is True
        for payload in (health, readiness, capabilities, activation)
    )
    if authority_attached:
        state = "REJECTED_AUTHORITY_ESCALATION"
    elif health.get("status") != "OK":
        state = "UNHEALTHY"
    elif readiness.get("state") != "READY":
        state = "DEFERRED"
    elif activation.get("state") != "ACTIVATED":
        state = "DEFERRED"
    else:
        state = "CONNECTED"

    return AdapterProbe(
        base_url=base_url,
        state=state,
        health=health,
        readiness=readiness,
        capabilities=capabilities,
        activation=activation,
    )


def discover_adapter(
    urls: Iterable[str] = DEFAULT_ADAPTER_URLS,
    *,
    opener: Callable[..., Any] = urlopen,
) -> AdapterProbe:
    failures: list[str] = []
    for url in urls:
        try:
            probe = probe_adapter(url, opener=opener)
        except LLMConnectionError as exc:
            failures.append(f"{url}:{exc}")
            continue
        if probe.state == "CONNECTED":
            return probe
        failures.append(f"{url}:state={probe.state}")
    raise LLMConnectionError("adapter_not_discovered:" + "|".join(failures))


def save_connection_descriptor(
    descriptor: Mapping[str, Any],
    *,
    root: str | Path = ".stegverse/llm-connections",
) -> Path:
    normalized = validate_connection_descriptor(descriptor)
    destination = Path(root)
    destination.mkdir(parents=True, exist_ok=True)
    name = normalized["connection_id"].replace("/", "_").replace("\\", "_")
    path = destination / f"{name}.json"
    path.write_text(json.dumps(normalized, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def build_submission(
    descriptor: Mapping[str, Any],
    *,
    route: str,
    action: str,
    payload: Mapping[str, Any],
) -> dict[str, Any]:
    normalized = validate_connection_descriptor(descriptor)
    request = {
        "identity": dict(normalized["identity"]),
        "route": route.strip(),
        "action": action.strip(),
        "payload": dict(payload),
    }
    reject_secret_fields(request)
    if not request["route"] or not request["action"]:
        raise LLMConnectionError("route_and_action_required")
    return request


__all__ = [
    "AdapterProbe",
    "CONNECTION_SCHEMA",
    "DEFAULT_ADAPTER_URLS",
    "LLMConnectionError",
    "build_connection_descriptor",
    "build_submission",
    "discover_adapter",
    "probe_adapter",
    "reject_secret_fields",
    "save_connection_descriptor",
    "validate_connection_descriptor",
]
