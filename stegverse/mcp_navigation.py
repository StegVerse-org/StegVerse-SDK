"""Human-facing selected-mode navigation for MCP production-artifact tests.

This module explains and routes the MCP test surface only. It does not evaluate
admissibility or grant authority.
"""
from __future__ import annotations

MCP_NAVIGATION = (
    ("000", "Show how the MCP production-artifact test works"),
    ("00", "Configure caller-return/explanation preferences"),
    ("0", "Run a governed MCP tool-call test"),
    ("1", "Replay a prior MCP governed run by manifest_receipt_id"),
    ("2", "Reconstruct a prior MCP governed run by manifest_receipt_id"),
)

MCP_ROUTE = """MCP PRODUCTION-ARTIFACT TEST ROUTE

The MCP server is a capability/transport endpoint. It does not become the
StegVerse authority source.

Canonical route:

  SDK MCP test entry
  -> MCP initialize + tools/list discovery (observation only)
  -> exact discovered tool contract + proposed arguments canonicalized and hashed
  -> portable MCP test packet constructed (authority effect: NONE)
  -> canonical SDK ingress / Core-Lite manifested route carrier
  -> Master Records MRR-* checkpoint custody
  -> canonical StegCore manifested transaction
  -> canonical StegGate + commit-coherence evaluation
  -> only when the canonical transaction permits consequence: MCP tools/call
  -> MCP result captured as execution observation
  -> Master Records MR-* exact-run custody
  -> canonical return ingestion/CGE
  -> Master Records MRR-* return custody
  -> same SDK caller connection receives permitted return projection

Every canonical route transition is manifested/receipted. Master Records custody
is independent of what transition details the caller elects to receive.

MCP source choices for option 0:
  reference -> StegVerse General MCP, an inspectable ordinary stdio MCP server
  external  -> tester-provided safe stdio server descriptor

Credential boundary:
  caller-managed tokens, secrets, passwords, auth headers, credential fields, or
  environment credentials in an external descriptor are rejected. Protected
  credential authority remains TV/TVC_ONLY.

Important invariants:
  tools/list != authority
  tools/call != authority
  packet validity != authority
  manifest_receipt_id != authority
  replay != consequence re-execution
  reconstruction != consequence re-execution
"""

MCP_RETURN_GUIDANCE = """MCP CALLER-RETURN / EXPLANATION PREFERENCES

This selected mode follows the ordinary SDK option 00 semantics.

The caller may request ALL, SELECTED, or NONE user-return transition projection
and explanatory labels where supported by the canonical ingress profile.
Those preferences control disclosure to the caller only. They do not suppress
Master Records custody, erase route checkpoints, alter a governance decision, or
grant MCP execution authority.
"""

MCP_RUN_GUIDANCE = """RUN A GOVERNED MCP TOOL-CALL TEST

Choose an MCP source:
  reference -> use the inspectable StegVerse General MCP
  external  -> provide a JSON stdio descriptor for your MCP server

The SDK initializes the server and performs tools/list first. The exact selected
tool contract and proposed arguments are canonicalized and hashed into the
portable MCP test packet. That packet becomes evidence for an ordinary canonical
StegGate request. No special MCP evaluator is introduced.

The actual MCP tools/call is installed as the bounded consequence executor of the
existing canonical StegCore transaction lifecycle. It is therefore not sent by
the test harness before governance. If the canonical lifecycle does not admit the
consequence, the MCP call is not the authority source and cannot make itself
admissible.
"""

MCP_REPLAY_GUIDANCE = """REPLAY A PRIOR MCP GOVERNED RUN

Provide the MR-* manifest_receipt_id from option 0. The ordinary canonical replay
operation re-evaluates retained governance evidence and records the replay
operation trajectory. It does not resend the original MCP tools/call.
"""

MCP_RECONSTRUCT_GUIDANCE = """RECONSTRUCT A PRIOR MCP GOVERNED RUN

Provide the MR-* manifest_receipt_id from option 0. The ordinary canonical
reconstruction operation rebuilds the retained run trajectory from Master Records
custody. It does not resend the original MCP tools/call.
"""


def navigation_text() -> str:
    lines = ["StegVerse MCP production-artifact tests", ""]
    lines.extend(f"[{key}] {label}" for key, label in MCP_NAVIGATION)
    return "\n".join(lines)


def guidance_for(selection: str) -> str:
    key = selection.strip().upper()
    if key == "000":
        return MCP_ROUTE
    if key == "00":
        return MCP_RETURN_GUIDANCE
    if key == "0":
        return MCP_RUN_GUIDANCE
    if key == "1":
        return MCP_REPLAY_GUIDANCE
    if key == "2":
        return MCP_RECONSTRUCT_GUIDANCE
    raise ValueError("MCP selection must be 000, 00, 0, 1, or 2")
