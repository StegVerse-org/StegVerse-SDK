#!/usr/bin/env python3
"""Build source-only manifests for the two canonical Entity Economy successors.

No run-manifest call, publication, release, Site propagation, or authority grant.
"""
from __future__ import annotations
import hashlib
from stegverse.publisher_paper_publication import PROFILE,TASK_ID,TARGET_REPOSITORY,prepare_publisher_paper_manifest,publisher_paper_governance_candidate
from stegverse.security_posture_request import build_security_posture_request

SOURCE_COMMIT="1b4b7b1defd46fe5c537ef67fe4a12085143f777"
COSV="10100000102000"
POLICY_MODE="RESEARCH_PUBLICATION_WITH_DISCLOSED_UNVERIFIED_EXTERNAL_REVIEW"
POLICY_REF="GCAT-BCAT-Engine/Publisher:docs/ENTITY_ECONOMY_VOLUME_III_INDEPENDENT_REVIEW_PACKET.md#2026-09-28-owner-policy-disposition"
ARTIFACTS={
"I":{"path":"papers/stegverse-entity-economy-volume-i-2026-09-29-convergence.md","sha256":"01cb40af02530e1bf5d1c99131703f484fbee02a52478665e4031fb4d924f7f2","blob":"66722e53fd2c823bbdab89488718b6e7a3918e85"},
"II":{"path":"papers/stegverse-entity-economy-volume-ii-2026-09-29-convergence.md","sha256":"e04fd1735309abe3009640d46d8d521fb868e9bb06776b15c9d0467647733e4e","blob":"a599f73776a3971853785198792588288d2d217b"}}

def build(volume,source_bytes,created_at="2026-10-04T23:57:00Z"):
 a=ARTIFACTS[volume]
 if hashlib.sha256(source_bytes).hexdigest()!=a["sha256"]: raise ValueError("canonical_successor_sha256_mismatch")
 candidate={"schema":PROFILE,"goal_task_id":TASK_ID,"target_repository":TARGET_REPOSITORY,"target_path":a["path"],"source_commit_sha":SOURCE_COMMIT,"source_sha256":a["sha256"],"source_git_blob_sha":a["blob"],"editorial_owner_approved":True,"review_policy":{"mode":POLICY_MODE,"policy_ref":POLICY_REF,"external_review_claimed":False,"owner_attested_convergence":True,"economics_report_sha256":None,"legal_report_sha256":None},"publication_executed":False,"authority_effect":"NONE"}
 action=publisher_paper_governance_candidate(candidate)
 refs=[f"task:{TASK_ID}",f"cosv:{COSV}",f"publisher-source-sha256:{a['sha256']}",f"publisher-source-commit:{SOURCE_COMMIT}",POLICY_REF]
 request={"candidate":action,"judgment":{"refusal_available":True,"operator_recoverability":"available","workload_state":"supported","time_pressure":"normal","isolation_state":"supported","evidence_refs":refs},"signal":{"admitted_signal_refs":refs,"excluded_signal_refs":[],"transformations":[],"missing_inputs":[],"uncertainty_state":"bounded","reference_state_hash":a["sha256"],"expected_reference_state_hash":a["sha256"],"reconstruction_available":True,"transformation_provenance_complete":True},"execution":{"actor_authority_current":False,"policy_current":True,"delegation_current":False,"evidence_current":True,"affected_entity_conditions_represented":True,"recoverability_profile":"recoverable","validity_window_open":True,"policy_ref":"GCAT-BCAT-Engine/Publisher#88","delegation_ref":"OWNER_DIRECT_REQUEST_NO_DELEGATION","evidence_refs":refs},"capability":{"allowed":True},"continuity":{"required":True,"previous_receipt_verified":False},"approval":{"required":False},"permission_present":True,"declared_context":{"goal_task_id":"ENTITY-ECONOMY-VOLUME-I-II-SUCCESSOR-PUBLICATION-001","cosv_task_vector":COSV,"owner_document_approval":True,"external_signed_review_claimed":False,"research_review_policy_mode":POLICY_MODE,"authority_effect":"NONE_REQUEST_CONTEXT_ONLY"}}
 posture=build_security_posture_request(task_id=TASK_ID,selection_present=False,organization_minimum_tier="SECURE",data_class=PROFILE,channel="publisher-papers")
 return prepare_publisher_paper_manifest(candidate=candidate,source_bytes=source_bytes,governance_request=request,security_posture_request=posture,created_at=created_at)
