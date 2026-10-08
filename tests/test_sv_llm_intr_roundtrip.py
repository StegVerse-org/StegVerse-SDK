"""Manifest Builder -> InTr round trip: StegVerse-org -> SV-LLM -> StegVerse-org -> SDK.

Proposed test. It drives the real boundary code of both organizations, leg by
leg, and stops at the first leg that does not ALLOW. Every leg's disposition is
written to a JSON run report, so a failure is a named predicate rather than a
claim. Both organization checkouts are copied to scratch first, so no ledger in
either checkout is written by a test run.

The test passes only when every leg allows. A loopback does not count: leg 2
must be consumed by SV-LLM's own crossing code, and leg 4 by StegVerse-org's.
The Publisher PDF is not produced here; only GCAT-BCAT-Engine/Publisher renders
it. The run report is the JSON half of the Publisher return.

Run:
  STEGVERSE_ORG_DOTGITHUB_ROOT=<StegVerse-org/.github checkout> \
  SV_LLM_DOTGITHUB_ROOT=<SV-LLM/.github checkout> \
  [SV_LLM_ROUNDTRIP_REPORT=<path>] \
  python -m unittest tests.test_sv_llm_intr_roundtrip -v
"""
from __future__ import annotations

import importlib.util
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from stegverse.manifest_builder import build_manifest

ORG = "StegVerse-org"
PEER = "SV-LLM"
GENESIS = {"mode": "ESTABLISH_GENESIS", "node_ref": "sv-llm-roundtrip", "predecessor": None}
LEDGER_ENV = ("STEGVERSE_REPO_LEDGER_ROOT", "STEGVERSE_ORG_LEDGER_ROOT")


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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
        previous = {name: os.environ.get(name) for name in LEDGER_ENV}
        for name in LEDGER_ENV:
            os.environ[name] = str(self.scratch / "ledger" / name.lower())
        self.addCleanup(lambda: [os.environ.pop(n, None) if v is None else os.environ.__setitem__(n, v)
                                 for n, v in previous.items()])
        self.legs: list[dict] = []

    def _leg(self, leg: int, name: str, fn):
        try:
            result = fn()
            disposition = result.get("disposition", "ALLOW") if isinstance(result, dict) else "ALLOW"
            entry = {"leg": leg, "name": name, "disposition": disposition, "result": result}
        except (Exception, SystemExit) as exc:  # a crash or refusal exit is a fail-closed leg, recorded with its predicate
            entry = {"leg": leg, "name": name, "disposition": "FAIL_CLOSED",
                     "failed_predicate": type(exc).__name__, "reason": str(exc)[:500]}
        self.legs.append(entry)
        return entry

    def _report(self, manifest) -> dict:
        reached = {e["leg"] for e in self.legs}
        names = ["SDK_MANIFEST_BUILD", "STEGVERSE_ORG_EGRESS_TO_SV_LLM", "SV_LLM_INGRESS",
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
            egress = _load("roundtrip_org_egress", self.org_root / "resident-runtime/organization_egress_boundary.py")
            return egress.emit(PEER, {"message_class": "ecosystem.work.request",
                                      "communication_id": "sv-llm-roundtrip-001",
                                      "subject": "manifest builder round trip",
                                      "body": {"manifest": manifest}},
                               standing=GENESIS, root=self.org_root, mesh_root=self.mesh, hb_epoch=32)

        def leg2():
            crossing = _load("roundtrip_sv_llm_crossing", self.peer_root / "org-runtime/crossing.py")
            consumed = crossing.ingress(mesh_root=self.mesh, root=self.peer_root)
            if not consumed:
                return {"disposition": "DENY", "failed_predicate": "NO_FRAME_CONSUMED_BY_SV_LLM"}
            return {"disposition": "ALLOW", "consumed": consumed}

        def leg3():
            crossing = _load("roundtrip_sv_llm_crossing_out", self.peer_root / "org-runtime/crossing.py")
            reply = {"manifest_id": "sv-llm-roundtrip-reply-001", "destination": {"organization": ORG},
                     "in_reply_to": "sv-llm-roundtrip-001", "payload": {"manifest": manifest}}
            return crossing.egress(reply, standing=GENESIS, mesh_root=self.mesh, root=self.peer_root)

        def leg4():
            cycle = _load("roundtrip_org_cycle", self.org_root / "resident-runtime/federation_cycle.py")
            node_state = self.scratch / "org-node-state"
            node_state.mkdir(exist_ok=True)
            result = cycle.main(mesh_root=self.mesh, node_state_root=node_state)
            if not isinstance(result, dict) or not result.get("frames_consumed"):
                return {"disposition": "DENY", "failed_predicate": "NO_REPLY_FRAME_CONSUMED_BY_STEGVERSE_ORG",
                        "result": result}
            return {"disposition": "ALLOW", "result": result}

        for i, (name, fn) in enumerate([("SDK_MANIFEST_BUILD", leg0), ("STEGVERSE_ORG_EGRESS_TO_SV_LLM", leg1),
                                        ("SV_LLM_INGRESS", leg2), ("SV_LLM_EGRESS_TO_STEGVERSE_ORG", leg3),
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


if __name__ == "__main__":
    unittest.main()
