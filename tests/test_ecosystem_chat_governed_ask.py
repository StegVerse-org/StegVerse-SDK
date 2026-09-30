"""A question in Ecosystem Chat, answered by N LLMs, governed and replayable.

This is Test 6 as a product path: one question fans to several branches, each
calling a different LLM, and the answers compose into one governed response the
asker can verify. No GitHub Actions worker is in the path -- the fan runs in the
SDK and the LLM interaction stays with the StegBrowser owner behind an injected
executor.

The executor here is built from StegBrowser's own begin/bind/complete functions
where that checkout is present, so the components and their four-per-branch
endpoint receipts are authentic rather than shaped to match what the SDK wants.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any, Dict, List, Mapping

import pytest

from stegverse.ecosystem_chat_ask import (
    ANSWER_SCHEMA,
    ANSWER_VERIFICATION_FIELDS,
    DISPOSITION_ANSWERED,
    DISPOSITION_FAN_INCOMPLETE,
    EcosystemChatAskError,
    answer_summary,
    ask_governed_question,
    build_ask_manifest,
    plan_ask_journey,
    verify_planned_journey,
)
from stegverse.governed_composite_response import (
    JOINT_RELATION_SCHEMA,
    STRATEGY_ATTRIBUTED_SET,
    STRATEGY_MAJORITY,
)
from stegverse.governed_llm_fan import (
    FAILURE_BRANCH_EXECUTION,
    FAILURE_BRANCH_RESULT_SHAPE,
    RECEIPTS_PER_BRANCH,
    STATUS_COMPLETED,
    STATUS_FAILED,
    STATUS_NOT_ATTEMPTED,
    GovernedLlmFanError,
    branch_operations,
    mint_branch_lease,
    run_governed_llm_fan,
)
from stegverse.stegbrowser_processor import JOURNEY_SCHEMA_V2, derive_state_graph

QUESTION = "What does StegVerse govern at the execution boundary?"
ANSWER = "It governs decision verification at the execution boundary."

#: Checkout locations, used only when the owner is not installed. StegBrowser
#: carries no packaging metadata, so a checkout is currently the only way to
#: reach it; the CI workflow makes one when a read token is available.
_BROWSER_PATHS = (
    Path("/home/user/stegbrowser/src/stegbrowser/llm_profile.py"),
    Path(__file__).resolve().parents[2] / "stegbrowser/src/stegbrowser/llm_profile.py",
    # The path the test-suite-ratchet workflow checks the owner out to.
    Path.cwd() / "_stegbrowser_owner/src/stegbrowser/llm_profile.py",
)


def _installed_browser_profile() -> Path | None:
    """Locate the installed owner's llm_profile.py without importing the package.

    The package's __init__ pulls chromium, publicsuffix2 and playwright, none of
    which this module needs. find_spec resolves the package directory without
    executing it, so the profile loads from an installed owner as cheaply as
    from a checkout.
    """
    try:
        spec = importlib.util.find_spec("stegbrowser")
    except (ImportError, ValueError):
        return None
    for location in list(getattr(spec, "submodule_search_locations", None) or []):
        candidate = Path(location) / "llm_profile.py"
        if candidate.exists():
            return candidate
    return None


def _load_browser():
    """Load the StegBrowser owner's profile: installed package, then checkout.

    Preferring the installed package is what lets CI run these tests at all.
    The owner ships in the `owner-test` extra; before it did, every test needing
    it skipped, and the suite looked greener than it was.
    """
    installed = _installed_browser_profile()
    for path in ((installed,) if installed else ()) + _BROWSER_PATHS:
        if path is None or not path.exists():
            continue
        spec = importlib.util.spec_from_file_location("_sb_profile_ask", path)
        if spec is None or spec.loader is None:
            continue
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    return None


BROWSER = _load_browser()
DIGEST = {k: f"sha256:{c * 64}" for k, c in
          {"o0": "a", "r0": "b", "o1": "c", "r1": "d", "o2": "e", "r2": "f"}.items()}


def _branch(branch_id: str, provider: str, model: str, out: str, ret: str) -> Dict[str, Any]:
    return {
        "branch_id": branch_id,
        "ephemeral_endpoint": f"stegbrowser:ephemeral:{branch_id}",
        "outbound_manifest_sha256": out,
        "return_manifest_sha256": ret,
        "return_predecessor_manifest_sha256": out,
        "provider": provider,
        "model": model,
        "response_marker": f"MARKER-{branch_id}",
        "secure_url": f"https://{branch_id}.example.test/chat",
        "browser_actions": [{"action": "read_text", "selector": "#answer"}],
    }


def journey(branch_count: int = 3) -> Dict[str, Any]:
    rows = [
        _branch("b0", "anthropic", "claude-opus", DIGEST["o0"], DIGEST["r0"]),
        _branch("b1", "openai", "gpt", DIGEST["o1"], DIGEST["r1"]),
        _branch("b2", "google", "gemini", DIGEST["o2"], DIGEST["r2"]),
    ][:branch_count]
    return {
        "schema": JOURNEY_SCHEMA_V2,
        "journey_id": "chat-ask-fan",
        "origin_endpoint": "stegverse:ecosystem-chat",
        "branches": rows,
    }


def browser_executor(answers: Mapping[str, str] | None = None):
    """An executor with StegBrowser's own signature and return shape."""
    if BROWSER is None:
        pytest.skip("StegBrowser checkout not present")

    def execute(request: Mapping[str, Any], lease: Mapping[str, Any]) -> Dict[str, Any]:
        assert lease["schema"] == "stegbrowser.ecosystem-ephemeral-lease.v1"
        normalized = BROWSER.validate_llm_profile_request(request)
        marker = normalized["response_marker"]
        branch_id = str(normalized["journey"]["journey_id"]).rsplit(":", 1)[-1]
        text = (answers or {}).get(branch_id, ANSWER)
        packet = BROWSER.begin_llm_profile_packet(normalized)
        bound = BROWSER.bind_llm_profile_result(
            packet=packet, response_text=f"{text} {marker}",
            provider=normalized["provider"], model=normalized["model"],
        )
        completed = BROWSER.complete_llm_profile_packet({**bound, "request": normalized})
        return {"result": completed["result"],
                "endpoint_receipts": completed["endpoint_receipts"]}

    return execute


VALID_RELATION = {
    "schema": JOINT_RELATION_SCHEMA,
    "relation_status": "validated",
    "relation_id": "REL-CHAT-ASK-001",
    "authority_source": "KV/SKAP Vault",
    "evidence_posture": "receipt_backed",
    "replay_posture": "receipt_backed",
}


def _ask(**kwargs):
    kwargs.setdefault("executor", browser_executor())
    kwargs.setdefault("joint_relation", VALID_RELATION)
    return ask_governed_question(QUESTION, journey(), **kwargs)


# --- the worker is not in the path -------------------------------------------


def test_the_sdk_runs_the_fan_with_no_worker_in_the_path() -> None:
    answer = _ask()
    assert answer["worker_in_path"] is False
    assert answer["branch_count"] == 3
    assert [row["status"] for row in answer["branches"]] == [STATUS_COMPLETED] * 3


def test_each_branch_leases_its_own_ephemeral_session() -> None:
    graph = derive_state_graph(build_ask_manifest(QUESTION, journey()))
    operations = branch_operations(graph)
    leases = [
        mint_branch_lease(op, fan_id="FANID", index=i, requester="test")
        for i, op in enumerate(operations, start=1)
    ]
    assert len({lease["lease_id"] for lease in leases}) == 3
    for lease in leases:
        assert lease["persistent_profile"] is False
        assert lease["persist_cookies"] is False
        assert len(lease["allowed_origins"]) == 1


def test_a_branch_journey_id_is_qualified_so_receipts_are_attributable() -> None:
    graph = derive_state_graph(build_ask_manifest(QUESTION, journey()))
    ids = [op["journey"]["journey_id"] for op in branch_operations(graph)]
    assert ids == ["chat-ask-fan:b0", "chat-ask-fan:b1", "chat-ask-fan:b2"]


def test_the_fan_collects_four_endpoint_receipts_per_branch() -> None:
    answer = _ask()
    assert answer["required_endpoint_receipts"] == RECEIPTS_PER_BRANCH * 3
    assert answer["observed_endpoint_receipts"] == RECEIPTS_PER_BRANCH * 3
    assert answer["fan_complete"] is True


WIRE_FIXTURE = (Path(__file__).resolve().parent
                / "fixtures/stegbrowser_branch_operations_wire_v1.json")


def _canonical(value: Any) -> str:
    import json as _json

    return _json.dumps(value, sort_keys=True, separators=(",", ":"))


def test_sdk_branch_requests_match_the_frozen_worker_wire_format() -> None:
    """The replay-compatibility guarantee, outliving the worker it came from.

    The GitHub Actions worker that used to execute the fan produced these exact
    branch requests, and the fixture was captured from it while it still existed
    -- only after asserting the two agreed. Comparing against the fixture keeps
    the guarantee once the worker is gone, and unlike a live comparison it runs
    everywhere rather than only where a .github checkout happens to sit.
    """
    import json as _json

    frozen = _json.loads(WIRE_FIXTURE.read_text(encoding="utf-8"))
    graph = derive_state_graph(build_ask_manifest(QUESTION, journey()))
    assert _canonical(branch_operations(graph)) == _canonical(frozen["branch_operations"])


def test_the_frozen_wire_fixture_says_where_it_came_from() -> None:
    """A frozen expectation nobody can trace is just a magic number."""
    import json as _json

    frozen = _json.loads(WIRE_FIXTURE.read_text(encoding="utf-8"))
    assert "_branch_operations" in frozen["captured_from"]
    assert frozen["why"]
    assert frozen["authority_effect"] == "NONE"


def test_sdk_branch_requests_still_match_the_live_worker_where_it_exists() -> None:
    """Belt and braces while both exist; skips once the worker is removed."""
    worker_path = Path("/home/user/.github/workers/manifest_state_transition_intr_ingress.py")
    if not worker_path.exists():
        pytest.skip("worker removed or .github checkout not present")
    for extra in ("/home/user/.github", "/home/user/.github/workers"):
        if extra not in sys.path:
            sys.path.insert(0, extra)
    spec = importlib.util.spec_from_file_location("_fan_worker", worker_path)
    if spec is None or spec.loader is None:
        pytest.skip("worker module not loadable")
    worker = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(worker)
    except Exception:  # its own runtime deps are not this repo's concern
        pytest.skip("worker module dependencies unavailable")

    graph = derive_state_graph(build_ask_manifest(QUESTION, journey()))
    assert _canonical(branch_operations(graph)) == _canonical(worker._branch_operations(graph))


# --- a question becomes one governed, replayable answer ----------------------


def test_three_llms_agreeing_produce_one_governed_answer() -> None:
    answer = _ask()
    assert answer["schema"] == ANSWER_SCHEMA
    assert answer["disposition"] == DISPOSITION_ANSWERED
    assert answer["governed_claim"] is True
    assert answer["answer"] == ANSWER
    assert answer["question"] == QUESTION


def test_the_answer_replays_from_its_own_components() -> None:
    answer = _ask()
    assert answer["replay"]["reconstruction_status"] == "RECONSTRUCTED"
    assert (answer["replay"]["reconstructed_composite_sha256"]
            == answer["composite"]["composite_sha256"])


def test_the_summary_carries_what_a_phone_needs_to_check_the_answer() -> None:
    summary = answer_summary(_ask())
    assert summary["answer"] == ANSWER
    assert summary["reconstruction_status"] == "RECONSTRUCTED"
    assert summary["composite_sha256"] == summary["reconstructed_composite_sha256"]
    assert sorted(summary["models_asked"]) == [
        "anthropic/claude-opus", "google/gemini", "openai/gpt"]
    assert summary["agreement_is_evidence_of_correctness"] is False


def test_every_named_verification_field_exists_on_a_real_answer() -> None:
    answer = _ask()
    available = dict(answer["composite"])
    available.update(answer["replay"])
    missing = [f for f in ANSWER_VERIFICATION_FIELDS if f not in available]
    assert missing == [], f"the asker is told to compare fields that do not exist: {missing}"


def test_chat_neither_builds_the_manifest_nor_picks_the_answer() -> None:
    answer = _ask()
    assert answer["chat_builds_manifest"] is False
    assert answer["chat_selects_answer"] is False
    assert answer["composite"]["boundary"]["composition_synthesizes_new_text"] is False


def test_disagreement_does_not_yield_a_governed_answer_under_unanimity() -> None:
    answer = _ask(executor=browser_executor({"b2": "Something entirely different."}))
    assert answer["governed_claim"] is False
    assert answer["answer"] is None
    assert answer["composite"]["distinct_answer_count"] == 2


def test_majority_answers_while_reporting_the_dissent() -> None:
    answer = _ask(executor=browser_executor({"b2": "Something entirely different."}),
                  strategy=STRATEGY_MAJORITY)
    assert answer["answer"] == ANSWER
    support = sorted(g["support_count"] for g in answer["composite"]["answer_groups"])
    assert support == [1, 2]


def test_attributed_set_returns_every_answer_and_selects_none() -> None:
    answer = _ask(executor=browser_executor({"b2": "Something entirely different."}),
                  strategy=STRATEGY_ATTRIBUTED_SET)
    assert answer["answer"] is None
    assert answer["composite"]["distinct_answer_count"] == 2


def test_without_a_validated_joint_relation_the_answer_is_not_a_governed_claim() -> None:
    answer = _ask(joint_relation=None)
    assert answer["governed_claim"] is False
    # The answer is still produced, attributed and replayable.
    assert answer["answer"] == ANSWER
    assert answer["replay"]["reconstruction_status"] == "RECONSTRUCTED"


# --- a partial fan never becomes an answer ----------------------------------


def _flaky_executor():
    calls = {"n": 0}
    working = browser_executor()

    def flaky(request: Mapping[str, Any], lease: Mapping[str, Any]) -> Dict[str, Any]:
        calls["n"] += 1
        if calls["n"] == 2:
            raise RuntimeError("ephemeral session lost")
        return working(request, lease)

    return flaky


def test_a_failed_branch_leaves_the_fan_incomplete_and_uncomposed() -> None:
    answer = _ask(executor=_flaky_executor())
    assert answer["disposition"] == DISPOSITION_FAN_INCOMPLETE
    assert answer["answer"] is None
    assert answer["composite"] is None
    assert answer["failure"]["failure_code"] == FAILURE_BRANCH_EXECUTION
    assert answer["boundary"]["composed_from_a_partial_fan"] is False


def test_branches_already_executed_keep_their_receipts() -> None:
    fan = run_governed_llm_fan(
        build_ask_manifest(QUESTION, journey()), executor=_flaky_executor())
    statuses = [row["status"] for row in fan["branches"]]
    assert statuses == [STATUS_COMPLETED, STATUS_FAILED, STATUS_NOT_ATTEMPTED]
    assert fan["observed_endpoint_receipts"] == RECEIPTS_PER_BRANCH
    assert fan["required_endpoint_receipts"] == RECEIPTS_PER_BRANCH * 3
    assert fan["complete"] is False


def test_an_executor_returning_the_wrong_shape_fails_closed() -> None:
    fan = run_governed_llm_fan(
        build_ask_manifest(QUESTION, journey()),
        executor=lambda request, lease: {"nope": True},
    )
    assert fan["complete"] is False
    assert fan["failure"]["failure_code"] == FAILURE_BRANCH_RESULT_SHAPE


def test_a_missing_stegbrowser_dependency_fails_closed_with_a_repair(monkeypatch) -> None:
    """No executor supplied and the owner package unimportable.

    The fan must name the dependency and its repair, not reach into a sibling
    checkout the way the worker did.
    """
    import stegverse.governed_llm_fan as fan_module

    # Setting a module to None in sys.modules makes importing it raise.
    monkeypatch.setitem(sys.modules, "stegbrowser.llm_browser_execution", None)
    monkeypatch.setitem(sys.modules, "stegbrowser", None)

    with pytest.raises(GovernedLlmFanError) as caught:
        fan_module._resolve_executor(None)
    message = str(caught.value)
    assert fan_module.FAILURE_EXECUTOR_UNAVAILABLE in message
    assert "stegbrowser" in message and "executor=" in message


def test_the_default_executor_is_only_used_when_none_is_supplied(monkeypatch) -> None:
    """A supplied executor must never trigger the owner import."""
    import stegverse.governed_llm_fan as fan_module

    monkeypatch.setitem(sys.modules, "stegbrowser.llm_browser_execution", None)
    monkeypatch.setitem(sys.modules, "stegbrowser", None)
    supplied = browser_executor()
    assert fan_module._resolve_executor(supplied) is supplied


# --- request shape and refusals ---------------------------------------------


def test_one_branch_is_not_a_governed_answer() -> None:
    with pytest.raises(EcosystemChatAskError):
        ask_governed_question(QUESTION, journey(branch_count=1),
                              executor=browser_executor())


def test_an_empty_question_is_refused() -> None:
    with pytest.raises(EcosystemChatAskError):
        ask_governed_question("   ", journey(), executor=browser_executor())


def test_a_v1_journey_is_not_an_ask_fan() -> None:
    with pytest.raises(EcosystemChatAskError):
        ask_governed_question(
            QUESTION,
            {"schema": "stegverse.packet-carried-endpoint-receipt-journey/v1"},
            executor=browser_executor(),
        )


def test_an_undeclared_strategy_is_refused() -> None:
    with pytest.raises(EcosystemChatAskError):
        ask_governed_question(QUESTION, journey(), strategy="WHATEVER",
                              executor=browser_executor())


def test_the_ask_declares_its_stated_return_planning_basis() -> None:
    answer = _ask()
    assert answer["journey_planning"]["basis"] == "STATED_RETURN_INTERLOCK_INTR"
    assert "predecessor-links" in answer["journey_planning"]["detail"]


# --- the journey is plannable because the return is stated, not observed -----

ROUTES = [
    {"provider": "anthropic", "model": "claude-opus",
     "secure_url": "https://a.example.test/chat",
     "browser_actions": [{"action": "read_text", "selector": "#out"}]},
    {"provider": "openai", "model": "gpt",
     "secure_url": "https://b.example.test/chat",
     "browser_actions": [{"action": "read_text", "selector": "#out"}]},
    {"provider": "google", "model": "gemini",
     "secure_url": "https://c.example.test/chat",
     "browser_actions": [{"action": "read_text", "selector": "#out"}]},
]


def test_a_question_and_its_routes_plan_a_whole_journey() -> None:
    """The ASK is the manifested packet with its return already stated, so
    nothing has to be observed before the journey can be planned."""
    planned = plan_ask_journey(QUESTION, ROUTES, fan_journey_id="ask-plan")
    assert len(planned["branches"]) == 3
    assert planned["planning_basis"] == "STATED_RETURN_INTERLOCK_INTR"
    for branch in planned["branches"]:
        assert branch["return_predecessor_manifest_sha256"] == branch["outbound_manifest_sha256"]
        assert branch["return_manifest_sha256"] != branch["outbound_manifest_sha256"]


def test_every_planned_digest_is_a_hash_of_a_real_document() -> None:
    """Not placeholders: each digest recomputes from the manifest it commits to."""
    planned = plan_ask_journey(QUESTION, ROUTES, fan_journey_id="ask-plan")
    report = verify_planned_journey(planned)
    assert report["verified"] is True
    for row in report["branches"]:
        assert row["outbound_matches"] and row["return_matches"]
        assert row["return_predecessor_links"]


def test_a_tampered_stated_return_breaks_its_commitment() -> None:
    """The stated return is a commitment only if changing it is detectable."""
    planned = plan_ask_journey(QUESTION, ROUTES, fan_journey_id="ask-plan")
    planned["planned_manifests"][1]["outbound_manifest"]["stated_return"][
        "response_marker"] = "SOMETHING-ELSE"
    report = verify_planned_journey(planned)
    assert report["verified"] is False
    assert report["branches"][1]["outbound_matches"] is False


def test_planned_branches_are_distinct_per_route() -> None:
    planned = plan_ask_journey(QUESTION, ROUTES, fan_journey_id="ask-plan")
    for field in ("outbound_manifest_sha256", "return_manifest_sha256",
                  "response_marker", "ephemeral_endpoint"):
        values = [b[field] for b in planned["branches"]]
        assert len(set(values)) == len(values), field


def test_the_same_question_and_routes_plan_the_same_journey() -> None:
    """Replay needs planning to be deterministic."""
    first = plan_ask_journey(QUESTION, ROUTES, fan_journey_id="ask-plan")
    second = plan_ask_journey(QUESTION, ROUTES, fan_journey_id="ask-plan")
    assert first == second


def test_a_different_question_plans_different_commitments() -> None:
    first = plan_ask_journey(QUESTION, ROUTES, fan_journey_id="ask-plan")
    other = plan_ask_journey("A different question entirely?", ROUTES,
                             fan_journey_id="ask-plan")
    assert ([b["outbound_manifest_sha256"] for b in first["branches"]]
            != [b["outbound_manifest_sha256"] for b in other["branches"]])


def test_a_planned_journey_answers_the_question_end_to_end() -> None:
    planned = plan_ask_journey(QUESTION, ROUTES, fan_journey_id="ask-plan")
    answer = ask_governed_question(
        QUESTION, planned, executor=browser_executor(), joint_relation=VALID_RELATION)
    assert answer["disposition"] == DISPOSITION_ANSWERED
    assert answer["answer"] == ANSWER
    assert answer["observed_endpoint_receipts"] == RECEIPTS_PER_BRANCH * 3
    assert answer["replay"]["reconstruction_status"] == "RECONSTRUCTED"


def test_one_route_cannot_plan_a_governed_answer() -> None:
    with pytest.raises(EcosystemChatAskError):
        plan_ask_journey(QUESTION, ROUTES[:1], fan_journey_id="ask-plan")


def test_a_route_missing_its_endpoint_is_refused() -> None:
    with pytest.raises(EcosystemChatAskError):
        plan_ask_journey(QUESTION, [ROUTES[0], {"provider": "x", "model": "y"}],
                         fan_journey_id="ask-plan")


# --- the device is interchangeable ------------------------------------------


def test_the_fan_is_performed_by_a_registered_node_not_a_device() -> None:
    """Any browser UI running Ecosystem Chat is itself a StegBrowser node."""
    node = _ask()["node"]
    assert node["executed_by"] == "REGISTERED_NODE_RUNNING_CHAT"
    assert node["any_browser_running_chat_is_a_stegbrowser_node"] is True
    assert node["device_identity_gate"] == "NONE_PROHIBITED"
    assert node["transportability_conferred_by"] == "NODE_REGISTRATION"
    assert node["transportability_conferred_by_device"] is False


def test_the_node_never_becomes_the_user_verifier() -> None:
    node = _ask()["node"]
    assert node["node_confers_user_verifier_authority"] is False
    assert node["user_verification_authority"] == "KV/SKAP Vault"


def test_no_operation_result_is_gated_on_a_device() -> None:
    from stegverse.ecosystem_chat_entry import ASK, RECONSTRUCT, SCHEMA
    from stegverse.ecosystem_chat_operations import handle_chat_entry

    _, served = handle_chat_entry(
        {"schema": SCHEMA, "operation": ASK, "question": QUESTION, "journey": journey()},
        executor=browser_executor(), joint_relation=VALID_RELATION)
    _, unserved = handle_chat_entry(
        {"schema": SCHEMA, "operation": RECONSTRUCT,
         "manifest_receipt_id": "MR-A1B2C3D4E5F60718"})
    for result in (served, unserved):
        assert result["device_identity_gate"] == "NONE_PROHIBITED"
    assert served["performed_by"] == "REGISTERED_NODE_RUNNING_CHAT"


# --- reachable through the Chat surface, not only from the SDK ---------------


def test_a_question_posted_to_the_chat_endpoint_returns_a_governed_answer() -> None:
    """The gap this closes: the surface used to serve no operation at all."""
    import json as _json

    from stegverse.ecosystem_chat_entry import ASK, SCHEMA
    from stegverse.ecosystem_chat_http import ECOSYSTEM_CHAT_PATH
    from stegverse.ecosystem_chat_pipeline_http import handle_ecosystem_chat_pipeline_http

    body = _json.dumps({
        "schema": SCHEMA, "operation": ASK,
        "question": QUESTION, "journey": journey(),
    })
    status, result = handle_ecosystem_chat_pipeline_http(
        "POST", ECOSYSTEM_CHAT_PATH, body,
        executor=browser_executor(), joint_relation=VALID_RELATION,
    )
    assert status == 200
    assert result["served"] is True
    assert result["capability"] == "ASK_GOVERNED_QUESTION"
    assert result["summary"]["answer"] == ANSWER
    assert result["summary"]["reconstruction_status"] == "RECONSTRUCTED"


def test_the_historical_pipeline_payload_keeps_its_behaviour() -> None:
    """An operation was added to the surface; nothing was taken from it."""
    import json as _json

    from stegverse.ecosystem_chat_http import ECOSYSTEM_CHAT_PATH
    from stegverse.ecosystem_chat_pipeline_http import handle_ecosystem_chat_pipeline_http

    status, result = handle_ecosystem_chat_pipeline_http(
        "POST", ECOSYSTEM_CHAT_PATH, _json.dumps({"not": "an entry request"}))
    # Still the pipeline shape, not an operation result.
    assert "intake" in result
    assert status in {202, 422}


def test_an_operation_the_surface_does_not_serve_says_so_rather_than_stubbing() -> None:
    from stegverse.ecosystem_chat_entry import RECONSTRUCT, SCHEMA
    from stegverse.ecosystem_chat_operations import NOT_SERVED, handle_chat_entry

    status, result = handle_chat_entry({
        "schema": SCHEMA, "operation": RECONSTRUCT,
        "manifest_receipt_id": "MR-A1B2C3D4E5F60718",
    })
    assert status == 501
    assert result["served"] is False
    assert result["disposition"] == NOT_SERVED
    assert result["required_evidence_or_repair"]
    # It still projects onto the console request that does serve it.
    assert result["console_equivalent_request"]["selection"] == RECONSTRUCT


def test_a_disagreeing_fan_answers_the_surface_with_422_not_a_fabricated_answer() -> None:
    import json as _json

    from stegverse.ecosystem_chat_entry import ASK, SCHEMA
    from stegverse.ecosystem_chat_http import ECOSYSTEM_CHAT_PATH
    from stegverse.ecosystem_chat_pipeline_http import handle_ecosystem_chat_pipeline_http

    body = _json.dumps({
        "schema": SCHEMA, "operation": ASK,
        "question": QUESTION, "journey": journey(),
    })
    status, result = handle_ecosystem_chat_pipeline_http(
        "POST", ECOSYSTEM_CHAT_PATH, body,
        executor=browser_executor({"b2": "Something entirely different."}),
        joint_relation=VALID_RELATION,
    )
    assert status == 422
    assert result["summary"]["answer"] is None
    assert result["summary"]["distinct_answer_count"] == 2
