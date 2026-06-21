"""Governed issuer interface for Ecosystem Chat.

The default issuer fails closed. A real issuer must be injected explicitly.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class IssuerResult:
    issued: bool
    receipt_id: str | None
    issuer_name: str
    errors: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "issued": self.issued,
            "receipt_id": self.receipt_id,
            "issuer_name": self.issuer_name,
            "errors": self.errors,
        }


class EcosystemChatIssuer(Protocol):
    def issue(self, receipt_decision: dict[str, Any]) -> IssuerResult:
        """Evaluate a receipt decision and return an issuer result."""


class DisabledEcosystemChatIssuer:
    issuer_name = "DISABLED_ECOSYSTEM_CHAT_ISSUER"

    def issue(self, receipt_decision: dict[str, Any]) -> IssuerResult:
        return IssuerResult(
            issued=False,
            receipt_id=None,
            issuer_name=self.issuer_name,
            errors=["governed issuer is not installed"],
        )


def issue_with_governed_issuer(
    receipt_decision: dict[str, Any],
    issuer: EcosystemChatIssuer | None = None,
) -> dict[str, Any]:
    active_issuer = issuer or DisabledEcosystemChatIssuer()
    return active_issuer.issue(receipt_decision).to_dict()
