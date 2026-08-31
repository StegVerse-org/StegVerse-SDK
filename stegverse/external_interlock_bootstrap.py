"""Canonical external-organization Interlock bootstrap surfaces.

These builders describe how an external organization/evaluator participates in
StegVerse through the production manifest/receipt-bound Interlock + InTr path.
They do not perform transport, mint receipts, grant authority, or assert that an
interaction occurred.
"""
from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any, Mapping

BOOTSTRAP_SCHEMA="stegverse.external_interlock_bootstrap_instructions.v1"
MANIFEST_SCHEMA="stegverse.external_organization.interaction_manifest.v1"
REQUEST_SCHEMA="stegverse.external_organization.interlock_request.v1"
REQUEST_CLASS="EXTERNAL_ORGANIZATION_INTERACTION"
TRANSPORT="InTr"
FIRST_OPERATION="REQUEST_SELF_CHARACTERIZATION"
EXPERIMENT_ID="STEGVERSE-002-SELF-CHARACTERIZATION-001"
SUBJECT_ID="StegVerse-002"
SDK_ORGANIZATION_ID="StegVerse-SDK-Evaluator"
OBJECTIVE="Determine what constitutes the entity identified as StegVerse-002 and produce a representation sufficient for another system to evaluate and reconstruct your conclusion."

def _canonical(value:Any)->bytes:
    return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False).encode("utf-8")

def canonical_sha256(value:Any)->str:
    return hashlib.sha256(_canonical(value)).hexdigest()

def external_interlock_bootstrap_instructions()->dict[str,Any]:
    """Return evaluator-neutral instructions for establishing an external Interlock."""
    return {
        "schema":BOOTSTRAP_SCHEMA,
        "mechanism":"CANONICAL_EXTERNAL_INTERLOCK",
        "transport":TRANSPORT,
        "production_lane":True,
        "demo_or_test_specific_lane":False,
        "sequence":[
            "identify external organization/evaluator",
            "construct exact interaction manifest",
            "bind target and manifest SHA-256",
            "submit through canonical Interlock Connector using InTr",
            "require authentic ingress transport receipt",
            "receive target response through the bound Interlock",
            "require authentic egress transport receipt",
            "preserve interaction manifest and receipts for Master Records custody/reconstruction",
        ],
        "required_request_properties":{
            "authority_transfer":False,
            "manifest_bound":True,
            "receipt_bound":True,
            "master_records_required":True,
        },
        "sdk_mints_intr_receipts":False,
        "sdk_grants_authority":False,
        "connection_itself_proves_interaction":False,
        "authority_effect_resolution":"DERIVED_FROM_APPLICABLE_TRANSITION_ELEMENTS",
    }

def known_available_organizations()->list[dict[str,Any]]:
    """Return organizations whose availability is known without implying a connection."""
    return [{
        "organization_id":"Admissible-Existence",
        "availability":"KNOWN_AVAILABLE_FROM_CONSTRUCTION_PROVENANCE",
        "connection_state":"NOT_CONNECTED",
        "connection_preestablished":False,
        "relevance_to_current_inquiry":"NOT_PRESCRIBED",
        "source_lineage":{
            "repository":"Admissible-Existence/TT",
            "commit":"ab60b42934222a2cb5335a5a8194f258a491fc57",
            "registry_path":"TT_ELEMENTS.json",
            "formal_standing_path":"FORMAL_STANDING_SPEC.md",
            "subject_provenance_ref":"StegVerse-002/micro-node-runtime:experiments/self-characterization-001/CONSTRUCTION_PROVENANCE.v0.1.json",
        },
        "availability_authority_effect":"NONE",
    }]


def build_external_interaction_manifest(
    *,
    source_organization_id:str,
    target_organization_id:str,
    operation:str,
    payload:Mapping[str,Any] | None=None,
    experiment_id:str | None=None,
)->dict[str,Any]:
    """Build a neutral manifest for a caller-selected external organization interaction."""
    source=str(source_organization_id or "").strip()
    target=str(target_organization_id or "").strip()
    op=str(operation or "").strip()
    if not source or not target or not op:
        raise ValueError("source organization, target organization, and operation are required")
    body={
        "schema":MANIFEST_SCHEMA,
        "manifest_id":"EXT-"+canonical_sha256({"source":source,"target":target,"operation":op,"payload":dict(payload or {})})[:24],
        "experiment_id":str(experiment_id or "").strip() or None,
        "source_organization":{"organization_id":source},
        "target":{"organization_id":target,"relationship_at_manifest_creation":"EXTERNAL_NOT_SELF"},
        "operation":op,
        "payload":deepcopy(dict(payload or {})),
        "interaction_instructions":{
            "request_is_manifest_receipt_bound":True,
            "transport":TRANSPORT,
            "response_must_bind_request_manifest":True,
            "response_transport_receipts_required":True,
            "master_records_custody_required":True,
        },
        "authority_transfer":False,
        "authority_effect_resolution":"DERIVED_FROM_APPLICABLE_TRANSITION_ELEMENTS",
    }
    return {**body,"manifest_sha256":canonical_sha256(body)}

def build_external_interlock_request(
    *,
    source_organization_id:str,
    target_organization_id:str,
    operation:str,
    payload:Mapping[str,Any] | None,
    authority_ref:str,
    experiment_id:str | None=None,
)->dict[str,Any]:
    """Build a production-lane request for a caller-selected external interaction."""
    authority=str(authority_ref or "").strip()
    if not authority:
        raise ValueError("authority_ref is required")
    manifest=build_external_interaction_manifest(
        source_organization_id=source_organization_id,
        target_organization_id=target_organization_id,
        operation=operation,
        payload=payload,
        experiment_id=experiment_id,
    )
    return {
        "schema_version":REQUEST_SCHEMA,
        "request_class":REQUEST_CLASS,
        "operation":manifest["operation"],
        "authority_ref":authority,
        "transport":TRANSPORT,
        "payload":{"manifest":manifest},
        "bindings":{
            "experiment_id":manifest["experiment_id"],
            "source_organization_id":source_organization_id,
            "target_organization_id":target_organization_id,
            "manifest_id":manifest["manifest_id"],
            "manifest_sha256":manifest["manifest_sha256"],
        },
        "authority_transfer":False,
        "sdk_mints_intr_receipt":False,
        "sdk_claims_delivery":False,
        "authority_effect_resolution":"DERIVED_FROM_APPLICABLE_TRANSITION_ELEMENTS",
    }

def build_sv002_self_characterization_manifest()->dict[str,Any]:
    """Build the exact first external manifest without prescribing a self-definition."""
    body={
        "schema":MANIFEST_SCHEMA,
        "manifest_id":"SDK-SV002-FIRST-SELF-CHARACTERIZATION-001",
        "experiment_id":EXPERIMENT_ID,
        "source_organization":{
            "organization_id":SDK_ORGANIZATION_ID,
            "role":"EXTERNAL_EVALUATOR_ORGANIZATION",
        },
        "target":{
            "entity_id":SUBJECT_ID,
            "relationship_at_manifest_creation":"EXTERNAL_NOT_SELF",
        },
        "operation":FIRST_OPERATION,
        "objective":OBJECTIVE,
        "interaction_instructions":{
            "request_is_manifest_receipt_bound":True,
            "transport":TRANSPORT,
            "response_instruction":"Return your completed response through this bound Interlock using the manifest/receipt interaction contract.",
            "response_must_bind_request_manifest":True,
            "response_transport_receipts_required":True,
            "master_records_custody_required":True,
        },
        "knowledge_policy":{
            "prescribe_self_ontology":False,
            "prescribe_formalism":False,
            "prescribe_transition_elements":False,
            "prescribe_external_followup":False,
            "prescribe_admissible_existence_connection":False,
        },
        "authority_transfer":False,
        "authority_effect_resolution":"DERIVED_FROM_APPLICABLE_TRANSITION_ELEMENTS",
    }
    return {**body,"manifest_sha256":canonical_sha256(body)}

def validate_sv002_self_characterization_manifest(manifest:Mapping[str,Any])->dict[str,Any]:
    if not isinstance(manifest,Mapping):
        raise ValueError("manifest must be an object")
    if manifest.get("schema")!=MANIFEST_SCHEMA:
        raise ValueError("manifest schema mismatch")
    if manifest.get("experiment_id")!=EXPERIMENT_ID:
        raise ValueError("experiment binding mismatch")
    if manifest.get("operation")!=FIRST_OPERATION:
        raise ValueError("operation mismatch")
    if manifest.get("objective")!=OBJECTIVE:
        raise ValueError("objective must remain exact")
    if (manifest.get("target") or {}).get("entity_id")!=SUBJECT_ID:
        raise ValueError("target mismatch")
    if manifest.get("authority_transfer") is not False or manifest.get("authority_effect_resolution")!="DERIVED_FROM_APPLICABLE_TRANSITION_ELEMENTS":
        raise ValueError("authority boundary mismatch")
    body=dict(manifest); claimed=str(body.pop("manifest_sha256",""))
    if claimed!=canonical_sha256(body):
        raise ValueError("manifest SHA-256 mismatch")
    policy=manifest.get("knowledge_policy")
    if not isinstance(policy,Mapping) or any(policy.get(k) is not False for k in (
        "prescribe_self_ontology","prescribe_formalism","prescribe_transition_elements",
        "prescribe_external_followup","prescribe_admissible_existence_connection"
    )):
        raise ValueError("knowledge policy became prescriptive")
    return deepcopy(dict(manifest))

def build_sv002_first_interlock_request(authority_ref:str)->dict[str,Any]:
    authority=str(authority_ref or "").strip()
    if not authority:
        raise ValueError("authority_ref is required")
    manifest=build_sv002_self_characterization_manifest()
    return {
        "schema_version":REQUEST_SCHEMA,
        "request_class":REQUEST_CLASS,
        "operation":FIRST_OPERATION,
        "authority_ref":authority,
        "transport":TRANSPORT,
        "payload":{"manifest":manifest},
        "bindings":{
            "experiment_id":EXPERIMENT_ID,
            "source_organization_id":SDK_ORGANIZATION_ID,
            "target_entity_id":SUBJECT_ID,
            "manifest_id":manifest["manifest_id"],
            "manifest_sha256":manifest["manifest_sha256"],
        },
        "authority_transfer":False,
        "sdk_mints_intr_receipt":False,
        "sdk_claims_delivery":False,
        "authority_effect_resolution":"DERIVED_FROM_APPLICABLE_TRANSITION_ELEMENTS",
    }

def validate_sv002_first_interlock_request(request:Mapping[str,Any])->dict[str,Any]:
    if not isinstance(request,Mapping):
        raise ValueError("request must be an object")
    expected={
        "schema_version":REQUEST_SCHEMA,
        "request_class":REQUEST_CLASS,
        "operation":FIRST_OPERATION,
        "transport":TRANSPORT,
        "authority_transfer":False,
        "sdk_mints_intr_receipt":False,
        "sdk_claims_delivery":False,
        "authority_effect_resolution":"DERIVED_FROM_APPLICABLE_TRANSITION_ELEMENTS",
    }
    for key,value in expected.items():
        if request.get(key)!=value:
            raise ValueError(f"{key} mismatch")
    if not str(request.get("authority_ref") or "").strip():
        raise ValueError("authority_ref required")
    payload=request.get("payload"); bindings=request.get("bindings")
    if not isinstance(payload,Mapping) or not isinstance(bindings,Mapping):
        raise ValueError("payload and bindings must be objects")
    manifest=validate_sv002_self_characterization_manifest(payload.get("manifest") or {})
    required={
        "experiment_id":EXPERIMENT_ID,
        "source_organization_id":SDK_ORGANIZATION_ID,
        "target_entity_id":SUBJECT_ID,
        "manifest_id":manifest["manifest_id"],
        "manifest_sha256":manifest["manifest_sha256"],
    }
    for key,value in required.items():
        if bindings.get(key)!=value:
            raise ValueError(f"bindings.{key} mismatch")
    return deepcopy(dict(request))

__all__=[
    "BOOTSTRAP_SCHEMA","MANIFEST_SCHEMA","REQUEST_SCHEMA","REQUEST_CLASS","TRANSPORT",
    "FIRST_OPERATION","EXPERIMENT_ID","SUBJECT_ID","SDK_ORGANIZATION_ID","OBJECTIVE",
    "canonical_sha256","external_interlock_bootstrap_instructions",
    "known_available_organizations","build_external_interaction_manifest","build_external_interlock_request","build_sv002_self_characterization_manifest",
    "validate_sv002_self_characterization_manifest","build_sv002_first_interlock_request",
    "validate_sv002_first_interlock_request",
]
