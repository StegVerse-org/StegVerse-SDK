from contextlib import redirect_stdout
from io import StringIO

from stegverse import cli


def _registry():
    return {
        "schema_version": "test",
        "repo": "StegVerse-org/StegVerse-SDK",
        "governed_llm_surfaces": {"receipt_handoff_binding": "built"},
        "sdk_to_spe_commitment_intake": {"allow_receipt_consumer": "built_progression_only"},
        "universal_entry_runtime": {"deterministic_router": "built"},
    }


def _capture(function, *args):
    stream = StringIO()
    with redirect_stdout(stream):
        result = function(*args)
    return result, stream.getvalue().lower()


def test_list_surfaces_is_generic():
    names = [name for name, _ in cli.list_surfaces(_registry())]
    assert "governed-llm-surfaces" in names
    assert "sdk-to-spe-commitment-intake" in names
    assert "universal-entry-runtime" in names
    assert all("mansoor" not in name.lower() for name in names)


def test_admittedcode_help_is_generic():
    result, out = _capture(cli.print_help_for_surface, "admittedcode", _registry())
    assert result == 0
    assert "admittedcode" in out
    assert "admissibility" in out
    assert "mansoor" not in out


def test_unknown_surface_fails_closed():
    result, out = _capture(cli.print_help_for_surface, "does-not-exist", _registry())
    assert result == 2
    assert "unknown surface" in out
