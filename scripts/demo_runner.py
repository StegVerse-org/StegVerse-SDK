#!/usr/bin/env python3
"""
SDK Wrapper Reference — AaCT-E Demo Runner

Implements the read-only contract from docs/SDK_INTEGRATION.md.
This is a reference implementation for SDK developers.

Usage:
    from demo_runner import DemoRunner
    runner = DemoRunner(repo="AaCT-E/demo", tag="v0.2.0")
    result = runner.verify()
    print(result)
"""

import subprocess
import json
import tempfile
import shutil
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class DemoResult:
    """Immutable result from AaCT-E demo verification."""
    passed: bool
    repo: str
    tag: str
    commit_sha: str
    scenarios: dict
    stdout: str
    stderr: str
    provenance: dict


class DemoRunner:
    """
    Read-only wrapper for AaCT-E/demo.

    Contract:
    - Specifies tag, never 'main'
    - Preserves all provenance fields
    - Surfaces verification failures raw
    - Runs demo in isolated subprocess
    - Does not modify demo source
    """

    def __init__(self, repo: str = "AaCT-E/demo", tag: str = "v0.2.0"):
        if not tag or tag == "main":
            raise ValueError("SDK contract requires explicit tag, not 'main'")
        self.repo = repo
        self.tag = tag
        self._temp_dir: Optional[Path] = None

    def _clone(self) -> Path:
        """Clone demo to temp directory. Returns path to cloned repo."""
        self._temp_dir = Path(tempfile.mkdtemp(prefix="aacte_demo_"))
        cmd = [
            "git", "clone",
            "--branch", self.tag,
            "--depth", "1",
            f"https://github.com/{self.repo}.git",
            str(self._temp_dir)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Clone failed: {result.stderr}")
        return self._temp_dir

    def _get_commit_sha(self, repo_dir: Path) -> str:
        """Get commit SHA from cloned repo."""
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(repo_dir),
            capture_output=True, text=True
        )
        return result.stdout.strip()

    def verify(self) -> DemoResult:
        """
        Run verification in isolated subprocess.

        Returns DemoResult with full provenance.
        Raises RuntimeError on clone failure.
        Returns DemoResult with passed=False on verification failure (does NOT raise).
        """
        repo_dir = self._clone()
        commit_sha = self._get_commit_sha(repo_dir)

        # Run verification
        verify_cmd = ["python", "verify_demo.py"]
        verify_result = subprocess.run(
            verify_cmd,
            cwd=str(repo_dir),
            capture_output=True,
            text=True
        )

        # Also run demo to get structured output
        demo_cmd = ["python", "-m", "access.cli", "--json"]
        demo_result = subprocess.run(
            demo_cmd,
            cwd=str(repo_dir),
            capture_output=True,
            text=True
        )

        scenarios = {}
        if demo_result.returncode == 0:
            try:
                data = json.loads(demo_result.stdout)
                scenarios = data.get("scenarios", {})
            except json.JSONDecodeError:
                pass

        provenance = {
            "repo": self.repo,
            "tag": self.tag,
            "commit_sha": commit_sha,
            "clone_path": str(repo_dir),
        }

        return DemoResult(
            passed=verify_result.returncode == 0,
            repo=self.repo,
            tag=self.tag,
            commit_sha=commit_sha,
            scenarios=scenarios,
            stdout=verify_result.stdout,
            stderr=verify_result.stderr,
            provenance=provenance,
        )

    def cleanup(self) -> None:
        """Remove temp clone directory."""
        if self._temp_dir and self._temp_dir.exists():
            shutil.rmtree(self._temp_dir)
            self._temp_dir = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
        return False


# Example usage
if __name__ == "__main__":
    with DemoRunner(tag="v0.2.0") as runner:
        result = runner.verify()
        print(f"Verification: {'PASSED' if result.passed else 'FAILED'}")
        print(f"Commit: {result.commit_sha}")
        print(f"Scenarios: {list(result.scenarios.keys())}")
        for name, data in result.scenarios.items():
            print(f"  {name}: {data['decision']} (min_sep={data['proposal_min_separation_nm']:.3f}nm)")
