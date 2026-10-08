"""Manifest Builder -> InTr round trip: StegVerse-org -> SV-LLM -> StegVerse-org -> SDK.

Proposed test. It drives the real boundary code of both organizations, leg by
leg, and stops at the first leg that does not ALLOW. Every leg's disposition is
written to a JSON run report, so a failure is a named predicate rather than a
claim. Both organization checkouts are copied to scratch first, so no ledger in
either checkout is written by a test run.

The test passes only when every leg allows. A loopback does not count: leg 2
must be consumed by SV-LLM's own crossing code, and leg 4 by StegVerse-org's.
Each organization's legs run in their own Python process with their own
ledgers: both runtimes import sibling modules by bare name (``ledger_store``),
so sharing one interpreter would let one organization's leg execute the other
organization's modules.
The Publisher PDF is not produced here; only GCAT-BCAT-Engine/Publisher renders
it. The run report is the JSON half of the Publisher return.

Run:
  STEGVERSE_ORG_DOTGITHUB_ROOT=<StegVerse-org/.github checkout> \
  SV_LLM_DOTGITHUB_ROOT=<SV-LLM/.github checkout> \
  [SV_LLM_ROUNDTRIP_REPORT=<path>] \
  python -m unittest tests.test_sv_llm_intr_roundtrip -v
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from stegverse.manifest_builder import build_manifest

ORG = "StegVerse-org"
PEER = "SV-LLM"
GENESIS = {"mode": "ESTABLISH_GENESIS", "node_ref": "sv-llm-roundtrip", "predecessor": None}
LEDGER_ENV = ("STEGVERSE_REPO_LEDGER_ROOT", "STEGVERSE_ORG_LEDGER_ROOT")


# Runs one organization operation in a fresh interpreter rooted at that
# organization's checkout. Paths in kwargs named *root are passed as Path.
_DRIVER = r"""
import importlib.util, json, sys
from pathlib import Path
req = json.load(sys.stdin)
spec = importlib.util.spec_from_file_location(req["name"], req["module"])
mod = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(mod)
    kwargs = {k: (Path(v) if k.endswith("root") and v is not None else v) for k, v in req["kwargs"].items()}
    out = getattr(mod, req["function"])(*req.get("args", []), **kwargs)
    print(json.dumps({"ok": True, "value": out}, default=str))
except SystemExit as exc:
    print(json.dumps({"ok": False, "type": "SystemExit", "reason": str(exc)}))
except Exception as exc:
    print(json.dumps({"ok": False, "type": type(exc).__name__, "reason": str(exc)[:500]}))
"""


def _run_in_org(org_root: Path, ledger_root: Path, module: str, function: str, *, args=(), **kwargs):
    env = {k: v for k, v in os.environ.items() if k not in LEDGER_ENV}
    env["STEGVERSE_REPO_LEDGER_ROOT"] = str(ledger_root / "repo")
    env["STEGVERSE_ORG_LEDGER_ROOT"] = str(ledger_root / "org")
    request = {"name": module.replace("/", "_").replace(".py", ""), "module": str(org_root / module),
               "function": function, "args": list(args), "kwargs": kwargs}
    completed = subprocess.run([sys.executable, "-B", "-c", _DRIVER], input=json.dumps(request, default=str),
                               capture_output=True, text=True, cwd=org_root, env=env, timeout=600)
    lines = [ln for ln in completed.stdout.splitlines() if ln.startswith("{")]
    if not lines:
        raise RuntimeError("org process produced no result: rc=%s %s" % (completed.returncode, completed.stderr[-500:]))
    result = json.loads(lines[-1])
    if not result["ok"]:
        raise RuntimeError("%s: %s" % (result["type"], result["reason"]))
    return result["value"]


SDK_INGRESS = "stegverse-org.sdk-manifest-ingress"
SDK_INGRESS_TRANSITION = "ORGANIZATION_SDK_MANIFEST_INGRESS"


def _receipt_classes(ledger_root: Path) -> dict:
    counts: dict = {}
    for path in ledger_root.rglob("*.json"):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            continue
        name = record.get("transition_class") if isinstance(record, dict) else None
        if name:
            counts[name] = counts.get(name, 0) + 1
    return counts


def _frames_by_destination(mesh: Path) -> dict:
    counts: dict = {}
    for path in mesh.rglob("*.json"):
        try:
            frame = json.loads(path.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            continue
        org = frame.get("destination_org") if isinstance(frame, dict) else None
        if org:
            counts[org] = counts.get(org, 0) + 1
    return counts


def _governance_request() -> dict:
    # The Manifest Builder's own fixture, so this test exercises the builder exactly as its gate does.
    from tests.test_manifest_builder import governance_request
    return governance_request()


@unittest.skipUnless(os.environ.get("STEGVERSE_ORG_DOTGITHUB_ROOT") and os.environ.get("SV_LLM_DOTGITHUB_ROOT"),
                     "requires StegVerse-org/.github and SV-LLM/.github checkouts")
class SVLLMIntrRoundTrip(unittest.TestCase):
    def setUp(self):
        self.scratch = Path(tempfile.mkdtemp(prefix="sv-llm-roundtrip-"))
        self.addCleanup(shutil.rmtree, self.scratch, True)
        self.org_root = self.scratch / "org"
        self.peer_root = self.scratch / "sv-llm"
        shutil.copytree(os.environ["STEGVERSE_ORG_DOTGITHUB_ROOT"], self.org_root, ignore=shutil.ignore_patterns(".git"))
        shutil.copytree(os.environ["SV_LLM_DOTGITHUB_ROOT"], self.peer_root, ignore=shutil.ignore_patterns(".git"))
        self.mesh = self.scratch / "mesh"
        self.mesh.mkdir()
        self.org_ledger = self.scratch / "ledger" / "stegverse-org"
        self.peer_ledger = self.scratch / "ledger" / "sv-llm"
        self.legs: list[dict] = []

    def _leg(self, leg: int, name: str, fn):
        try:
            result = fn()
            disposition = result.get("disposition", "ALLOW") if isinstance(result, dict) else "ALLOW"
            entry = {"leg": leg, "name": name, "disposition": disposition, "result": result}
        except Exception as exc:  # a crash or refusal exit is a fail-closed leg, recorded with its predicate
            entry = {"leg": leg, "name": name, "disposition": "FAIL_CLOSED",
                     "failed_predicate": type(exc).__name__, "reason": str(exc)[:500]}
        self.legs.append(entry)
        return entry

    def _report(self, manifest) -> dict:
        reached = {e["leg"] for e in self.legs}
        names = ["SDK_MANIFEST_BUILD", "STEGVERSE_ORG_EGRESS_TO_SV_LLM", "SV_LLM_ORG_LEDGER_GENESIS", "SV_LLM_INGRESS",
                 "SV_LLM_EGRESS_TO_STEGVERSE_ORG", "STEGVERSE_ORG_INGRESS_TO_SDK"]
        report = {
            "schema": "stegverse.sdk.sv-llm-intr-roundtrip-run/v0.1",
            "task": "SV-LLM-INTR-ROUNDTRIP-TEST-PROPOSAL-001",
            "route": [ORG, PEER, ORG, "StegVerse-SDK"],
            "manifest_sha256": (manifest or {}).get("payload_sha256") if isinstance(manifest, dict) else None,
            "legs": self.legs + [{"leg": i, "name": n, "disposition": "NOT_REACHED"}
                                 for i, n in enumerate(names) if i not in reached],
            "all_legs_allow": all(e["disposition"] == "ALLOW" for e in self.legs) and len(reached) == len(names),
            "publisher_pdf": "NOT_PRODUCED_HERE_REQUIRES_GCAT-BCAT-Engine/Publisher",
            "evidence_class": "SAME_HOST_SCRATCH_CODE_PATH_CONFORMANCE_ONLY",
            "process_isolation": "ONE_INTERPRETER_PER_ORGANIZATION_LEG",
            "authority_effect": "NONE_TEST_ONLY",
        }
        out = os.environ.get("SV_LLM_ROUNDTRIP_REPORT")
        if out:
            Path(out).write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
        return report

    def test_manifest_crosses_to_sv_llm_and_returns(self):
        manifest = None

        def leg0():
            nonlocal manifest
            manifest = build_manifest(data={"probe": "sv-llm-roundtrip"}, source_framework="StegVerse-SDK",
                                      source_output_id="sv-llm-roundtrip-001",
                                      processor_request=_governance_request(),
                                      created_at="2026-10-08T00:00:00Z")
            return {"disposition": "ALLOW", "manifest_keys": sorted(manifest)}

        def leg1():
            return _run_in_org(self.org_root, self.org_ledger, "resident-runtime/organization_egress_boundary.py", "emit",
                               args=[PEER, {"message_class": "ecosystem.work.request",
                                            "communication_id": "sv-llm-roundtrip-001",
                                            "subject": "manifest builder round trip",
                                            "body": {"manifest": manifest}}],
                               standing=GENESIS, root=str(self.org_root), mesh_root=str(self.mesh), hb_epoch=32)

        def leg2_genesis():
            # SV-LLM's own declared ledger-opening transition, as its live lane runs it
            # (org-runtime/authentic_live_lane.py). Scratch ledger only.
            return _run_in_org(self.peer_root, self.peer_ledger, "org-runtime/crossing.py", "open_organization_ledger",
                               root=str(self.peer_root))

        def leg2():
            consumed = _run_in_org(self.peer_root, self.peer_ledger, "org-runtime/crossing.py", "ingress",
                                   mesh_root=str(self.mesh), root=str(self.peer_root))
            if not consumed:
                return {"disposition": "DENY", "failed_predicate": "NO_FRAME_CONSUMED_BY_SV_LLM"}
            return {"disposition": "ALLOW", "consumed": consumed}

        def leg3():
            # The reply declares the capability it is for, so SV-LLM addresses
            # StegVerse-org's SDK manifest ingress rather than its control service.
            reply = {"manifest_id": "sv-llm-roundtrip-reply-001",
                     "destination": {"organization": ORG, "capability": "sdk-manifest-ingress"},
                     "in_reply_to": "sv-llm-roundtrip-001", "payload": {"manifest": manifest}}
            emitted = _run_in_org(self.peer_root, self.peer_ledger, "org-runtime/crossing.py", "egress", args=[reply],
                               standing=GENESIS, mesh_root=str(self.mesh), root=str(self.peer_root))
            if emitted.get("disposition") == "ALLOW" and emitted.get("destination_service") != SDK_INGRESS:
                return {"disposition": "DENY", "failed_predicate": "REPLY_NOT_ADDRESSED_TO_SDK_MANIFEST_INGRESS",
                        "result": emitted}
            return emitted

        def leg4():
            node_state = self.scratch / "org-node-state"
            node_state.mkdir(exist_ok=True)
            result = _run_in_org(self.org_root, self.org_ledger, "resident-runtime/federation_cycle.py", "main",
                                 mesh_root=str(self.mesh), node_state_root=str(node_state))
            if not isinstance(result, dict) or not result.get("frames_consumed"):
                return {"disposition": "DENY", "failed_predicate": "NO_REPLY_FRAME_CONSUMED_BY_STEGVERSE_ORG",
                        "result": result}
            ingress = _receipt_classes(self.org_ledger).get(SDK_INGRESS_TRANSITION, 0)
            if not ingress:
                return {"disposition": "DENY", "failed_predicate": "SDK_MANIFEST_INGRESS_NOT_RECORDED_BY_STEGVERSE_ORG",
                        "result": result}
            return {"disposition": "ALLOW", "result": result, "sdk_manifest_ingress_receipts": ingress,
                    "onward_frames": _frames_by_destination(self.mesh)}

        for i, (name, fn) in enumerate([("SDK_MANIFEST_BUILD", leg0), ("STEGVERSE_ORG_EGRESS_TO_SV_LLM", leg1),
                                        ("SV_LLM_ORG_LEDGER_GENESIS", leg2_genesis), ("SV_LLM_INGRESS", leg2), ("SV_LLM_EGRESS_TO_STEGVERSE_ORG", leg3),
                                        ("STEGVERSE_ORG_INGRESS_TO_SDK", leg4)]):
            if self._leg(i, name, fn)["disposition"] != "ALLOW":
                break

        report = self._report(manifest)
        first_failure = next((e for e in self.legs if e["disposition"] != "ALLOW"), None)
        self.assertTrue(report["all_legs_allow"],
                        "round trip stopped at leg %s %s: %s" % (
                            first_failure and first_failure["leg"], first_failure and first_failure["name"],
                            json.dumps({k: v for k, v in (first_failure or {}).items() if k != "result"},
                                       default=str)[:400]))


class SVLLMIntrRoundTripBoundaryCases(SVLLMIntrRoundTrip):
    """Non-ALLOW and receiver-unavailable cases at the same real boundaries."""

    def test_manifest_crosses_to_sv_llm_and_returns(self):  # covered by the parent class
        self.skipTest("positive path runs once, in SVLLMIntrRoundTrip")

    def _frames(self):
        return sorted(p for p in self.mesh.rglob("*") if p.is_file())

    def _genesis(self):
        return _run_in_org(self.peer_root, self.peer_ledger, "org-runtime/crossing.py", "open_organization_ledger",
                           root=str(self.peer_root))

    def _peer_egress(self, manifest):
        return _run_in_org(self.peer_root, self.peer_ledger, "org-runtime/crossing.py", "egress", args=[manifest],
                           standing=GENESIS, mesh_root=str(self.mesh), root=str(self.peer_root))

    def test_undeclared_destination_is_refused_and_nothing_is_published(self):
        result = _run_in_org(self.org_root, self.org_ledger, "resident-runtime/organization_egress_boundary.py", "emit",
                             args=["NO-SUCH-ORGANIZATION", {"message_class": "ecosystem.work.request",
                                                            "communication_id": "sv-llm-roundtrip-undeclared",
                                                            "subject": "undeclared destination", "body": {}}],
                             standing=GENESIS, root=str(self.org_root), mesh_root=str(self.mesh), hb_epoch=32)
        self.assertEqual(result["disposition"], "DENY")
        self.assertEqual(result["failed_predicate"], "DESTINATION_IS_A_DECLARED_PEER_OF_THIS_ORGANIZATION")
        self.assertEqual(self._frames(), [])

    def test_reply_manifest_without_destination_is_refused(self):
        self._genesis()
        result = self._peer_egress({"manifest_id": "sv-llm-roundtrip-tampered", "payload": {}})
        self.assertEqual(result["disposition"], "DENY")
        self.assertEqual(result["failed_predicate"], "MANIFEST_DESTINATION_MISSING")
        self.assertEqual(self._frames(), [])

    def test_reply_to_an_organization_outside_the_directory_is_refused(self):
        self._genesis()
        result = self._peer_egress({"manifest_id": "sv-llm-roundtrip-undeclared-reply",
                                    "destination": {"organization": "NO-SUCH-ORGANIZATION"}, "payload": {}})
        self.assertEqual(result["disposition"], "DENY")
        self.assertEqual(result["failed_predicate"], "DESTINATION_NOT_IN_FEDERATION_DIRECTORY")
        self.assertEqual(self._frames(), [])

    def test_unavailable_receiver_does_not_hold_the_transition(self):
        # StegVerse-org never runs a cycle here: the reply is durably queued, not awaited.
        self._genesis()
        result = self._peer_egress({"manifest_id": "sv-llm-roundtrip-queued",
                                    "destination": {"organization": ORG}, "payload": {}})
        self.assertEqual(result["disposition"], "ALLOW")
        self.assertIs(result["awaits_receiver"], False)
        self.assertEqual(result["receiver_unavailable_disposition"], "DURABLE_QUEUE_OR_EVENT_EPHEMERAL_MATERIALIZATION")
        self.assertTrue(self._frames(), "an allowed egress must leave a durable frame in the mesh")

    def test_organization_ledgers_are_not_shared(self):
        # Regression for a shared interpreter: StegVerse-org writing its own ledger
        # must not open SV-LLM's. Without SV-LLM's own genesis, its record is refused.
        self.test_undeclared_destination_is_refused_and_nothing_is_published()
        with self.assertRaisesRegex(RuntimeError, "ORG_LEDGER_GENESIS_NOT_DECLARED"):
            self._peer_egress({"manifest_id": "sv-llm-roundtrip-no-genesis",
                               "destination": {"organization": ORG}, "payload": {}})


if __name__ == "__main__":
    unittest.main()
