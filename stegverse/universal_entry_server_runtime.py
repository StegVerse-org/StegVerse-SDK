"""Server-side composition for the universal-entry runtime.

This module wires existing dependency-injected components without owning browser
credentials, deployment authority, or activation authority. Every live integration
is disabled by default and must be supplied explicitly by a server process.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping, Sequence

from .activation_evidence import evaluate_activation_evidence
from .canonical_source_collector import CanonicalSourceCollector
from .ecosystem_catalog import build_catalog, validate_catalog
from .ecosystem_records import AuthoritativeEcosystemRetriever
from .governed_conversation import GovernedConversationHandler
from .llm_adapter_bridge import GovernedLLMAdapterProvider
from .master_records_organization_record import MasterRecordsOrganizationRecordClient
from .repository_source_reader import AllowlistedRepositorySourceReader
from .universal_entry_handlers import build_default_handler_registry
from .universal_entry_runtime import run_universal_entry


OrganizationRecordClient = MasterRecordsOrganizationRecordClient

# Legacy configuration key accepted by from_mapping only
# (MASTER-RECORDS-BULK-SEMANTIC-REMEDIATION-002).
LEGACY_ORGANIZATION_RECORD_ENABLED_KEY = "custody_enabled"


class UniversalEntryServerRuntimeError(ValueError):
    """Raised when server-side runtime composition violates a boundary."""


@dataclass(frozen=True)
class UniversalEntryServerConfig:
    source_collection_enabled: bool = False
    provider_enabled: bool = False
    organization_record_enabled: bool = False
    activation_evidence_enabled: bool = False
    catalog_built_at: str | None = None
    catalog_source_set_id: str | None = None
    # Deprecated name of organization_record_enabled, accepted for pinned callers only.
    custody_enabled: bool | None = None

    def __post_init__(self) -> None:
        if self.custody_enabled is not None:
            object.__setattr__(
                self,
                "organization_record_enabled",
                self.organization_record_enabled or self.custody_enabled is True,
            )
            object.__setattr__(self, "custody_enabled", None)

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "UniversalEntryServerConfig":
        allowed = {
            "source_collection_enabled",
            "provider_enabled",
            "organization_record_enabled",
            LEGACY_ORGANIZATION_RECORD_ENABLED_KEY,
            "activation_evidence_enabled",
            "catalog_built_at",
            "catalog_source_set_id",
        }
        unknown = sorted(set(raw) - allowed)
        if unknown:
            raise UniversalEntryServerRuntimeError(
                f"unknown server runtime configuration: {', '.join(unknown)}"
            )
        return cls(
            source_collection_enabled=raw.get("source_collection_enabled") is True,
            provider_enabled=raw.get("provider_enabled") is True,
            organization_record_enabled=(
                raw.get("organization_record_enabled") is True
                or raw.get(LEGACY_ORGANIZATION_RECORD_ENABLED_KEY) is True
            ),
            activation_evidence_enabled=raw.get("activation_evidence_enabled") is True,
            catalog_built_at=(str(raw["catalog_built_at"]) if raw.get("catalog_built_at") else None),
            catalog_source_set_id=(
                str(raw["catalog_source_set_id"])
                if raw.get("catalog_source_set_id")
                else None
            ),
        )


@dataclass
class UniversalEntryServerRuntime:
    config: UniversalEntryServerConfig
    source_inventory: Sequence[Mapping[str, Any]] = ()
    source_reader: AllowlistedRepositorySourceReader | None = None
    provider: GovernedLLMAdapterProvider | None = None
    organization_record_client: MasterRecordsOrganizationRecordClient | None = None
    # Deprecated name of organization_record_client, accepted for pinned callers only.
    custody_client: OrganizationRecordClient | None = None

    def __post_init__(self) -> None:
        if self.custody_client is not None:
            if self.organization_record_client is not None:
                raise UniversalEntryServerRuntimeError(
                    "pass organization_record_client only; custody_client is its deprecated name"
                )
            self.organization_record_client = self.custody_client
            self.custody_client = None

    def _build_retriever(self) -> AuthoritativeEcosystemRetriever | None:
        if not self.config.source_collection_enabled:
            return None
        if self.source_reader is None:
            raise UniversalEntryServerRuntimeError(
                "source collection enabled without an allowlisted source reader"
            )
        if not self.config.catalog_built_at or not self.config.catalog_source_set_id:
            raise UniversalEntryServerRuntimeError(
                "source collection requires catalog_built_at and catalog_source_set_id"
            )
        collector = CanonicalSourceCollector.from_inventory(
            self.source_inventory,
            reader=self.source_reader,
        )
        collection = collector.collect()
        catalog = build_catalog(
            collection["projections"],
            built_at=self.config.catalog_built_at,
            source_set_id=self.config.catalog_source_set_id,
        )
        validated = validate_catalog(catalog)
        return AuthoritativeEcosystemRetriever.from_mappings(validated["records"])

    def process(
        self,
        envelope: Mapping[str, Any],
        capability_registry: Mapping[str, Any],
        *,
        initial_context: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        if self.config.provider_enabled and self.provider is None:
            raise UniversalEntryServerRuntimeError(
                "provider enabled without a governed provider"
            )
        if self.config.organization_record_enabled and self.organization_record_client is None:
            raise UniversalEntryServerRuntimeError(
                "organization records enabled without an organization-record client"
            )

        retriever = self._build_retriever()
        conversation = GovernedConversationHandler(
            provider=self.provider if self.config.provider_enabled else None
        )
        handlers = build_default_handler_registry(
            ecosystem_retriever=retriever,
            external_llm_provider=self.provider if self.config.provider_enabled else None,
        )
        handlers["conversation"] = conversation

        result = run_universal_entry(
            envelope,
            capability_registry,
            handlers,
            initial_context=initial_context,
            organization_record_client=(
                self.organization_record_client
                if self.config.organization_record_enabled
                else None
            ),
        )
        result["server_runtime"] = {
            "source_collection_enabled": self.config.source_collection_enabled,
            "provider_enabled": self.config.provider_enabled,
            "organization_record_enabled": self.config.organization_record_enabled,
            "activation_evidence_enabled": self.config.activation_evidence_enabled,
            "credentials_exposed_to_entry_adapter": False,
            "deployment_authorized": False,
            "activation_performed": False,
        }
        return result

    def evaluate_readiness(self, evidence: Mapping[str, Any]) -> dict[str, Any]:
        if not self.config.activation_evidence_enabled:
            raise UniversalEntryServerRuntimeError(
                "activation evidence evaluation is disabled"
            )
        return evaluate_activation_evidence(evidence)
