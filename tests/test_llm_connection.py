from __future__ import annotations

import io
import json
from pathlib import Path
import tempfile
import unittest

from stegverse.llm_connection import (
    LLMConnectionError,
    build_connection_descriptor,
    build_submission,
    probe_adapter,
    save_connection_descriptor,
    validate_connection_descriptor,
)


class _Response:
    def __init__(self, payload: dict, status: int = 200) -> None:
        self.payload = payload
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


def _opener(request, timeout=5):
    del timeout
    url = request.full_url
    if url.endswith("/healthz"):
        return _Response({"status": "OK", "authority_attached": False})
    if url.endswith("/readyz"):
        return _Response({"state": "READY", "authority_attached": False})
    if url.endswith("/v1/user-llm/capabilities"):
        return _Response({"status": "OK", "capabilities": [{"route": "demo_test_suite"}], "authority_attached": False})
    if url.endswith("/v1/user-llm/activation-proof"):
        return _Response({"state": "ACTIVATED", "proof_hash": "fixture", "authority_attached": False})
    raise AssertionError(url)


class LLMConnectionTests(unittest.TestCase):
    def _descriptor(self) -> dict:
        return build_connection_descriptor(
            adapter_url="http://127.0.0.1:8080",
            user_id="tester",
            llm_id="local-llm",
            provider="ollama",
            model="llama3.2",
            scopes=["demo:read"],
        )

    def test_descriptor_forces_adapter_submit_endpoint(self) -> None:
        descriptor = self._descriptor()
        self.assertEqual(
            descriptor["endpoints"]["submit"],
            "http://127.0.0.1:8080/v1/user-llm/requests",
        )
        self.assertEqual(
            descriptor["submission_invariant"],
            "ALL_LLM_SUBMISSIONS_ENTER_STEGVERSE_THROUGH_LLM_ADAPTER",
        )
        self.assertEqual(descriptor["credential_authority"], "TV/TVC")
        self.assertFalse(descriptor["credential_fields_permitted"])
        self.assertEqual(descriptor["github_token_runtime_authority"], "NONE")
        self.assertEqual(validate_connection_descriptor(descriptor), descriptor)

    def test_secret_or_token_fields_are_rejected(self) -> None:
        descriptor = self._descriptor()
        descriptor["api_key"] = "must-not-be-accepted"
        with self.assertRaisesRegex(LLMConnectionError, "secret_or_token_field_rejected"):
            validate_connection_descriptor(descriptor)

    def test_probe_accepts_canonical_adapter_surface_without_credentials(self) -> None:
        probe = probe_adapter("http://127.0.0.1:8080", opener=_opener)
        self.assertEqual(probe.state, "CONNECTED")
        self.assertFalse(probe.as_dict()["credential_required"])
        self.assertFalse(probe.as_dict()["github_token_required"])

    def test_submission_uses_bound_identity_and_rejects_secret_payloads(self) -> None:
        descriptor = self._descriptor()
        request = build_submission(
            descriptor,
            route="demo_test_suite",
            action="inspect",
            payload={"question": "show public StegVerse help"},
        )
        self.assertEqual(request["identity"]["llm_id"], "local-llm")
        self.assertEqual(request["route"], "demo_test_suite")
        with self.assertRaisesRegex(LLMConnectionError, "secret_or_token_field_rejected"):
            build_submission(
                descriptor,
                route="demo_test_suite",
                action="inspect",
                payload={"authorization": "Bearer nope"},
            )

    def test_save_persists_only_validated_non_secret_descriptor(self) -> None:
        descriptor = self._descriptor()
        with tempfile.TemporaryDirectory() as directory:
            path = save_connection_descriptor(descriptor, root=Path(directory))
            saved = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(saved, descriptor)
        serialized = json.dumps(saved).lower()
        self.assertNotIn("api_key", serialized)
        self.assertNotIn("authorization", serialized)


if __name__ == "__main__":
    unittest.main()
