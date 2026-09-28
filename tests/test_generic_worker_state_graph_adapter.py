from stegverse.manifest_builder import build_manifest
from stegverse.manifest_state_transition_runtime import derive_execution_request

def _policy():
    p={"expected_task_execution":1,"known_delay":0,"inferred_unknown_delay_reserve":0,"records_decomposition":0,"safety_reserve":0}
    return {"mode":"DERIVED_COST_TASK_DELAY_BUDGET","production_recompute_required":True,"decomposition_target":"RECORDS_ENABLED_PACKET","retirement_condition":"PURPOSE_COMPLETED_OR_FAILED_OR_BUDGET_EXHAUSTED","cost_analysis":{"expected_compute_units":1,"external_cost_usd_ceiling":0,"task_cost_basis":"test"},"time_budget_seconds":p,"derived_max_lifetime_seconds":sum(p.values()),"unknown_delay_inference_basis":"test"}

def test_purpose_worker_adapter_only_derives_graph():
    manifest=build_manifest(data={"text":"abc"},data_class="test",source_framework="evaluator",source_output_id="generic-worker",processor_request={"schema":"stegverse.sdk.purpose-bound-worker-test.v1","test_id":"generic-worker","purpose":"prove generic state graph","required_capability":"text","lifetime_policy":_policy(),"expected_evidence_fields":["records_only"]},process="purpose_bound_worker")
    request=derive_execution_request(manifest)
    assert request["state_graph"]["adapter_executes_lifecycle"] is False
    assert request["sdk_executes_lifecycle"] is False
    assert request["transition_authority"]=="INTERLOCK_INTR"
