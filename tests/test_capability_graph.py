"""A declared capability set resolves to its closure and never wider."""
from copy import deepcopy

import pytest

from stegverse.capability_graph import (
    CAPABILITY_GRAPH_SCHEMA,
    CLOSURE_MEMBER_OFFLINE,
    CLOSURE_MEMBER_UNKNOWN,
    CLOSURE_RESOLVED,
    REQUIREMENT_CYCLE,
    UNDECLARED_REQUIREMENT,
    UNREACHED_DECLARATION,
    CapabilityGraphError,
    resolve_declared_capabilities,
    validate_capability_graph,
)
from stegverse.manifest_builder import PROCESSOR_ROUTES, build_manifest
from stegverse.route_resolution import PUBLISHED_ROUTES, STEGBROWSER_ROUTE_ID


def _graph(**overrides):
    graph = {
        "schema": CAPABILITY_GRAPH_SCHEMA,
        "graph_id": "acme-ingest-v1",
        "root_capability": "governance",
        "declared_capabilities": ["governance", "stegbrowser"],
        "requires": {"governance": ["stegbrowser"]},
    }
    graph.update(overrides)
    return graph


def _resolve(graph, **kwargs):
    return resolve_declared_capabilities(
        graph,
        processor_routes=PROCESSOR_ROUTES,
        published_routes=PUBLISHED_ROUTES,
        source_framework=kwargs.pop("source_framework", "acme"),
        source_output_id=kwargs.pop("source_output_id", "out-1"),
        processor_request=kwargs.pop("processor_request", {"intent": "submit"}),
        **kwargs,
    )


def _stegbrowser_request():
    outbound = "sha256:" + "a" * 64
    return {
        "schema": "stegbrowser.llm-profile-request.v1", "profile": "llm.v1",
        "prompt": "CG", "response_marker": "CG", "provider": "openai",
        "journey": {
            "schema": "stegverse.packet-carried-endpoint-receipt-journey/v1",
            "journey_id": "cg-1", "origin_endpoint": "origin",
            "ephemeral_endpoint": "ephemeral", "outbound_manifest_sha256": outbound,
            "return_manifest_sha256": "sha256:" + "b" * 64,
            "return_predecessor_manifest_sha256": outbound,
        },
    }


def test_declared_closure_resolves_to_its_installed_routes():
    result = _resolve(_graph())
    assert result["verdict"] == CLOSURE_RESOLVED
    assert result["resolved"] is True
    assert result["closure"] == ["governance", "stegbrowser"]
    assert result["route_ids"] == [
        PROCESSOR_ROUTES["governance"], PROCESSOR_ROUTES["stegbrowser"]
    ]
    assert result["next_action"] == "BUILD_AND_SUBMIT_MANIFEST"


def test_a_requirement_the_declaration_omitted_is_fail_closed():
    """Declaring a capability does not declare what it needs."""
    result = _resolve(_graph(declared_capabilities=["governance"]))
    assert result["verdict"] == UNDECLARED_REQUIREMENT
    assert result["defect_detail"] == "stegbrowser"
    assert result["resolved"] is False
    assert result["closure"] == []


def test_a_declared_capability_the_root_never_reaches_is_fail_closed():
    """Excess declaration is a defect: a submitter cannot park capabilities."""
    result = _resolve(_graph(requires={}))
    assert result["verdict"] == UNREACHED_DECLARATION
    assert result["defect_detail"] == "stegbrowser"
    assert result["resolved"] is False


def test_requirement_cycle_is_fail_closed():
    result = _resolve(_graph(
        root_capability="governance",
        declared_capabilities=["governance", "stegbrowser"],
        requires={"governance": ["stegbrowser"], "stegbrowser": ["governance"]},
    ))
    assert result["verdict"] == REQUIREMENT_CYCLE
    assert "governance" in result["defect_detail"]
    assert result["resolved"] is False


def test_unknown_member_requests_development_and_does_not_resolve():
    result = _resolve(_graph(
        declared_capabilities=["governance", "future_thing"],
        requires={"governance": ["future_thing"]},
    ))
    assert result["verdict"] == CLOSURE_MEMBER_UNKNOWN
    assert result["unknown_members"] == ["future_thing"]
    assert result["resolved"] is False
    requests = result["capability_development_requests"]
    assert [r["requested_capability"] for r in requests] == ["future_thing"]
    assert requests[0]["request_granted_authority"] is False
    assert requests[0]["original_processor_request"] == {"intent": "submit"}


def test_one_offline_member_leaves_the_whole_closure_unresolved(monkeypatch):
    original = deepcopy(PUBLISHED_ROUTES[STEGBROWSER_ROUTE_ID])
    monkeypatch.setitem(
        PUBLISHED_ROUTES, STEGBROWSER_ROUTE_ID, {**original, "runtime_installed": False}
    )
    result = _resolve(_graph())
    assert result["verdict"] == CLOSURE_MEMBER_OFFLINE
    assert result["offline_members"] == ["stegbrowser"]
    assert result["resolved"] is False


def test_resolution_is_bound_to_the_declaration_that_produced_it():
    first = _resolve(_graph())
    second = _resolve(_graph(graph_id="other-graph-v1"))
    assert first["coverage"]["covers_graph_id"] == "acme-ingest-v1"
    assert second["coverage"]["covers_graph_id"] == "other-graph-v1"
    assert (
        first["coverage"]["covers_declaration_sha256"]
        != second["coverage"]["covers_declaration_sha256"]
    )


def test_closure_component_ids_follow_the_joint_relation_convention():
    result = _resolve(_graph())
    assert result["closure_component_ids"] == [
        "acme-ingest-v1:governance", "acme-ingest-v1:stegbrowser"
    ]


def test_resolution_never_grants_authority():
    result = _resolve(_graph())
    assert result["authority_effect"] == "NONE_RESOLUTION_ONLY"
    boundary = result["authority_boundary"]
    assert boundary["declaration_creates_capability"] is False
    assert boundary["closure_membership_grants_execution"] is False
    assert boundary["resolution_grants_authority"] is False
    assert boundary["wider_closure_admits_undeclared_member"] is False
    assert boundary["sdk_substitutes_unresolved_member"] is False


@pytest.mark.parametrize("graph", [
    {"schema": "wrong.schema.v1", "graph_id": "g", "root_capability": "governance",
     "declared_capabilities": ["governance"], "requires": {}},
    {"schema": CAPABILITY_GRAPH_SCHEMA, "graph_id": "g", "root_capability": "governance",
     "declared_capabilities": [], "requires": {}},
    {"schema": CAPABILITY_GRAPH_SCHEMA, "graph_id": "g", "root_capability": "governance",
     "declared_capabilities": ["governance"], "requires": {"governance": ["governance"]}},
    {"schema": CAPABILITY_GRAPH_SCHEMA, "graph_id": "g", "root_capability": "governance",
     "declared_capabilities": ["governance"], "requires": {}, "install": True},
])
def test_structural_defects_raise(graph):
    with pytest.raises(CapabilityGraphError):
        validate_capability_graph(graph)


def test_declaration_is_normalized_case_insensitively_and_deduplicated():
    graph = validate_capability_graph(_graph(
        declared_capabilities=["Governance", "STEGBROWSER", "governance"],
        requires={"Governance": ["StegBrowser"]},
    ))
    assert graph["declared_capabilities"] == ["governance", "stegbrowser"]
    assert graph["requires"] == {"governance": ["stegbrowser"]}


def test_builder_binds_a_resolved_closure_into_the_manifest():
    graph = _graph(root_capability="stegbrowser",
                   declared_capabilities=["stegbrowser"], requires={})
    manifest = build_manifest(
        data={"x": 1}, source_framework="acme", source_output_id="cg-bind",
        processor_request=_stegbrowser_request(), process="stegbrowser",
        capability_graph=graph,
    )
    bound = manifest["extensions"]["capability_graph"]
    assert bound["verdict"] == CLOSURE_RESOLVED
    assert bound["closure"] == ["stegbrowser"]
    assert manifest["processing"]["capability"] == "stegbrowser"


def test_builder_refuses_to_emit_a_manifest_for_an_unresolved_closure():
    graph = _graph(root_capability="stegbrowser",
                   declared_capabilities=["stegbrowser", "future_thing"],
                   requires={"stegbrowser": ["future_thing"]})
    result = build_manifest(
        data={"x": 1}, source_framework="acme", source_output_id="cg-unresolved",
        processor_request=_stegbrowser_request(), process="stegbrowser",
        capability_graph=graph,
    )
    assert result["state"] == "CAPABILITY_CLOSURE_UNRESOLVED"
    assert result["capability_closure"]["verdict"] == CLOSURE_MEMBER_UNKNOWN
    assert "processing" not in result
    assert result["authority_effect"] == "NONE_RESOLUTION_ONLY"


def test_builder_rejects_a_graph_root_that_disagrees_with_the_declared_capability():
    with pytest.raises(ValueError, match="does not match declared processing capability"):
        build_manifest(
            data={"x": 1}, source_framework="acme", source_output_id="cg-mismatch",
            processor_request=_stegbrowser_request(), process="stegbrowser",
            capability_graph=_graph(root_capability="governance",
                                    declared_capabilities=["governance"], requires={}),
        )


def test_requires_key_that_is_not_a_declared_capability_raises():
    with pytest.raises(CapabilityGraphError, match="not a declared capability"):
        validate_capability_graph(_graph(requires={
            "governance": ["stegbrowser"], "orphan": ["stegbrowser"],
        }))


def test_a_shared_requirement_appears_once_in_the_closure():
    """A diamond resolves; the shared member is not visited twice."""
    result = _resolve(_graph(
        root_capability="governance",
        declared_capabilities=[
            "governance", "purpose_bound_worker", "atomic_task_worker", "stegbrowser",
        ],
        requires={
            "governance": ["purpose_bound_worker", "atomic_task_worker"],
            "purpose_bound_worker": ["stegbrowser"],
            "atomic_task_worker": ["stegbrowser"],
        },
    ))
    assert result["verdict"] == CLOSURE_RESOLVED
    assert result["closure"] == [
        "atomic_task_worker", "governance", "purpose_bound_worker", "stegbrowser",
    ]
    assert len(result["closure"]) == len(set(result["closure"]))


def test_a_deep_declaration_resolves_without_recursing_to_its_depth():
    """The declaration is untrusted input; its depth must not reach the SDK stack."""
    depth = 5000
    names = [f"cap_{i:05d}" for i in range(depth)]
    graph = _graph(
        root_capability=names[0],
        declared_capabilities=list(names),
        requires={names[i]: [names[i + 1]] for i in range(depth - 1)},
    )
    result = _resolve(graph)
    # Every member is unknown to the SDK, which is the point: the walk completed
    # and classified the whole chain instead of exhausting the interpreter stack.
    assert result["verdict"] == CLOSURE_MEMBER_UNKNOWN
    assert len(result["closure"]) == depth
    assert len(result["unknown_members"]) == depth


def test_a_deep_cycle_is_reported_rather_than_overflowing():
    depth = 5000
    names = [f"cap_{i:05d}" for i in range(depth)]
    requires = {names[i]: [names[i + 1]] for i in range(depth - 1)}
    requires[names[-1]] = [names[0]]
    result = _resolve(_graph(
        root_capability=names[0], declared_capabilities=list(names), requires=requires,
    ))
    assert result["verdict"] == REQUIREMENT_CYCLE
    assert result["resolved"] is False
