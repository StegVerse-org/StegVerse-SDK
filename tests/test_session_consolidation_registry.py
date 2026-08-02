import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "task-registry" / "orli-judgment-system-boundary-2026-08-02.json"
VALIDATOR = ROOT / "scripts" / "validate_session_consolidation_registry.py"


def load_validator_module():
    spec = importlib.util.spec_from_file_location("session_consolidation_validator", VALIDATOR)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_registry():
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def test_registry_is_archive_safe_and_has_no_unassigned_or_session_owned_claims():
    module = load_validator_module()
    registry = load_registry()

    assert module.validate_registry(registry) == []
    assert registry["archive_test"]["archive_ready"] is True
    assert all(task["claim_state"] != "UNCLAIMED" for task in registry["tasks"])
    assert all(task["archival_dependency"] is False for task in registry["tasks"])
    assert all(value == "RELEASED" for value in registry["session_claims"].values())


def test_every_unresolved_task_has_named_owner_location_evidence_and_release_condition():
    registry = load_registry()
    unresolved = {
        "MACHINE_OWNED",
        "BLOCKED",
        "CLAIMED_FOR_IMPLEMENTATION",
        "CLAIMED_FOR_VALIDATION",
        "CLAIMED_FOR_INTEGRATION",
    }

    for task in registry["tasks"]:
        if task["claim_state"] not in unresolved:
            continue
        assert task["owner"].strip()
        assert task["repository"].strip()
        assert task["location"].strip()
        assert task["evidence_location"].strip()
        assert task["next_action"].strip()
        assert task["release_condition"].strip()


def test_machine_owned_tasks_are_not_reassigned_to_chat_or_user():
    registry = load_registry()
    for task in registry["tasks"]:
        if task["claim_state"] == "MACHINE_OWNED":
            owner = task["owner"].lower()
            assert "chat" not in owner
            assert "user" not in owner


def test_archive_ready_state_fails_when_a_session_claim_is_reintroduced():
    module = load_validator_module()
    registry = load_registry()
    registry["session_claims"]["validation"] = "ACTIVE"

    errors = module.validate_registry(registry)
    assert "session claim validation must be RELEASED for archive-ready state" in errors


def test_archive_ready_state_fails_when_release_condition_is_removed():
    module = load_validator_module()
    registry = load_registry()
    registry["tasks"][0]["release_condition"] = ""

    errors = module.validate_registry(registry)
    assert "tasks[0].release_condition must be a non-empty string" in errors
