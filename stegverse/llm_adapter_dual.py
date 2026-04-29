#!/usr/bin/env python3
"""
StegVerse LLM Adapter v2.0 — Dual Purpose
1. Governance Ingress: LLM output → canonical intent → pipeline
2. Ecosystem Optimization: Ecosystem state → LLM → optimization → pipeline
"""

import json
import hashlib
import re
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timezone

from .safety_stack import StegVerseSafetyStack, GCATState, SafetyDecision


class LLMProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"
    AZURE = "azure"
    GOOGLE = "google"


@dataclass
class CanonicalIntent:
    """Universal intent format for StegVerse pipeline."""

    schema_version: str = "2.1"
    ingress_source: str = ""  # llm|human|webhook|api|ecosystem
    provider: str = ""
    model: str = ""
    actor_id: str = ""
    session_id: str = ""
    intent_type: str = ""  # code_generation|resource_scaling|optimization|...
    payload: Dict[str, Any] = None
    gcat_state: Dict[str, float] = None
    metadata: Dict[str, Any] = None
    timestamp: str = ""

    def __post_init__(self):
        if self.payload is None:
            self.payload = {}
        if self.gcat_state is None:
            self.gcat_state = {"g": 0.25, "c": 0.25, "a": 0.25, "t": 0.25}
        if self.metadata is None:
            self.metadata = {}
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "ingress": {
                "source": self.ingress_source,
                "provider": self.provider,
                "model": self.model,
                "actor_id": self.actor_id,
                "session_id": self.session_id,
                "timestamp": self.timestamp,
            },
            "payload": self.payload,
            "gcat_state": self.gcat_state,
            "metadata": self.metadata,
        }

    def hash(self) -> str:
        canonical = json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode()).hexdigest()


class StegVerseLLMAdapterDual:
    """
    Dual-purpose LLM adapter for StegVerse ecosystem.
    """

    # Dangerous patterns: list of (regex, description) tuples
    # Defined as a class method to avoid raw-string quote issues
    @classmethod
    def _get_dangerous_patterns(cls) -> List[Tuple[str, str]]:
        return [
            (r"os\.system\s*\(", "os.system call"),
            (r"subprocess\.call\s*\(", "subprocess.call"),
            (r"subprocess\.run\s*\(", "subprocess.run"),
            (r"subprocess\.Popen\s*\(", "subprocess.Popen"),
            (r"eval\s*\(", "eval()"),
            (r"exec\s*\(", "exec()"),
            (r"compile\s*\(", "compile()"),
            (r"__import__\s*\(", "__import__()"),
            (r"importlib\.import_module", "importlib.import_module"),
            (r"pickle\.loads?\s*\(", "pickle deserialization"),
            (r"yaml\.load\s*\(", "yaml.load unsafe"),
            (r"input\s*\(", "input()"),
            (r"raw_input\s*\(", "raw_input()"),
            (r"shutil\.rmtree", "shutil.rmtree"),
            (r"os\.remove\s*\(", "os.remove"),
            (r"os\.unlink\s*\(", "os.unlink"),
            (r"socket\.socket", "socket creation"),
            (r"urllib\.request", "urllib request"),
            (r"requests\.get\s*\(", "requests.get"),
            (r"requests\.post\s*\(", "requests.post"),
        ]

    def __init__(
        self,
        safety_stack: Optional[StegVerseSafetyStack] = None,
        pipeline_url: str = "https://api.stegverse.org/v1",
    ):
        self.safety = safety_stack or StegVerseSafetyStack()
        self.pipeline_url = pipeline_url
        self._session_counter = 0

    def govern_llm_output(
        self,
        provider: LLMProvider,
        model: str,
        prompt: str,
        output: str,
        user_context: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        self._session_counter += 1
        session_id = (
            "ingress-"
            + datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
            + f"-{self._session_counter}"
        )

        parsed = self._parse_llm_output(output)

        if parsed.get("has_dangerous_patterns"):
            patterns = parsed.get("dangerous_patterns_found", [])
            return {
                "decision": "DENY",
                "safety_layer": "SECURITY_SCAN",
                "reason": f"Dangerous patterns detected: {patterns}",
                "receipt": self.safety._generate_receipt(
                    "SECURITY", "DENY", "llm-adapter"
                ),
                "suggestions": [
                    "Remove dangerous system calls",
                    "Use safe alternatives for file/network operations",
                    "Add input validation",
                ],
            }

        gcat_state = self._compute_gcat_state(parsed)

        intent = CanonicalIntent(
            ingress_source="llm",
            provider=provider.value,
            model=model,
            actor_id=f"llm-{provider.value}-{model}-{hashlib.sha256(session_id.encode()).hexdigest()[:8]}",
            session_id=session_id,
            intent_type="code_generation",
            payload=parsed,
            gcat_state=gcat_state,
            metadata={"prompt": prompt, "user_context": user_context or {}},
        )

        gcat_obj = GCATState(**gcat_state)
        bcat_score = self._compute_bcat_score(parsed)

        safety_decision = self.safety.evaluate_mathematical(
            gcat_obj, bcat_score, intent.actor_id
        )

        if safety_decision.action == "HALT":
            return {
                "decision": "DENY",
                "safety_layer": safety_decision.layer_triggered.name,
                "reason": safety_decision.reason,
                "receipt": safety_decision.receipt_hash,
                "suggestions": self._generate_suggestions(gcat_obj, bcat_score, parsed),
            }

        if safety_decision.action == "DEFER":
            return {
                "decision": "DEFER",
                "safety_layer": safety_decision.layer_triggered.name,
                "reason": safety_decision.reason,
                "receipt": safety_decision.receipt_hash,
                "intent": intent.to_dict(),
            }

        return {
            "decision": "ADMIT",
            "safety_layer": safety_decision.layer_triggered.name,
            "receipt": safety_decision.receipt_hash,
            "intent_hash": intent.hash(),
            "gcat_score": gcat_obj.legitimacy_surplus(),
            "bcat_score": bcat_score,
        }

    def optimize_ecosystem(
        self,
        ecosystem_metrics: Dict[str, Any],
        llm_analysis: str,
        proposed_changes: Dict[str, Any],
    ) -> Dict[str, Any]:
        self._session_counter += 1
        session_id = (
            "optimization-"
            + datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
            + f"-{self._session_counter}"
        )

        gcat_state = self._compute_ecosystem_gcat_state(ecosystem_metrics)

        intent = CanonicalIntent(
            ingress_source="ecosystem",
            provider="stegverse-internal",
            model="optimizer",
            actor_id="llm-stegverse-optimizer-001",
            session_id=session_id,
            intent_type="ecosystem_modification",
            payload={
                "metrics": ecosystem_metrics,
                "analysis": llm_analysis,
                "proposed_changes": proposed_changes,
            },
            gcat_state=gcat_state,
            metadata={"optimization_type": proposed_changes.get("type", "unknown")},
        )

        gcat_obj = GCATState(**gcat_state)
        bcat_score = self._compute_ecosystem_bcat_score(proposed_changes)

        safety_decision = self.safety.evaluate_mathematical(
            gcat_obj, bcat_score, intent.actor_id
        )

        if safety_decision.action == "HALT":
            return {
                "decision": "DENY",
                "safety_layer": safety_decision.layer_triggered.name,
                "reason": safety_decision.reason,
                "receipt": safety_decision.receipt_hash,
                "suggestions": [
                    "Reduce cost impact of proposed changes",
                    "Increase observability before scaling",
                    "Defer to human review for high-cost changes",
                ],
            }

        if safety_decision.action == "DEFER":
            return {
                "decision": "DEFER",
                "safety_layer": safety_decision.layer_triggered.name,
                "reason": safety_decision.reason,
                "receipt": safety_decision.receipt_hash,
                "intent": intent.to_dict(),
            }

        return {
            "decision": "ADMIT",
            "safety_layer": safety_decision.layer_triggered.name,
            "receipt": safety_decision.receipt_hash,
            "intent_hash": intent.hash(),
            "gcat_score": gcat_obj.legitimacy_surplus(),
            "bcat_score": bcat_score,
            "execution_plan": proposed_changes,
        }

    def _parse_llm_output(self, output: str) -> Dict[str, Any]:
        code_blocks = re.findall(r"```(?:\w+)?\n(.*?)\n```", output, re.DOTALL)
        files = re.findall(r'["\']([\w/]+\.(py|js|ts|java|go|rs))["\']', output)

        dangerous_found = []
        for pattern, desc in self._get_dangerous_patterns():
            if re.search(pattern, output, re.IGNORECASE):
                dangerous_found.append(desc)

        return {
            "code_blocks": code_blocks,
            "files_modified": [f[0] for f in files],
            "lines_added": sum(len(block.split("\n")) for block in code_blocks),
            "has_tests": "test" in output.lower() or "assert" in output.lower(),
            "has_docs": '"""' in output or "docstring" in output.lower(),
            "complexity": self._estimate_complexity(code_blocks),
            "has_dangerous_patterns": len(dangerous_found) > 0,
            "dangerous_patterns_found": dangerous_found,
        }

    def _compute_gcat_state(self, parsed: Dict) -> Dict[str, float]:
        g = (
            0.3
            + (0.15 if parsed.get("has_docs") else 0)
            + (0.1 if parsed.get("has_tests") else 0)
        )
        c = 0.2 + (0.25 if parsed.get("has_tests") else 0)
        a = 0.15 + (0.25 * min(1.0, parsed.get("lines_added", 0) / 100))
        t = 0.25

        total = g + c + a + t
        return {
            "g": g / total,
            "c": c / total,
            "a": a / total,
            "t": t / total,
        }

    def _compute_bcat_score(self, parsed: Dict) -> float:
        observability = 0.3 + (0.4 if parsed.get("has_tests") else 0)
        risk = 1.0 - min(1.0, parsed.get("complexity", 0.5))
        boundary = 1.0 - min(1.0, parsed.get("lines_added", 0) / 500)
        return observability * 0.4 + risk * 0.3 + boundary * 0.3

    def _compute_ecosystem_gcat_state(self, metrics: Dict) -> Dict[str, float]:
        cpu = metrics.get("cpu", 0.5)
        memory = metrics.get("memory", 0.5)
        cost = metrics.get("cost_ratio", 0.5)
        trust = metrics.get("system_trust", 0.5)

        g = 1.0 - max(cpu, memory)
        c = 1.0 - metrics.get("error_rate", 0)
        a = (cost + cpu) / 2
        t = trust

        total = g + c + a + t
        return {
            "g": g / total,
            "c": c / total,
            "a": a / total,
            "t": t / total,
        }

    def _compute_ecosystem_bcat_score(self, changes: Dict) -> float:
        cost = changes.get("cost_increase", 0)
        risk = changes.get("risk_score", 0.5)
        observability = changes.get("observability", 0.5)

        return (
            observability * 0.4
            + (1.0 - risk) * 0.3
            + (1.0 - min(1.0, cost / 10000)) * 0.3
        )

    def _estimate_complexity(self, code_blocks: List[str]) -> float:
        if not code_blocks:
            return 0.0
        total_lines = sum(len(block.split("\n")) for block in code_blocks)
        return min(1.0, total_lines / 200)

    def _generate_suggestions(
        self, gcat: GCATState, bcat: float, parsed: Dict
    ) -> List[str]:
        suggestions = []
        if gcat.legitimacy_surplus() < 0:
            suggestions.append("Reduce artifact pressure: smaller changes")
        if bcat < 0.6:
            suggestions.append("Improve observability: add tests, docs")
        if not parsed.get("has_tests"):
            suggestions.append("Add tests for verification")
        if not parsed.get("has_docs"):
            suggestions.append("Add documentation")
        if parsed.get("has_dangerous_patterns"):
            suggestions.append(
                "Remove dangerous system calls and use safe alternatives"
            )
        return suggestions


if __name__ == "__main__":
    print("StegVerse LLM Adapter v2.0")
    adapter = StegVerseLLMAdapterDual()

    safe_code = '''
def hello():
    """Say hello."""
    return "hello"

def test_hello():
    assert hello() == "hello"
    '''

    result = adapter.govern_llm_output(
        provider=LLMProvider.OPENAI,
        model="gpt-4",
        prompt="Write a hello function",
        output=safe_code,
    )
    print(f"Safe: {result['decision']} (Layer: {result['safety_layer']})")

    risky_code = "import os\ndef run(cmd):\n    os.system(cmd)"
    result = adapter.govern_llm_output(
        provider=LLMProvider.OPENAI,
        model="gpt-4",
        prompt="Run a command",
        output=risky_code,
    )
    print(f"Risky: {result['decision']} (Layer: {result['safety_layer']})")
