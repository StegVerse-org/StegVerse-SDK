from __future__ import annotations
import json, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "examples/governed_llm_demo/session_packet.simple_query.json"

def test_demo_packet_shape_is_non_executing() -> None:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    assert packet["authority_decision"] == "ALLOW"
    assert packet["action"] == "NONE"
    assert packet["action_route"] is None
    assert packet["commitment_request"] is None
    assert packet["execution_handoff"] is None
    assert packet["evidence"]["stale"] is False

def test_demo_packet_verifier_passes() -> None:
    result = subprocess.run([sys.executable, "scripts/verify_governed_llm_demo_packet.py", "--session", str(PACKET)], cwd=ROOT, text=True, capture_output=True, check=True)
    assert "GOVERNED LLM DEMO PACKET: PASS" in result.stdout
