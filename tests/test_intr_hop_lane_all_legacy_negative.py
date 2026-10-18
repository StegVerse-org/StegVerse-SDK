"""InTr hop lane: a correlated chain built only from LEGACY receipts is never live evidence.

Negative cases for the remediation lane (LLM-adapter#368, H36). A receipt is
LEGACY when it reached the organization-ledger ref before the peer's
supplied-epoch writer was introduced. A hop whose emission, arrival and
closure are all LEGACY carries no authentic live evidence, so the readback
must report it as not sent: never ``PASS``, ``ledger_state`` ``UNSENT``,
``authenticity_claimed`` False, and the six disposition fields on the
non-ALLOW hop.

The cases exercise public entrypoints only (``discover_peers``, ``run_live``,
``pair_ledger_state``) so they apply unchanged to any version of the module.
A version whose ``run_live`` takes no ``writer_introduction`` has no LEGACY
classification at all; there the LEGACY cases are skipped with that reason and
only the positive control runs. Every receipt here is fabricated in a
temporary directory; nothing is appended to a real ledger and no external
machine is contacted or awaited.
"""
from __future__ import annotations

import inspect
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

import stegverse.intr_destination_hop_lane as lane
from stegverse.intr_destination_hop_lane import (
    ACK_CLASS,
    CLOSED_CLASS,
    EMITTED_CLASS,
    INGRESS_CLASS,
    LEDGER_REF,
    ORG_SCHEMA,
    PROFILE_ID,
    REPO_SCHEMA,
    discover_peers,
    organization_slug,
    run_live,
    sha256,
)

_SIX = ("failure_code", "failed_predicate", "required_evidence_or_repair",
        "retry_entrypoint", "owning_existing_goal", "next_attempt")

# Receipts committed now are before this cutoff, so every one of them is LEGACY.
_WRITER_AFTER_EVERY_RECEIPT = {"commit": "writer", "committed_at_unix": 2 ** 40, "source": "TEST"}
# Receipts committed now are after this cutoff, so none of them is LEGACY.
_WRITER_BEFORE_EVERY_RECEIPT = {"commit": "writer", "committed_at_unix": 1, "source": "TEST"}


def _classifies_legacy() -> bool:
    return "writer_introduction" in inspect.signature(run_live).parameters


def _pair_state_takes_legacy() -> bool:
    pair_state = getattr(lane, "pair_ledger_state", None)
    return pair_state is not None and "legacy" in inspect.signature(pair_state).parameters


def _live(peers, introduction=None):
    if introduction is not None and _classifies_legacy():
        return run_live(peers, fetch=False, writer_introduction=lambda peer: introduction)
    return run_live(peers, fetch=False)


def _advertise(root: Path, organization: str) -> None:
    service = organization_slug(organization) + "." + PROFILE_ID
    (root / "org-runtime").mkdir(parents=True, exist_ok=True)
    (root / "org-boundary" / "registry").mkdir(parents=True, exist_ok=True)
    (root / "org-runtime" / "interlock-intr.json").write_text(json.dumps({
        "ingress": {"capability_endpoint_bindings": [{
            "profile_id": PROFILE_ID,
            "receiving_operation": {"addressed_service": service,
                                    "operation_id": "ORGANIZATION_INTR_DESTINATION_INGRESS"},
        }]},
        "egress": {"peer_capability_resolution": {"proven_on_this_organization": [service]}},
    }), encoding="utf-8")
    (root / "org-boundary" / "registry" / "services.json").write_text(json.dumps({
        "organization": organization,
        "services": [{"service_id": service, "repository": organization + "/.github",
                      "capability_profile_id": PROFILE_ID}],
    }), encoding="utf-8")


def _peer(test: unittest.TestCase, root: Path, organization: str) -> dict:
    _advertise(root, organization)
    peers = discover_peers([root])
    test.assertEqual(len(peers), 1)
    (root / ".stegverse" / "transition-ledger").mkdir(parents=True, exist_ok=True)
    (root / ".stegverse" / "transition-ledger" / "contract.json").write_text(json.dumps({
        "repository_ledger_location": {"namespace": "repository-ledger/" + organization + "/.github"},
    }), encoding="utf-8")
    return peers[0]


def _commit(root: Path) -> None:
    env = {**os.environ, "GIT_AUTHOR_NAME": "lane", "GIT_AUTHOR_EMAIL": "lane@example.invalid",
           "GIT_COMMITTER_NAME": "lane", "GIT_COMMITTER_EMAIL": "lane@example.invalid"}
    for command in (["git", "init", "-q"], ["git", "add", "-A"], ["git", "commit", "-q", "-m", "ledger"],
                    ["git", "update-ref", LEDGER_REF, "HEAD"]):
        subprocess.run(command, cwd=root, check=True, env=env)


def _hb() -> dict:
    return {
        "epoch": 32, "generation": 32, "heartbeat_id": "HB:32", "phase_offset_ns": 0,
        "frequency_hz": 100, "progression_dependency": "OSCILLATOR_ONLY",
        "derived_from_clock": False, "authority_effect": "NONE",
    }


def _repo(previous, transition_id, transition_class, evidence, repository):
    body = {
        "schema": REPO_SCHEMA, "repository": repository, "transition_id": transition_id,
        "transition_class": transition_class, "predecessor_state_sha256": "sha256:" + "ab" * 32,
        "successor_state_sha256": "sha256:" + "cd" * 32, "evidence": evidence,
        "authority_effect": "NONE", "hb_reference": _hb(), "previous_receipt_sha256": previous,
    }
    return {**body, "receipt_sha256": sha256(body)}


def _org(previous, source):
    body = {
        "schema": ORG_SCHEMA, "organization": source["repository"].split("/")[0],
        "source_transition_sha256": source["receipt_sha256"], "source_transition_id": source["transition_id"],
        "source_repository": source["repository"], "repo_receipt_sha256": source["receipt_sha256"],
        "repo_transition_id": source["transition_id"], "org_transition_class": "REPO_STATE_PROPAGATION",
        "predecessor_org_state_sha256": source["predecessor_state_sha256"],
        "successor_org_state_sha256": source["successor_state_sha256"],
        "boundary_evidence": {}, "authority_effect": "NONE", "hb_reference": source["hb_reference"],
        "previous_receipt_sha256": previous,
    }
    return {**body, "receipt_sha256": sha256(body)}


def _store(root: Path, receipts: list, sources: list) -> None:
    (root / "receipts").mkdir(parents=True, exist_ok=True)
    (root / "source-receipts").mkdir(parents=True, exist_ok=True)
    for folder, items in (("receipts", receipts), ("source-receipts", sources)):
        for receipt in items:
            name = receipt["receipt_sha256"].split(":", 1)[1] + ".json"
            (root / folder / name).write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    head = {"receipt_sha256": receipts[-1]["receipt_sha256"]} if receipts else {}
    (root / "HEAD.json").write_text(json.dumps(head, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _pair_receipts(sender: str, dest: str, communication_id: str, packet_id: str):
    address = organization_slug(dest) + "." + PROFILE_ID
    emitted = _repo(None, "ORGANIZATION_EGRESS_EMITTED:" + packet_id, EMITTED_CLASS, {
        "packet_id": packet_id, "destination_organization": dest, "destination_service": address,
        "payload_sha256": "sha256:" + "11" * 32, "disposition": "ALLOW",
    }, sender + "/.github")
    closed = _repo(emitted["receipt_sha256"], "ORGANIZATION_EGRESS_CLOSED:" + packet_id, CLOSED_CLASS, {
        "communication_id": communication_id, "request_packet_id": packet_id,
        "destination_organization": dest, "response_message_class": ACK_CLASS, "disposition": "ALLOW",
    }, sender + "/.github")
    arrived = _repo(None, "ORGANIZATION_INTR_DESTINATION_INGRESS:" + packet_id, INGRESS_CLASS, {
        "communication_id": communication_id, "profile_id": PROFILE_ID, "disposition": "ALLOW",
        "packet_id": packet_id,
    }, dest + "/.github")
    return emitted, closed, arrived


def _write_org(root: Path, organization: str, repo_receipts: list) -> None:
    linked, previous = [], None
    for receipt in repo_receipts:
        body = {key: value for key, value in receipt.items() if key != "receipt_sha256"}
        body["previous_receipt_sha256"] = previous
        stamped = {**body, "receipt_sha256": sha256(body)}
        linked.append(stamped)
        previous = stamped["receipt_sha256"]
    org_linked, previous = [], None
    for receipt in linked:
        org = _org(previous, receipt)
        org_linked.append(org)
        previous = org["receipt_sha256"]
    _store(root, org_linked, linked)
    _store(root / "repository-ledger" / organization / ".github", linked, [])


class AllLegacyCorrelatedChainTests(unittest.TestCase):
    """A fully correlated Alpha<->Beta chain; only the writer cutoff decides LEGACY."""

    def _ledgers(self, base: Path):
        alpha = _peer(self, base / "alpha", "Alpha")
        beta = _peer(self, base / "beta", "Beta")
        forward = _pair_receipts("Alpha", "Beta", "legacy-alpha-beta", "pkt-ab")
        back = _pair_receipts("Beta", "Alpha", "legacy-beta-alpha", "pkt-ba")
        _write_org(Path(alpha["root"]), "Alpha", [forward[0], forward[1], back[2]])
        _write_org(Path(beta["root"]), "Beta", [back[0], back[1], forward[2]])
        _commit(Path(alpha["root"]))
        _commit(Path(beta["root"]))
        return alpha, beta

    def test_control_the_same_chain_with_live_receipts_passes(self):
        # Proves the fixture is a complete correlated chain, so a non-PASS
        # below is caused by the LEGACY classification and nothing else.
        with tempfile.TemporaryDirectory() as tmp:
            peers = self._ledgers(Path(tmp))
            report = _live(peers, _WRITER_BEFORE_EVERY_RECEIPT)
        self.assertEqual(report["counts"]["PASS"], 2, [hop["findings"] for hop in report["hops"]])
        self.assertTrue(report["authenticity_claimed"])

    @unittest.skipUnless(_classifies_legacy(), "run_live has no writer_introduction: nothing is LEGACY here")
    def test_an_all_legacy_chain_is_unsent_never_pass_and_claims_no_authenticity(self):
        with tempfile.TemporaryDirectory() as tmp:
            peers = self._ledgers(Path(tmp))
            report = _live(peers, _WRITER_AFTER_EVERY_RECEIPT)
        self.assertEqual(report["hop_count"], 2)
        self.assertEqual(report["counts"].get("PASS", 0), 0, [hop["findings"] for hop in report["hops"]])
        self.assertIs(report["authenticity_claimed"], False)
        for hop in report["hops"]:
            pair = (hop["sender_slug"], hop["destination_slug"])
            self.assertNotEqual(hop["status"], "PASS", pair)
            self.assertIs(hop["authenticity_claimed"], False, pair)
            self.assertIsNone(hop["authenticity_basis"], pair)
            self.assertEqual(hop["ledger_state"], "UNSENT", pair)
            self.assertEqual(hop["communication_ids_read_back"], [], pair)

    @unittest.skipUnless(_classifies_legacy() and hasattr(lane, "non_allow_fields"),
                         "this version emits no six-field disposition or no LEGACY classification")
    def test_an_all_legacy_hop_carries_the_six_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            peers = self._ledgers(Path(tmp))
            report = _live(peers, _WRITER_AFTER_EVERY_RECEIPT)
        for hop in report["hops"]:
            for field in _SIX:
                self.assertIsInstance(hop.get(field), str, (field, hop["status"], hop["findings"]))
                self.assertTrue(hop[field].strip(), (field, hop["status"], hop["findings"]))

    @unittest.skipUnless(_pair_state_takes_legacy(), "pair_ledger_state takes no legacy receipts")
    def test_pair_state_of_an_all_legacy_sender_chain_is_unsent(self):
        emitted, closed, _ = _pair_receipts("Alpha", "Beta", "legacy-alpha-beta", "pkt-ab")
        chain = [emitted, closed]
        address = "beta." + PROFILE_ID
        self.assertEqual(lane.pair_ledger_state(chain, "Beta", address), "CLOSED")
        everything = [receipt["receipt_sha256"] for receipt in chain]
        self.assertEqual(lane.pair_ledger_state(chain, "Beta", address, legacy=everything), "UNSENT")


if __name__ == "__main__":
    unittest.main()
