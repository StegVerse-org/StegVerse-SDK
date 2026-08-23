import io
import json
from contextlib import redirect_stderr
from pathlib import Path

from stegverse.portable_governance_verifier_cli import main


def test_cli_fails_closed_on_invalid_bundle(tmp_path: Path):
    path = tmp_path / "invalid.json"
    path.write_text(json.dumps({"schema": "wrong"}), encoding="utf-8")
    stderr = io.StringIO()

    with redirect_stderr(stderr):
        rc = main([str(path)])

    assert rc == 2
    report = json.loads(stderr.getvalue())
    assert report["status"] == "FAIL_CLOSED"
    assert report["authority"] == {
        "verification_authority": "NONE",
        "execution_authorized": False,
        "standing_minted": False,
        "admissibility_decided": False,
        "custody_claimed": False,
    }


def test_cli_fails_closed_on_non_object_json(tmp_path: Path):
    path = tmp_path / "list.json"
    path.write_text("[]", encoding="utf-8")
    stderr = io.StringIO()

    with redirect_stderr(stderr):
        rc = main([str(path)])

    assert rc == 2
    report = json.loads(stderr.getvalue())
    assert report["status"] == "FAIL_CLOSED"
    assert "root must be an object" in report["error"]
