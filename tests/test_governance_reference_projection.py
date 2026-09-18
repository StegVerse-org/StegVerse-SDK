from __future__ import annotations

import json
from contextlib import redirect_stdout
from io import StringIO

from stegverse.governance_reference_graph import build_governance_reference_graph, main as graph_main
from stegverse.governance_reference_projection import project_governance_reference_graph


def graph_fixture(*, complete=False):
    return build_governance_reference_graph(
        graph_id="projection-test",
        nodes=[
            {"node_id":"actor:a","class":"human","ref":"actor:a"},
            {"node_id":"scope:s","class":"scope","ref":"scope:s"},
            {"node_id":"constraint:q","class":"constraint","ref":"stegcore:policy-shape:quorum"},
            {"node_id":"system:x","class":"ai","ref":"system:x"},
        ],
        relations=[
            {
                "relation_id":"r-auth",
                "subject":"actor:a",
                "relation":"HAS_SCOPED_AUTHORITY",
                "object":"scope:s",
                "applicability":{
                    "actions":["approve"],
                    "targets":["case:1"],
                    "scopes":["scope:s"],
                    "status":"ACTIVE",
                    "valid_from":"2026-09-01T00:00:00Z",
                    "valid_until":"2026-12-31T23:59:59Z",
                    "condition_refs":[],
                },
                "source_ref":"authority:register",
                "evidence_refs":["evidence:auth"],
                "basis_refs":[],
            },
            {
                "relation_id":"r-quorum",
                "subject":"actor:a",
                "relation":"REQUIRES_CONSTRAINT",
                "object":"constraint:q",
                "applicability":{"actions":["approve"],"targets":["case:1"],"scopes":["scope:s"]},
                "constraint_ref":"stegcore:policy-shape:quorum",
                "source_ref":"policy:shape",
                "evidence_refs":["evidence:policy"],
                "basis_refs":[],
            },
            {
                "relation_id":"r-external",
                "subject":"actor:a",
                "relation":"HGAI_CONTEXT_LINK",
                "object":"system:x",
                "source_ref":"hgai:graph",
                "evidence_refs":["evidence:hgai"],
                "basis_refs":[],
            },
        ],
        coverage=[
            {
                "coverage_id":"c-auth",
                "relation":"HAS_SCOPED_AUTHORITY",
                "subject":"actor:a",
                "selector":{"actions":["approve"],"targets":["case:1"],"scopes":["scope:s"]},
                "complete":complete,
                "source_ref":"authority:register",
                "evidence_refs":["evidence:auth"],
            }
        ],
        source_refs=["authority:register","policy:shape","hgai:graph"],
    )


def fake_canonical_authority_resolver(request, *, observed_at):
    current = True if request["authority_assertions"] else (
        False if request["authority_basis_complete"] else None
    )
    disposition = "ALLOW" if current is True else ("DENY" if current is False else "FAIL_CLOSED")
    return {
        "schema":"stegcore.authority-basis-resolution.v1",
        "task_id":request["task_id"],
        "observed_at":observed_at,
        "actor_identity":request["actor_identity"],
        "actor_role":request.get("actor_role"),
        "candidate":dict(request["candidate"]),
        "disposition":disposition,
        "actor_authority_current":current,
        "delegation_current":True,
        "authority_basis_complete":request["authority_basis_complete"],
        "delegation_basis_complete":request["delegation_basis_complete"],
        "selected_authority_assertion_id":"r-auth" if current is True else None,
        "selected_delegation_assertion_id":None,
        "evidence_refs":["evidence:auth"] if current is True else [],
        "role_label_used_as_authority":False,
        "role_policy_interpreted":False,
        "authority_issued":False,
        "credential_verified":False,
        "resolution_authority":"STEGCORE_TEST_AUTHORITY_BASIS",
        "authority_effect":"NONE_RESOLUTION_ONLY",
    }


def test_recognized_relations_project_to_existing_owners_and_unknown_is_preserved():
    graph=graph_fixture()
    before=graph["graph_sha256"]
    result=project_governance_reference_graph(
        graph,
        task_id="SDK-GRG-CANONICAL-PROJECTION-CONSOLE-001",
        candidate={"action":"approve","target":"case:1","scope":"scope:s"},
        observed_at="2026-09-18T18:00:00Z",
    )
    assert graph["graph_sha256"] == before
    by_id={item["relation_id"]:item for item in result["relations"]}
    assert by_id["r-auth"]["canonical_semantic_owner"] == "StegCore.authority_basis.resolve_authority_basis"
    assert by_id["r-auth"]["projection_state"] == "RECOGNIZED_PROJECTED"
    assert by_id["r-auth"]["projected_input"]["authority_basis_complete"] is False
    assert by_id["r-quorum"]["canonical_semantic_owner"] == "StegCore.policy-shape"
    assert by_id["r-quorum"]["projection_state"] == "RECOGNIZED_PROJECTED"
    assert by_id["r-quorum"]["semantic_owner_callable"] is False
    assert by_id["r-external"]["projection_state"] == "UNKNOWN_RELATION_PRESERVED"
    assert by_id["r-external"]["authority_effect"] == "NONE_NON_AUTHORIZING_EVIDENCE_ONLY"
    assert result["live_runtime_bound"] is False


def test_authority_projection_can_be_canonically_evaluated_only_via_injected_owner():
    result=project_governance_reference_graph(
        graph_fixture(complete=False),
        task_id="SDK-GRG-CANONICAL-PROJECTION-CONSOLE-001",
        candidate={"action":"approve","target":"case:1","scope":"scope:s"},
        observed_at="2026-09-18T18:00:00Z",
        authority_resolver=fake_canonical_authority_resolver,
    )
    auth=next(item for item in result["relations"] if item["relation_id"]=="r-auth")
    assert auth["projection_state"] == "CANONICALLY_EVALUATED"
    assert auth["governance_result"]["actor_authority_current"] is True
    assert auth["governance_result"]["sdk_resolved_authority"] is False
    assert auth["transition_runtime_binding_state"] == "NOT_LIVE_RUNTIME_BOUND"


def test_incomplete_no_match_can_remain_unknown_fail_closed_through_owner_binding():
    graph=graph_fixture(complete=False)
    graph["relations"]=[r for r in graph["relations"] if r["relation_id"] != "r-auth"]
    from stegverse.governance_reference_graph import governance_reference_graph_sha256
    graph["graph_sha256"]=governance_reference_graph_sha256(graph)
    result=project_governance_reference_graph(
        graph,
        task_id="SDK-GRG-CANONICAL-PROJECTION-CONSOLE-001",
        candidate={"action":"approve","target":"case:1","scope":"scope:s"},
        observed_at="2026-09-18T18:00:00Z",
        authority_resolver=fake_canonical_authority_resolver,
    )
    assert all(item["relation_id"] != "r-auth" for item in result["relations"])
    # No authority relation means the SDK does not synthesize an authority conclusion.


def test_public_console_projects_without_claiming_runtime(tmp_path):
    path=tmp_path/"graph.json"
    path.write_text(json.dumps(graph_fixture()), encoding="utf-8")
    out=StringIO()
    with redirect_stdout(out):
        rc=graph_main([
            "--project",str(path),
            "--task-id","SDK-GRG-CANONICAL-PROJECTION-CONSOLE-001",
            "--action","approve",
            "--target","case:1",
            "--scope","scope:s",
            "--observed-at","2026-09-18T18:00:00Z",
        ])
    assert rc == 0
    payload=json.loads(out.getvalue())
    assert payload["schema"] == "stegverse.sdk.grg-semantic-projection.v1"
    assert payload["live_runtime_bound"] is False
    assert any(item["projection_state"] == "UNKNOWN_RELATION_PRESERVED" for item in payload["relations"])
