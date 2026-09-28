from copy import deepcopy
from stegverse.capability_resolution import ONLINE, OFFLINE, UNKNOWN_CAPABILITY, classify_capability
from stegverse.manifest_builder import PROCESSOR_ROUTES, build_manifest
from stegverse.route_resolution import PUBLISHED_ROUTES, STEGBROWSER_ROUTE_ID


def _stegbrowser_request():
    outbound="sha256:"+"a"*64
    return {"schema":"stegbrowser.llm-profile-request.v1","profile":"llm.v1","prompt":"TEST5_A",
      "response_marker":"TEST5_A","provider":"openai","journey":{
      "schema":"stegverse.packet-carried-endpoint-receipt-journey/v1","journey_id":"test5-a",
      "origin_endpoint":"origin","ephemeral_endpoint":"ephemeral",
      "outbound_manifest_sha256":outbound,"return_manifest_sha256":"sha256:"+"b"*64,
      "return_predecessor_manifest_sha256":outbound}}


def test_online_capability_is_bound_at_manifest_creation():
    manifest=build_manifest(data={"test":5},data_class="test",source_framework="eval",
      source_output_id="online",processor_request=_stegbrowser_request(),process="stegbrowser")
    assert manifest["extensions"]["capability_resolution"]["status"]==ONLINE
    assert manifest["processing"]["route_id"]==STEGBROWSER_ROUTE_ID


def test_offline_capability_returns_active_workaround_contract(monkeypatch):
    original=deepcopy(PUBLISHED_ROUTES[STEGBROWSER_ROUTE_ID])
    monkeypatch.setitem(PUBLISHED_ROUTES,STEGBROWSER_ROUTE_ID,{**original,"runtime_installed":False,
      "offline_workaround_candidates":["USE_ADMITTED_LOCAL_LLM_PROFILE","REPAIR_STEGBROWSER_RUNTIME"]})
    result=build_manifest(data={"test":5},source_framework="eval",source_output_id="offline",
      processor_request=_stegbrowser_request(),process="stegbrowser")
    assert result["state"]=="CAPABILITY_WORKAROUND_REQUIRED"
    r=result["capability_resolution"]
    assert r["status"]==OFFLINE and r["solution_required"] is True
    assert r["next_action"]=="ATTEMPT_GOVERNED_WORKAROUND_SELECTION"
    assert r["workaround_candidates"]


def test_unknown_capability_becomes_user_requested_development_deployment_obligation():
    r=classify_capability("future_thing",PROCESSOR_ROUTES,PUBLISHED_ROUTES)
    assert r["status"]==UNKNOWN_CAPABILITY
    from stegverse.capability_resolution import capability_development_request
    req=capability_development_request(capability="future_thing",processor_request={"intent":"do it"},
      source_framework="eval",source_output_id="unknown")
    assert req["state"]=="REQUESTED"
    assert req["requested_capability"]=="future_thing"
    assert req["requested_process"][-1]=="RETRY_ORIGINAL_USER_MANIFEST_REQUEST"
    assert req["request_granted_authority"] is False
