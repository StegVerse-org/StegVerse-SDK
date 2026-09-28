"""Manifest-creation capability classification and active resolution contract."""
from __future__ import annotations
from copy import deepcopy
from typing import Any, Mapping

ONLINE="ONLINE"
OFFLINE="OFFLINE"
UNKNOWN_CAPABILITY="UNKNOWN_CAPABILITY"
SCHEMA="stegverse.manifest-capability-resolution.v1"


def classify_capability(capability:str, processor_routes:Mapping[str,str], published_routes:Mapping[str,Mapping[str,Any]])->dict[str,Any]:
    name=str(capability or "").strip().lower()
    if not name:
        raise ValueError("processing capability is required")
    route_id=processor_routes.get(name)
    if route_id is None:
        return {
          "schema":SCHEMA,"capability":name,"status":UNKNOWN_CAPABILITY,
          "route_id":None,"solution_required":True,
          "next_action":"CREATE_CAPABILITY_DEVELOPMENT_DEPLOYMENT_REQUEST",
          "user_request_preserved":True,"authority_effect":"NONE_CLASSIFICATION_ONLY",
        }
    route=published_routes.get(route_id)
    if not isinstance(route,Mapping):
        return {
          "schema":SCHEMA,"capability":name,"status":OFFLINE,"route_id":route_id,
          "solution_required":True,
          "workaround_candidates":["REPAIR_PUBLISHED_ROUTE_BINDING","SELECT_ADMITTED_EQUIVALENT_CAPABILITY"],
          "next_action":"ATTEMPT_GOVERNED_WORKAROUND_SELECTION",
          "authority_effect":"NONE_CLASSIFICATION_ONLY",
        }
    if route.get("runtime_installed") is not True:
        candidates=route.get("offline_workaround_candidates")
        if not isinstance(candidates,list) or not candidates:
            candidates=["REPAIR_OR_DEPLOY_EXISTING_CAPABILITY","SELECT_ADMITTED_EQUIVALENT_CAPABILITY"]
        return {
          "schema":SCHEMA,"capability":name,"status":OFFLINE,"route_id":route_id,
          "solution_required":True,"workaround_candidates":deepcopy(candidates),
          "next_action":"ATTEMPT_GOVERNED_WORKAROUND_SELECTION",
          "authority_effect":"NONE_CLASSIFICATION_ONLY",
        }
    return {
      "schema":SCHEMA,"capability":name,"status":ONLINE,"route_id":route_id,
      "solution_required":False,"next_action":"BUILD_AND_SUBMIT_MANIFEST",
      "authority_effect":"NONE_CLASSIFICATION_ONLY",
    }


def capability_development_request(*, capability:str, processor_request:Mapping[str,Any], source_framework:str, source_output_id:str)->dict[str,Any]:
    name=str(capability or "").strip().lower()
    if not name: raise ValueError("processing capability is required")
    if not isinstance(processor_request,Mapping):
        raise ValueError("UNKNOWN_CAPABILITY requires the original processor_request object")
    return {
      "schema":"stegverse.capability-development-request.v1",
      "state":"REQUESTED","requested_capability":name,
      "source_framework":str(source_framework).strip(),"source_output_id":str(source_output_id).strip(),
      "original_processor_request":deepcopy(dict(processor_request)),
      "requested_process":[
        "DISCOVER_EXISTING_EQUIVALENT_CAPABILITY",
        "DEFINE_CAPABILITY_AND_PROFILE_CONTRACT_IF_ABSENT",
        "DEVELOP_WITHIN_EXISTING_SDK_AUTHORITY",
        "VALIDATE_AND_DEPLOY_THROUGH_EXISTING_RELEASE_AUTHORITY",
        "RETRY_ORIGINAL_USER_MANIFEST_REQUEST",
      ],
      "solution_required":True,"user_request_preserved":True,
      "request_granted_authority":False,"authority_effect":"NONE_REQUEST_ONLY",
    }
