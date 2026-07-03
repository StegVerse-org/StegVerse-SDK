import subprocess
import sys
from pathlib import Path


def test_verify_governed_llm_demo_packet(tmp_path):
    """Verify that the demo packet passes verification."""
    repo_root = Path(__file__).resolve().parents[1]
    # Copy the session packet into a temporary location
    src_packet = repo_root / "examples" / "governed_llm_demo" / "session_packet.simple_query.json"
    dst_packet = tmp_path / "session_packet.simple_query.json"
    dst_packet.write_bytes(src_packet.read_bytes())

    script = repo_root / "scripts" / "verify_governed_llm_demo_packet.py"
    result = subprocess.run(
        [sys.executable, str(script), "--session", str(dst_packet)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Verification failed: {result.stdout}{result.stderr}"