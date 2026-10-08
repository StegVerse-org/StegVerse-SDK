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
            "preserve interaction manifest and receipts as Master Records organization records/reconstruction",
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
            "master_records_organization_record_required":True,
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

GENERATION_MANIFEST_SCHEMA="stegverse.external_organization.interaction_manifest.v2"
GENERATION_DECLARED_STRINGS=("manifest_id","experiment_id","operation","objective",
                             "transition_reference","packet_id_prefix")
NON_PRESCRIPTIVE_POLICY_KEYS=(
    "prescribe_self_ontology","prescribe_formalism","prescribe_transition_elements",
    "prescribe_external_followup","prescribe_admissible_existence_connection",
)
PREDECESSOR_FIELDS=("generation","manifest_sha256","result_sha256","heartbeat_epoch")


def _declared(mapping:Mapping[str,Any],key:str,where:str)->str:
    value=mapping.get(key)
    if not isinstance(value,str) or not value.strip():
        raise ValueError(f"{where}.{key} must be declared")
    return value.strip()


def _digest_field(mapping:Mapping[str,Any],key:str,where:str)->str:
    value=mapping.get(key)
    if not isinstance(value,str) or len(value)!=64 or any(c not in "0123456789abcdef" for c in value):
        raise ValueError(f"{where}.{key} must be a sha256 digest")
    return value


def non_prescriptive_knowledge_policy()->dict[str,Any]:
    """The neutral knowledge policy: the manifest asks, it does not prescribe."""
    return {key:False for key in NON_PRESCRIPTIVE_POLICY_KEYS}


def successor_predecessor_binding(
    *,
    predecessor_manifest:Mapping[str,Any],
    predecessor_result:Any,
    heartbeat_epoch:int,
)->dict[str,Any]:
    """Bind a successor generation to the generation whose result was reviewed.

    Augment-and-repeat is how a question advances here: review a generation's
    result, augment the manifest, freeze it again. This computes the binding so
    a caller cannot transcribe a digest wrongly, and so the successor records
    what was actually read rather than an assertion that something was.

    `heartbeat_epoch` is the oscillator count at which the result was observed.
    Order across generations comes from that count, never from a host clock
    reading, so a chain stays orderable without any node agreeing on a time.
    """
    if not isinstance(predecessor_manifest,Mapping):
        raise ValueError("predecessor_manifest must be an object")
    generation=predecessor_manifest.get("generation")
    if not isinstance(generation,int) or isinstance(generation,bool) or generation<1:
        raise ValueError("predecessor_manifest.generation must be an integer of at least 1")
    if not isinstance(heartbeat_epoch,int) or isinstance(heartbeat_epoch,bool) or heartbeat_epoch<1:
        raise ValueError("heartbeat_epoch must be a positive oscillator count")
    body=dict(predecessor_manifest); claimed=str(body.pop("manifest_sha256",""))
    if claimed!=canonical_sha256(body):
        raise ValueError("predecessor_manifest SHA-256 mismatch")
    return {
        "generation":generation,
        "manifest_sha256":claimed,
        "result_sha256":canonical_sha256(predecessor_result),
        "heartbeat_epoch":heartbeat_epoch,
    }


def build_external_interaction_generation_manifest(
    *,
    manifest_id:str,
    experiment_id:str,
    operation:str,
    objective:str,
    source_organization_id:str,
    source_role:str="EXTERNAL_EVALUATOR_ORGANIZATION",
    target_entity_id:str,
    target_organization:str,
    target_service:str,
    transition_reference:str,
    packet_id_prefix:str,
    generation:int,
    predecessor:Mapping[str,Any] | None,
    response_instruction:str="Return your completed response through this bound Interlock using the manifest/receipt interaction contract.",
)->dict[str,Any]:
    """Build a generic external-organization interaction manifest for one generation.

    Every identity this interaction has is declared by the caller and carried in
    the manifest: the experiment, the operation, the objective, the far side's
    organization *and* service, the transition it references, and the prefix its
    transport packet is named with. The frozen first-generation builder below
    left the last four implicit in the consuming runtime's constants, which made
    the runtime the only place a second question could be asked from.

    Each generation remains a frozen one-shot. Nothing here holds a standing
    query: the stability preference runs toward `ONE_SHOT_OPERATION`, and a
    durable standing coupling is what the least-stable-micronode policy denies.
    What replaces editing a runtime is declaring the next generation.
    """
    body={
        "schema":GENERATION_MANIFEST_SCHEMA,
        "manifest_id":str(manifest_id or "").strip(),
        "experiment_id":str(experiment_id or "").strip(),
        "generation":generation,
        "predecessor":dict(predecessor) if isinstance(predecessor,Mapping) else predecessor,
        "source_organization":{
            "organization_id":str(source_organization_id or "").strip(),
            "role":str(source_role or "").strip(),
        },
        "target":{
            "entity_id":str(target_entity_id or "").strip(),
            "organization":str(target_organization or "").strip(),
            "service":str(target_service or "").strip(),
            "relationship_at_manifest_creation":"EXTERNAL_NOT_SELF",
        },
        "operation":str(operation or "").strip(),
        "objective":str(objective or "").strip(),
        "transition_reference":str(transition_reference or "").strip(),
        "packet_id_prefix":str(packet_id_prefix or "").strip(),
        "interaction_instructions":{
            "request_is_manifest_receipt_bound":True,
            "transport":TRANSPORT,
            "response_instruction":str(response_instruction or "").strip(),
            "response_must_bind_request_manifest":True,
            "response_transport_receipts_required":True,
            "master_records_organization_record_required":True,
        },
        "knowledge_policy":non_prescriptive_knowledge_policy(),
        "authority_transfer":False,
        "authority_effect_resolution":"DERIVED_FROM_APPLICABLE_TRANSITION_ELEMENTS",
    }
    manifest={**body,"manifest_sha256":canonical_sha256(body)}
    # Built and then validated by the same contract a consumer applies, so a
    # builder cannot emit a manifest the boundary would refuse.
    return validate_external_interaction_generation_manifest(manifest)


def validate_external_interaction_generation_manifest(manifest:Mapping[str,Any])->dict[str,Any]:
    """Validate a generation manifest, defaulting nothing it failed to declare."""
    if not isinstance(manifest,Mapping):
        raise ValueError("manifest must be an object")
    if manifest.get("schema")!=GENERATION_MANIFEST_SCHEMA:
        raise ValueError(f"manifest schema must be {GENERATION_MANIFEST_SCHEMA}")
    for key in GENERATION_DECLARED_STRINGS:
        _declared(manifest,key,"manifest")

    source=manifest.get("source_organization")
    if not isinstance(source,Mapping):
        raise ValueError("manifest.source_organization must be declared")
    _declared(source,"organization_id","manifest.source_organization")
    target=manifest.get("target")
    if not isinstance(target,Mapping):
        raise ValueError("manifest.target must be declared")
    for key in ("entity_id","organization","service"):
        _declared(target,key,"manifest.target")

    policy=manifest.get("knowledge_policy")
    if not isinstance(policy,Mapping) or any(policy.get(k) is not False for k in NON_PRESCRIPTIVE_POLICY_KEYS):
        raise ValueError("knowledge policy became prescriptive")
    if manifest.get("authority_transfer") is not False:
        raise ValueError("authority boundary mismatch")
    if manifest.get("authority_effect_resolution")!="DERIVED_FROM_APPLICABLE_TRANSITION_ELEMENTS":
        raise ValueError("authority boundary mismatch")

    generation=manifest.get("generation")
    if not isinstance(generation,int) or isinstance(generation,bool) or generation<1:
        raise ValueError("manifest.generation must be an integer of at least 1")
    if "predecessor" not in manifest:
        # An absent key is an unstated chain position. Reading it as a first
        # generation would be the defaulting this contract exists to remove.
        raise ValueError("manifest.predecessor must be declared, as null for a first generation")
    predecessor=manifest["predecessor"]
    if generation==1:
        if predecessor is not None:
            raise ValueError("a first generation declares no predecessor")
    else:
        if not isinstance(predecessor,Mapping):
            raise ValueError("a generation beyond the first declares the predecessor it continues")
        unknown=sorted(set(predecessor)-set(PREDECESSOR_FIELDS))
        if unknown:
            raise ValueError("unknown predecessor fields: "+", ".join(unknown))
        if predecessor.get("generation")!=generation-1:
            raise ValueError("manifest.predecessor.generation must be this generation less one")
        for key in ("manifest_sha256","result_sha256"):
            _digest_field(predecessor,key,"manifest.predecessor")
        epoch=predecessor.get("heartbeat_epoch")
        if not isinstance(epoch,int) or isinstance(epoch,bool) or epoch<1:
            raise ValueError("manifest.predecessor.heartbeat_epoch must be a positive oscillator count")

    body=dict(manifest); claimed=str(body.pop("manifest_sha256",""))
    if claimed!=canonical_sha256(body):
        raise ValueError("manifest SHA-256 mismatch")
    return deepcopy(dict(manifest))


def build_external_interaction_generation_request(*,authority_ref:str,**manifest_kwargs:Any)->dict[str,Any]:
    """Build the production-lane request carrying one generation's manifest.

    The request envelope is unchanged from the first-generation contract -- same
    schema, same authority boundary, same bindings -- because none of that is
    what generalized. Only the manifest gained declarations, so only the
    manifest is versioned.
    """
    authority=str(authority_ref or "").strip()
    if not authority:
        raise ValueError("authority_ref is required")
    manifest=build_external_interaction_generation_manifest(**manifest_kwargs)
    return {
        "schema_version":REQUEST_SCHEMA,
        "request_class":REQUEST_CLASS,
        "operation":manifest["operation"],
        "authority_ref":authority,
        "transport":TRANSPORT,
        "payload":{"manifest":manifest},
        "bindings":{
            "experiment_id":manifest["experiment_id"],
            "source_organization_id":manifest["source_organization"]["organization_id"],
            "target_entity_id":manifest["target"]["entity_id"],
            "manifest_id":manifest["manifest_id"],
            "manifest_sha256":manifest["manifest_sha256"],
        },
        "authority_transfer":False,
        "sdk_mints_intr_receipt":False,
        "sdk_claims_delivery":False,
        "authority_effect_resolution":"DERIVED_FROM_APPLICABLE_TRANSITION_ELEMENTS",
    }


def validate_external_interaction_generation_request(request:Mapping[str,Any])->dict[str,Any]:
    """Validate a generation request without supplying anything it omitted."""
    if not isinstance(request,Mapping):
        raise ValueError("request must be an object")
    expected={
        "schema_version":REQUEST_SCHEMA,
        "request_class":REQUEST_CLASS,
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
    manifest=validate_external_interaction_generation_manifest(payload.get("manifest") or {})
    if request.get("operation")!=manifest["operation"]:
        raise ValueError("request operation does not match the manifest declaration")
    required={
        "experiment_id":manifest["experiment_id"],
        "source_organization_id":manifest["source_organization"]["organization_id"],
        "target_entity_id":manifest["target"]["entity_id"],
        "manifest_id":manifest["manifest_id"],
        "manifest_sha256":manifest["manifest_sha256"],
    }
    for key,value in required.items():
        if bindings.get(key)!=value:
            raise ValueError(f"bindings.{key} mismatch")
    return deepcopy(dict(request))


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
            "master_records_organization_record_required":True,
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
    "BOOTSTRAP_SCHEMA","MANIFEST_SCHEMA","GENERATION_MANIFEST_SCHEMA","REQUEST_SCHEMA","REQUEST_CLASS","TRANSPORT",
    "non_prescriptive_knowledge_policy","successor_predecessor_binding",
    "build_external_interaction_generation_manifest","validate_external_interaction_generation_manifest",
    "build_external_interaction_generation_request","validate_external_interaction_generation_request",
    "FIRST_OPERATION","EXPERIMENT_ID","SUBJECT_ID","SDK_ORGANIZATION_ID","OBJECTIVE",
    "canonical_sha256","external_interlock_bootstrap_instructions",
    "known_available_organizations","build_external_interaction_manifest","build_external_interlock_request","build_sv002_self_characterization_manifest",
    "validate_sv002_self_characterization_manifest","build_sv002_first_interlock_request",
    "validate_sv002_first_interlock_request",
]
