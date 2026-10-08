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
The last leg hands the run report to GCAT-BCAT-Engine/Publisher through its
existing artifact-transfer adapter, in Publisher's own interpreter, and binds
the PDF and JSON it returns to the original manifest. The test declares the
export's review authorization itself; no owner issued it.

Run:
  STEGVERSE_ORG_DOTGITHUB_ROOT=<StegVerse-org/.github checkout> \
  SV_LLM_DOTGITHUB_ROOT=<SV-LLM/.github checkout> \
  GCAT_BCAT_PUBLISHER_ROOT=<GCAT-BCAT-Engine/Publisher checkout> \
  [SV_LLM_ROUNDTRIP_REPORT=<path>] [SV_LLM_ROUNDTRIP_PUBLISHER_DIR=<dir>] \
  python -m unittest tests.test_sv_llm_intr_roundtrip -v
"""
from __future__ import annotations

import base64
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from stegverse.manifest_builder import build_manifest
from stegverse.review_publisher_transfer import (
    bind_exact_review_return, digest, digest_bytes, prepare_review_transfer,
)

ORG = "StegVerse-org"
PEER = "SV-LLM"
GENESIS = {"mode": "ESTABLISH_GENESIS", "node_ref": "sv-llm-roundtrip", "predecessor": None}
LEDGER_ENV = ("STEGVERSE_REPO_LEDGER_ROOT", "STEGVERSE_ORG_LEDGER_ROOT", "STEGVERSE_REPO_LEDGER_HOME")


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
    # Where the organization's repository ledgers live, for receipt propagation.
    # Supplied like the other ledger locations; never derived from the host.
    env["STEGVERSE_REPO_LEDGER_HOME"] = str(ledger_root / "repo-ledgers")
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
PUBLISHER = "GCAT-BCAT-Engine/Publisher"
RUN_ORIGINAL = "evidence/sv-llm-intr-roundtrip-run.json"
LEG_NAMES = ["SDK_MANIFEST_BUILD", "STEGVERSE_ORG_EGRESS_TO_SV_LLM", "SV_LLM_ORG_LEDGER_GENESIS", "SV_LLM_INGRESS",
             "SV_LLM_EGRESS_TO_STEGVERSE_ORG", "STEGVERSE_ORG_INGRESS_TO_SDK", "PUBLISHER_RENDER_AND_RETURN"]
NOT_PROVEN = [
    "Crossing between separate runners: both organizations ran on one host and crossed through a shared folder.",
    "Origin attestation: needs a TV/TVC-issued credential, and none has been issued.",
    "StegVerse-Labs deciding the governance request and returning it.",
    "Owner-issued Publisher authorization: the review authorization on this export is declared by the test.",
]


def _publisher_export(manifest: dict, legs: list, run_bytes: bytes) -> dict:
    # Publisher's evidence-report package: one section per leg, every section
    # sourced from the exact run report, which travels as the original.
    def section(section_id, heading, body):
        return {"section_id": section_id, "heading": heading, "body": body, "content_class": "OWNER_AUTHORED",
                "fidelity": "semantic_reconstruction", "source_subject_ids": [RUN_ORIGINAL]}

    sections = [section("summary", "Summary",
                        "Route: StegVerse-SDK Manifest Builder -> StegVerse-org/.github egress -> SV-LLM/.github "
                        "ingress -> SV-LLM/.github egress -> StegVerse-org/.github SDK manifest ingress -> "
                        "GCAT-BCAT-Engine/Publisher. Legs 0-5 all ALLOW: %s. Evidence class: "
                        "SAME_HOST_SCRATCH_CODE_PATH_CONFORMANCE_ONLY; each organization ran in its own interpreter "
                        "with its own scratch ledger." % ("yes" if all(e["disposition"] == "ALLOW" for e in legs) else "no"))]
    for entry in legs:
        facts = {k: v for k, v in (entry.get("result") or {}).items()
                 if k in ("failed_predicate", "destination_service", "sdk_manifest_ingress_receipts",
                          "onward_frames", "consumed", "frames_consumed")} if isinstance(entry.get("result"), dict) else {}
        body = "Disposition: %s. %s%s" % (
            entry["disposition"],
            ("Predicate: %s. " % entry["failed_predicate"]) if entry.get("failed_predicate") else "",
            ("Facts: %s." % json.dumps(facts, sort_keys=True, default=str)[:600]) if facts else "")
        sections.append(section("leg-%d" % entry["leg"], "Leg %d - %s" % (entry["leg"], entry["name"]), body))
    sections.append(section("not-proven", "Not proven by this run", " ".join(
        "(%d) %s" % (i, text) for i, text in enumerate(NOT_PROVEN, start=1))))
    sections.append(section("reproduce", "Reproduce",
                            "StegVerse-SDK workflow sv-llm-intr-roundtrip.yml runs tests/test_sv_llm_intr_roundtrip.py "
                            "against pinned StegVerse-org/.github, SV-LLM/.github and GCAT-BCAT-Engine/Publisher "
                            "commits. The exact run report is attached to this report as %s." % RUN_ORIGINAL))
    bundle = {
        "schema_version": "stegverse.publisher.evidence-report-package/v1",
        "export_id": "sv-llm-intr-roundtrip-001",
        "created_at": "2026-10-08T00:00:00Z",
        "authorization": {
            "authority_ref": "sdk-roundtrip-test-declared-not-owner-issued", "receipt_id": "sdk-roundtrip-test",
            "status": "active", "revoked": False, "destination": PUBLISHER, "purpose": "EXTERNAL_EVALUATOR_REVIEW",
            "scope": [RUN_ORIGINAL], "allowed_formats": ["pdf", "json"], "expires_at": "2099-12-31T23:59:59Z",
        },
        "requested_formats": ["pdf", "json"],
        "source": {"repository": "StegVerse-org/StegVerse-SDK", "release": "sv-llm-intr-roundtrip-test",
                   "verification_root": digest(manifest), "event_ids": [RUN_ORIGINAL], "vault_class": "SOURCE_REPORT"},
        "evidence": [{"subject_id": RUN_ORIGINAL, "path": RUN_ORIGINAL, "content_hash": digest_bytes(run_bytes),
                      "bytes": len(run_bytes), "media_type": "application/json", "fidelity": "exact",
                      "retention_class": "full_fidelity", "payload_available": True, "derived_index": False,
                      "restricted": False, "superseded": False, "contains_credentials": False, "artifact_refs": []}],
        "document": {"document_id": "sv-llm-intr-roundtrip-001", "document_type": "REPORT",
                     "title": "Manifest Builder InTr round trip: StegVerse-org -> SV-LLM -> StegVerse-org -> SDK",
                     "authors": [{"name": "StegVerse-SDK round-trip test", "affiliation": "StegVerse"}],
                     "sections": sections},
        "redaction": {"profile": "sdk-roundtrip-test", "removed_paths": [], "restricted_content_present": False,
                      "review_state": "OWNER_APPROVED"},
        "publication_authorized": False, "release_authorized": False, "execution_authorized": False,
        "authority_effect": "NONE",
    }
    bundle["export_sha256"] = digest(bundle)
    return bundle


def _run_original(run_bytes: bytes) -> dict:
    return {"path": RUN_ORIGINAL, "media_type": "application/json", "sha256": digest_bytes(run_bytes),
            "bytes": len(run_bytes), "content_base64": base64.b64encode(run_bytes).decode("ascii"),
            "source_class": "SDK_SOURCE_VALIDATED_ARTIFACT"}


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

    def _report(self, manifest, *, names=LEG_NAMES, write=True) -> dict:
        reached = {e["leg"] for e in self.legs}
        publisher = next((e.get("result") for e in self.legs if e["name"] == "PUBLISHER_RENDER_AND_RETURN"), None)
        report = {
            "schema": "stegverse.sdk.sv-llm-intr-roundtrip-run/v0.1",
            "task": "SV-LLM-INTR-ROUNDTRIP-TEST-PROPOSAL-001",
            "route": [ORG, PEER, ORG, "StegVerse-SDK", PUBLISHER],
            "manifest_sha256": (manifest or {}).get("payload_sha256") if isinstance(manifest, dict) else None,
            "legs": self.legs + [{"leg": i, "name": n, "disposition": "NOT_REACHED"}
                                 for i, n in enumerate(names) if i not in reached],
            "all_legs_allow": all(e["disposition"] == "ALLOW" for e in self.legs) and len(reached) == len(names),
            "publisher_return": publisher if isinstance(publisher, dict) else "NOT_PRODUCED",
            "not_proven": NOT_PROVEN,
            "evidence_class": "SAME_HOST_SCRATCH_CODE_PATH_CONFORMANCE_ONLY",
            "process_isolation": "ONE_INTERPRETER_PER_ORGANIZATION_LEG",
            "authority_effect": "NONE_TEST_ONLY",
        }
        out = os.environ.get("SV_LLM_ROUNDTRIP_REPORT")
        if out and write:
            Path(out).write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
        return report

    def test_manifest_crosses_to_sv_llm_and_returns(self):
        manifest = None

        def leg0():
            nonlocal manifest
            manifest = build_manifest(data={"probe": "sv-llm-roundtrip"}, source_framework="StegVerse-SDK",
                                      source_output_id="sv-llm-roundtrip-001",
                                      processor_request=_governance_request(),
                                      created_at="2026-10-08T00:00:00Z", external_review=True,
                                      publisher_destination={"type": "SDK_CONSOLE_SESSION",
                                                             "session_ref": "sv-llm-roundtrip"})
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
            # SV-LLM's node state is supplied, as its materializer would; without
            # it SV-LLM records a FAIL_CLOSED and consumes nothing.
            node_state = self.scratch / "sv-llm-node-state"
            node_state.mkdir(exist_ok=True)
            consumed = _run_in_org(self.peer_root, self.peer_ledger, "org-runtime/crossing.py", "ingress",
                                   mesh_root=str(self.mesh), node_state_root=str(node_state),
                                   root=str(self.peer_root))
            if not consumed:
                return {"disposition": "DENY", "failed_predicate": "NO_FRAME_CONSUMED_BY_SV_LLM"}
            # Each consumed entry carries SV-LLM's own disposition. A recorded
            # refusal is a result, not a consumption, so it is never read as ALLOW.
            refused = [entry for entry in consumed
                       if not isinstance(entry, dict) or entry.get("disposition") != "ALLOW"]
            if refused:
                first = refused[0] if isinstance(refused[0], dict) else {}
                return {"disposition": first.get("disposition") or "FAIL_CLOSED",
                        "failed_predicate": first.get("failed_predicate") or "SV_LLM_INGRESS_NOT_ALLOWED",
                        "result": first}
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

        def leg5_publisher():
            # The manifest selected Publisher; the run so far is the original it renders.
            publisher_root = os.environ.get("GCAT_BCAT_PUBLISHER_ROOT")
            if not publisher_root:
                return {"disposition": "FAIL_CLOSED", "failed_predicate": "PUBLISHER_CHECKOUT_NOT_SUPPLIED"}
            run_bytes = (json.dumps(self._report(manifest, names=LEG_NAMES[:-1], write=False), indent=2,
                                    sort_keys=True, default=str) + "\n").encode("utf-8")
            prepared = prepare_review_transfer(manifest=manifest,
                                               authorized_export_bundle=_publisher_export(manifest, self.legs, run_bytes),
                                               original_assets=[_run_original(run_bytes)],
                                               transfer_id="sv-llm-intr-roundtrip-001")
            work = self.scratch / "publisher"
            work.mkdir()
            (work / "transfer.json").write_bytes(prepared["transfer_bytes"])
            done = subprocess.run([sys.executable, "-B", "tools/process_intr_artifact_transfer.py",
                                   str(work / "transfer.json"), "--output-dir", str(work / "out"),
                                   "--return-packet", str(work / "return.json")],
                                  capture_output=True, text=True, cwd=publisher_root, timeout=600)
            if done.returncode:
                return {"disposition": "DENY", "failed_predicate": "PUBLISHER_REJECTED_TRANSFER",
                        "reason": done.stderr[-500:]}
            returned = (work / "return.json").read_bytes()
            # The SDK accepts the return only if it binds to this transfer and this manifest.
            bound = bind_exact_review_return(prepared=prepared, manifest=manifest,
                                             manifest_receipt_id="MR-" + digest(manifest)[7:39].upper(),
                                             publisher_return_bytes=returned)
            artifacts = {a["format"]: a for a in json.loads(returned)["artifacts"]}
            if not {"pdf", "json"} <= set(artifacts):
                return {"disposition": "DENY", "failed_predicate": "PUBLISHER_RETURN_MISSING_PDF_OR_JSON",
                        "formats": sorted(artifacts)}
            out_dir = os.environ.get("SV_LLM_ROUNDTRIP_PUBLISHER_DIR")
            if out_dir:
                Path(out_dir).mkdir(parents=True, exist_ok=True)
                for fmt in ("pdf", "json"):
                    (Path(out_dir) / artifacts[fmt]["path"]).write_bytes(
                        base64.b64decode(artifacts[fmt]["content_base64"]))
                (Path(out_dir) / RUN_ORIGINAL.split("/")[-1]).write_bytes(run_bytes)
                (Path(out_dir) / "publisher-return.json").write_bytes(returned)
            return {"disposition": "ALLOW", "transfer_sha256": prepared["transfer_sha256"],
                    "return_sha256": digest_bytes(returned), "manifest_sha256": digest(manifest),
                    "pdf": {k: artifacts["pdf"][k] for k in ("path", "sha256", "bytes")},
                    "json": {k: artifacts["json"][k] for k in ("path", "sha256", "bytes")},
                    "original": {"path": RUN_ORIGINAL, "sha256": digest_bytes(run_bytes)},
                    "sdk_return_binding_observed": bound.get("sdk_return_binding_observed"),
                    "communication_complete": bound.get("communication_complete")}

        for i, (name, fn) in enumerate([("SDK_MANIFEST_BUILD", leg0), ("STEGVERSE_ORG_EGRESS_TO_SV_LLM", leg1),
                                        ("SV_LLM_ORG_LEDGER_GENESIS", leg2_genesis), ("SV_LLM_INGRESS", leg2), ("SV_LLM_EGRESS_TO_STEGVERSE_ORG", leg3),
                                        ("STEGVERSE_ORG_INGRESS_TO_SDK", leg4),
                                        ("PUBLISHER_RENDER_AND_RETURN", leg5_publisher)]):
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
