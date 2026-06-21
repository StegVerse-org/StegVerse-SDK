"""Deterministic local issuer for Ecosystem Chat.

This issuer is not used by the default pipeline. It must be injected explicitly.
"""

from __future__ import annotations

import hashlib

from .ecosystem_chat_issuer import IssuerResult


class LocalGovernedEcosystemChatIssuer:
    issuer_name = "LOCAL_GOVERNED_ECOSYSTEM_CHAT_ISSUER"

    def issue(self, receipt_decision: dict) -> IssuerResult:
        if receipt_decision.get("decision") != "ISSUANCE_PENDING":
            return IssuerResult(
                issued=False,
                receipt_id=None,
                issuer_name=self.issuer_name,
                errors=["receipt decision is not eligible for local issuance"],
            )

        request_hash = receipt_decision.get("request_hash")
        if not isinstance(request_hash, str) or not request_hash.startswith("sha256:"):
            return IssuerResult(
                issued=False,
                receipt_id=None,
                issuer_name=self.issuer_name,
                errors=["request_hash is missing or invalid"],
            )

        return IssuerResult(
            issued=True,
            receipt_id=_receipt_id(request_hash),
            issuer_name=self.issuer_name,
            errors=[],
        )


def _receipt_id(request_hash: str) -> str:
    digest = hashlib.sha256(request_hash.encode("utf-8")).hexdigest()
    return "ecr-local-" + digest[:24]
