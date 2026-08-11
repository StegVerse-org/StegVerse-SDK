from contextlib import redirect_stdout
from io import StringIO
import json

from stegverse import cli


def _capture(function, *args):
    stream = StringIO()
    with redirect_stdout(stream):
        result = function(*args)
    return result, stream.getvalue().lower()


def test_list_surfaces_is_generic_and_callable():
    names = [name for name, _ in cli.list_surfaces()]
    assert "admittedcode" in names
    assert "admissibility" in names
    assert "llm-admissibility" in names
    assert "math-admissibility" in names
    assert "universal-entry" in names
    assert "bridges" in names
    assert "entry-points" in names
    assert all("mansoor" not in name.lower() for name in names)


def test_admittedcode_help_is_generic_and_actionable():
    result, out = _capture(cli.print_help_for_surface, "admittedcode")
    assert result == 0
    assert "portable admittedcode" in out
    assert "stegverse run admittedcode" in out
    assert "stegverse demo admittedcode" in out
    assert "result semantics" in out
    assert "docs/sdk_console.md#admittedcode" in out
    assert "mansoor" not in out


def test_unknown_surface_fails_closed():
    result, out = _capture(cli.print_help_for_surface, "does-not-exist")
    assert result == 2
    assert "unknown surface" in out


def test_bridges_run_without_external_authority():
    result, out = _capture(cli.main, ["run", "bridges"])
    assert result == 0
    payload = json.loads(out)
    ids = {item["id"] for item in payload["bridges"]}
    assert {"generic_tester_packet", "llm_output", "math_artifact"}.issubset(ids)


def test_entry_points_run_without_external_authority():
    result, out = _capture(cli.main, ["run", "entry-points"])
    assert result == 0
    payload = json.loads(out)
    ids = {item["entry_point_id"] for item in payload["entry_points"]}
    assert "sdk" in ids
    assert "llm_adapter" in ids


def test_llm_admissibility_run_is_local_and_receipt_referenced():
    result, out = _capture(
        cli.main,
        [
            "run", "llm-admissibility",
            "--provider", "fixture-provider",
            "--model", "fixture-model",
            "--prompt", "Draft a research note.",
            "--output", "A bounded research note.",
        ],
    )
    assert result == 0
    payload = json.loads(out)
    assert payload["schema"] == "stegverse.llm_admissibility.bridge_result.v1"
    assert "admissibility_receipt_reference" in payload


def test_admittedcode_demo_exercises_allow_and_deny_receipts():
    result, out = _capture(cli.main, ["demo", "admittedcode"])
    assert result == 0
    payload = json.loads(out)
    assert payload["surface"] == "admittedcode"
    assert payload["authority_effect"] == "none"
    assert payload["results"]["allow"]["verification"]["status"] == "accepted"
    assert payload["results"]["allow"]["verification"]["decision"] == "allow"
    assert payload["results"]["deny"]["verification"]["status"] == "accepted"
    assert payload["results"]["deny"]["verification"]["decision"] == "deny"


def test_admittedcode_demo_can_select_one_case():
    result, out = _capture(cli.main, ["demo", "admittedcode", "--case", "deny"])
    assert result == 0
    payload = json.loads(out)
    assert set(payload["results"]) == {"deny"}


def test_missing_run_input_fails_closed_with_demo_hint():
    result, out = _capture(cli.main, ["run", "admittedcode"])
    assert result == 2
    assert "requires --input" in out
    assert "stegverse demo admittedcode" in out
