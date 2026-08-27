import json
import sys
import types
from dataclasses import dataclass
from pathlib import Path


FIXTURE = Path(__file__).resolve().parents[1] / "stegverse" / "demo_data" / "manifold_governance_reviewable.json"


@dataclass(frozen=True)
class FakeAction:
    state: str
    continue_transition_ids: tuple[str, ...]
    review_transition_ids: tuple[str, ...]
    held_transition_ids: tuple[str, ...]
    denied_transition_ids: tuple[str, ...]
    fail_closed_transition_ids: tuple[str, ...]
    reviewable_projection: dict
    external_execution_performed: bool = False
    authority_effect: str = "NONE_UNTIL_SEPARATE_GOVERNED_COMMIT"


class FakeRequest:
    @classmethod
    def model_validate(cls, value):
        return {"canonical_request": dict(value)}


class FakePopulationTransition:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def _install_fake_canonical_runtime(monkeypatch, calls):
    stegcore = types.ModuleType("stegcore")
    manifold = types.ModuleType("stegcore.manifold_governance")
    steggate = types.ModuleType("stegcore.steggate")

    def govern_manifold_action(transitions, *, authority_boundary_refs=()):
        rows = tuple(transitions)
        calls.append(
            {
                "transition_ids": tuple(row.transition_id for row in rows),
                "authority_boundary_refs": tuple(authority_boundary_refs),
            }
        )
        return FakeAction(
            state="REVIEWABLE",
            continue_transition_ids=("T-SENSOR-A", "T-SENSOR-B"),
            review_transition_ids=("T-PROTECTED-RELEASE",),
            held_transition_ids=("T-AFTER-REVIEW",),
            denied_transition_ids=(),
            fail_closed_transition_ids=(),
            reviewable_projection={
                "schema": "stegcore.governed-manifold-projection.v1",
                "governance_invariants": {
                    "human_in_the_loop_timing_is_governance_authority": False,
                    "wall_clock_is_governance_authority": False,
                    "heartbeat_is_governance_authority": False,
                    "linear_transition_path_required": False,
                    "machine_speed_internal_transitions_may_continue_inside_existing_authority": True,
                    "protected_boundary_crossing_requires_external_authority": True,
                },
            },
        )

    manifold.PopulationTransition = FakePopulationTransition
    manifold.govern_manifold_action = govern_manifold_action
    steggate.AdmissibilityRequest = FakeRequest

    monkeypatch.setitem(sys.modules, "stegcore", stegcore)
    monkeypatch.setitem(sys.modules, "stegcore.manifold_governance", manifold)
    monkeypatch.setitem(sys.modules, "stegcore.steggate", steggate)


def _fixture():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_sdk_is_a_thin_client_of_canonical_production_runtime(monkeypatch):
    calls = []
    _install_fake_canonical_runtime(monkeypatch, calls)

    from stegverse.manifold_governance import (
        PRODUCTION_RUNTIME,
        evaluate_manifold_governance,
    )

    result = evaluate_manifold_governance(_fixture())

    assert calls == [
        {
            "transition_ids": (
                "T-SENSOR-A",
                "T-SENSOR-B",
                "T-PROTECTED-RELEASE",
                "T-AFTER-REVIEW",
            ),
            "authority_boundary_refs": (
                "authority:human-review",
                "policy:manifold-demo-v1",
            ),
        }
    ]
    assert result["production_runtime"] == PRODUCTION_RUNTIME
    assert result["production_runtime"] == "stegcore.manifold_governance.govern_manifold_action"
    assert result["parallel_evaluator"] is False
    assert result["sdk_grants_authority"] is False
    assert result["sdk_reinterprets_disposition"] is False
    assert result["external_execution_performed_by_sdk"] is False

    action = result["action"]
    assert action["state"] == "REVIEWABLE"
    assert action["continue_transition_ids"] == ("T-SENSOR-A", "T-SENSOR-B")
    assert action["review_transition_ids"] == ("T-PROTECTED-RELEASE",)
    assert action["held_transition_ids"] == ("T-AFTER-REVIEW",)
    assert action["external_execution_performed"] is False


def test_missing_canonical_runtime_fails_without_sdk_fallback(monkeypatch):
    monkeypatch.delitem(sys.modules, "stegcore", raising=False)
    monkeypatch.delitem(sys.modules, "stegcore.manifold_governance", raising=False)
    monkeypatch.delitem(sys.modules, "stegcore.steggate", raising=False)

    import builtins
    real_import = builtins.__import__

    def blocked_import(name, *args, **kwargs):
        if name.startswith("stegcore"):
            raise ImportError("canonical runtime unavailable")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", blocked_import)

    from stegverse.manifold_governance import ManifoldGovernanceSDKError, evaluate_manifold_governance

    try:
        evaluate_manifold_governance(_fixture())
    except ManifoldGovernanceSDKError as exc:
        message = str(exc)
    else:
        raise AssertionError("missing canonical StegCore must fail")

    assert "no fallback or parallel evaluator" in message
