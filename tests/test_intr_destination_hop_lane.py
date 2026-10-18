"""InTr destination hop lane: discovery, receipt readback, and fabricated crossings.

Federation directories are not a peer source. A peer is a checkout that
advertises ``<slug>.intr-destination``. Fabricated crossings run only when
organization checkouts are supplied; the cases here that build their own
ledgers do not need one.
"""
from __future__ import annotations

import json
import os
import re
import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import stegverse.intr_destination_hop_lane as lane
from stegverse.intr_destination_hop_lane import (
    ACK_CLASS,
    CANDIDATE_ORGANIZATIONS,
    CLOSED_CLASS,
    CONTRACT_RELATIVE,
    EMITTED_CLASS,
    FEDERATION_READ_TOKEN_ENV,
    INGRESS_CLASS,
    LEDGER_REF,
    ORG_SCHEMA,
    OVERLAY_RELATIVE,
    PROFILE_ID,
    REGISTRY_RELATIVE,
    REPO_SCHEMA,
    REQUEST_CLASS,
    discover_peers,
    discover_peers_from_github,
    github_read_file,
    hop_receipt_findings,
    integrity_findings,
    main,
    ordered_pairs,
    organization_slug,
    render_markdown,
    run_fabricated,
    run_live,
    sha256,
    walk_posix,
)

_GRANT = re.compile(r"\bgrants?\b", re.IGNORECASE)
_SIX = ("failure_code", "failed_predicate", "required_evidence_or_repair",
        "retry_entrypoint", "owning_existing_goal", "next_attempt")
_GOAL = "StegVerse-Labs/.github#2897 / StegVerse-org/.github#162 P0-runtime-and-custody"


def _workflow_epoch_gate(job: str) -> str:
    """The orchestrate job's own python hb_epoch gate, read out of the workflow file."""
    body = job.split("python - <<'PY'\n", 1)[1].split("\n          PY\n", 1)[0]
    return "\n".join(line[10:] for line in body.splitlines())


def _assert_six(test, item):
    for field in _SIX:
        test.assertIsInstance(item.get(field), str, (field, item))
        test.assertTrue(item[field].strip(), (field, item))
    test.assertEqual(item["owning_existing_goal"], _GOAL)


def _advertise(root: Path, organization: str, *, bind: bool = True, address: str | None = None) -> None:
    slug = organization_slug(organization)
    service = address if address is not None else slug + "." + PROFILE_ID
    (root / "org-runtime").mkdir(parents=True, exist_ok=True)
    (root / "org-boundary" / "registry").mkdir(parents=True, exist_ok=True)
    bindings = []
    services = []
    if bind:
        bindings.append({
            "profile_id": PROFILE_ID,
            "receiving_operation": {
                "addressed_service": service,
                "operation_id": "ORGANIZATION_INTR_DESTINATION_INGRESS",
            },
        })
        services.append({
            "service_id": service,
            "repository": organization + "/.github",
            "capability_profile_id": PROFILE_ID,
        })
    (root / "org-runtime" / "interlock-intr.json").write_text(json.dumps({
        "ingress": {"capability_endpoint_bindings": bindings},
        "egress": {"peer_capability_resolution": {"proven_on_this_organization": [service] if bind else []}},
    }), encoding="utf-8")
    (root / "org-boundary" / "registry" / "services.json").write_text(json.dumps({
        "organization": organization, "services": services,
    }), encoding="utf-8")
    # Not a peer source. Invalid on purpose: discovery must not open it.
    (root / "org-boundary" / "registry" / "federation.json").write_text("{not-json", encoding="utf-8")


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


def _store(root: Path, receipts: list[dict], sources: list[dict] | None = None) -> None:
    (root / "receipts").mkdir(parents=True, exist_ok=True)
    (root / "source-receipts").mkdir(parents=True, exist_ok=True)
    for receipt in receipts:
        name = receipt["receipt_sha256"].split(":", 1)[1] + ".json"
        (root / "receipts" / name).write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for source in sources or []:
        name = source["receipt_sha256"].split(":", 1)[1] + ".json"
        (root / "source-receipts" / name).write_text(json.dumps(source, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    head = {"receipt_sha256": receipts[-1]["receipt_sha256"]} if receipts else {}
    (root / "HEAD.json").write_text(json.dumps(head, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _pair_receipts(sender: str, dest: str, address: str, communication_id: str, packet_id: str):
    sender_repo_name = sender + "/.github"
    dest_repo_name = dest + "/.github"
    emitted = _repo(None, "ORGANIZATION_EGRESS_EMITTED:" + packet_id, EMITTED_CLASS, {
        "packet_id": packet_id, "destination_organization": dest, "destination_service": address,
        "payload_sha256": "sha256:" + "11" * 32, "disposition": "ALLOW",
    }, sender_repo_name)
    closed = _repo(emitted["receipt_sha256"], "ORGANIZATION_EGRESS_CLOSED:" + packet_id, CLOSED_CLASS, {
        "communication_id": communication_id, "request_packet_id": packet_id,
        "destination_organization": dest, "response_message_class": ACK_CLASS, "disposition": "ALLOW",
    }, sender_repo_name)
    arrived = _repo(None, "ORGANIZATION_INTR_DESTINATION_INGRESS:" + packet_id, INGRESS_CLASS, {
        "communication_id": communication_id, "profile_id": PROFILE_ID, "disposition": "ALLOW",
        "packet_id": packet_id,
    }, dest_repo_name)
    return emitted, closed, arrived



def _WRITER_BEFORE_EVERY_RECEIPT(peer):
    """An observed writer introduction older than every fabricated receipt: none is LEGACY."""
    return {"commit": "writer", "committed_at_unix": 1, "source": "TEST"}

class DiscoveryTests(unittest.TestCase):
    def test_peers_are_advertised_addresses_and_the_federation_file_is_not_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _advertise(root / "alpha", "Alpha")
            _advertise(root / "beta", "Beta Org")
            _advertise(root / "silent", "Silent", bind=False)
            _advertise(root / "misaddressed", "Misaddressed", address="not-the-slug.intr-destination")
            peers = discover_peers([root / "alpha", root / "beta", root / "silent", root / "misaddressed"])
        self.assertEqual([peer["slug"] for peer in peers], ["alpha", "beta-org"])
        self.assertEqual(peers[0]["address"], "alpha.intr-destination")
        self.assertEqual(peers[1]["address"], "beta-org.intr-destination")
        self.assertTrue(all(peer["peer_source"] == "ADVERTISED_CAPABILITY" for peer in peers))

    def test_ordered_pairs_are_one_way_and_exclude_self(self):
        peers = [{"slug": "a"}, {"slug": "b"}, {"slug": "c"}]
        pairs = [(s["slug"], d["slug"]) for s, d in ordered_pairs(peers)]
        self.assertEqual(pairs, [("a", "b"), ("a", "c"), ("b", "a"), ("b", "c"), ("c", "a"), ("c", "b")])
        self.assertNotIn(("a", "a"), pairs)


class ReceiptReadbackTests(unittest.TestCase):
    def _views(self, sender_repo, sender_org, dest_repo, dest_org):
        return (
            {"present": True, "chain": sender_repo, "sources": {item["receipt_sha256"]: item for item in sender_repo}, "findings": []},
            {"present": True, "chain": sender_org, "sources": {item["source_transition_sha256"]: next(s for s in sender_repo if s["receipt_sha256"] == item["repo_receipt_sha256"]) for item in sender_org}, "findings": []},
            {"present": True, "chain": dest_repo, "sources": {item["receipt_sha256"]: item for item in dest_repo}, "findings": []},
            {"present": True, "chain": dest_org, "sources": {item["source_transition_sha256"]: next(s for s in dest_repo if s["receipt_sha256"] == item["repo_receipt_sha256"]) for item in dest_org}, "findings": []},
        )

    def _hop(self, communication_id, packet_id, dest, address):
        return {
            "communication_id": communication_id, "packet_id": packet_id,
            "destination_organization": dest, "destination_service": address,
            "payload_sha256": "sha256:" + "11" * 32, "hb_epoch": 32,
        }

    def test_a_correlated_pair_has_no_findings(self):
        emitted, closed, arrived = _pair_receipts("Alpha", "Beta", "beta.intr-destination", "cid-1", "pkt-1")
        sender_org = [_org(None, emitted), _org(None, closed)]
        sender_org[1] = _org(sender_org[0]["receipt_sha256"], closed)
        dest_org = [_org(None, arrived)]
        repo_s, org_s, repo_d, org_d = self._views([emitted, closed], sender_org, [arrived], dest_org)
        self.assertEqual(integrity_findings(repo_s, org_s), [])
        self.assertEqual(integrity_findings(repo_d, org_d), [])
        self.assertEqual(hop_receipt_findings(self._hop("cid-1", "pkt-1", "Beta", "beta.intr-destination"),
                                              repo_s["chain"], org_s["chain"], repo_d["chain"], org_d["chain"]), [])

    def test_duplicate_closure_and_communication_mismatch_and_orphan_are_findings(self):
        emitted, closed, arrived = _pair_receipts("Alpha", "Beta", "beta.intr-destination", "cid-1", "pkt-1")
        duplicate = _repo(closed["receipt_sha256"], "ORGANIZATION_EGRESS_CLOSED:other", CLOSED_CLASS, {
            "communication_id": "cid-1", "request_packet_id": "pkt-1", "destination_organization": "Beta",
            "response_message_class": ACK_CLASS, "disposition": "ALLOW",
        }, "Alpha/.github")
        sender_org = [_org(None, emitted)]
        findings = hop_receipt_findings(
            self._hop("cid-1", "pkt-1", "Beta", "beta.intr-destination"),
            [emitted, closed, duplicate], sender_org, [arrived], [_org(None, arrived)])
        self.assertIn("DUPLICATE_SENDER_CLOSURE_RECEIPT", findings)
        mismatched = dict(arrived)
        # A different communication id is a missing ingress for this hop, not a second copy.
        other = _repo(None, "ORGANIZATION_INTR_DESTINATION_INGRESS:pkt-1", INGRESS_CLASS, {
            "communication_id": "someone-else", "profile_id": PROFILE_ID, "disposition": "ALLOW",
        }, "Beta/.github")
        missing = hop_receipt_findings(
            self._hop("cid-1", "pkt-1", "Beta", "beta.intr-destination"),
            [emitted, closed], [_org(None, emitted), _org(None, closed)], [other], [_org(None, other)])
        self.assertIn("DESTINATION_INGRESS_RECEIPT_MISSING", missing)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _store(root, [emitted])
            (root / "receipts" / "orphan.json").write_text("{}\n", encoding="utf-8")
            walked = walk_posix(root)
            self.assertIn("ORPHAN_RECEIPT", walked["findings"])

    def test_a_broken_receipt_body_does_not_verify(self):
        emitted, _, _ = _pair_receipts("Alpha", "Beta", "beta.intr-destination", "cid-1", "pkt-1")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _store(root, [emitted])
            path = root / "receipts" / (emitted["receipt_sha256"].split(":", 1)[1] + ".json")
            document = json.loads(path.read_text(encoding="utf-8"))
            document["transition_id"] = "rewritten"
            path.write_text(json.dumps(document), encoding="utf-8")
            walked = walk_posix(root)
            self.assertIn("RECEIPT_DOES_NOT_VERIFY_AGAINST_ITS_BODY", walked["findings"])


class LiveLedgerTests(unittest.TestCase):
    def _peer(self, root: Path, organization: str) -> dict:
        _advertise(root, organization)
        peers = discover_peers([root])
        self.assertEqual(len(peers), 1)
        (root / ".stegverse" / "transition-ledger").mkdir(parents=True, exist_ok=True)
        namespace = "repository-ledger/" + organization + "/.github"
        (root / ".stegverse" / "transition-ledger" / "contract.json").write_text(json.dumps({
            "repository_ledger_location": {"namespace": namespace},
        }), encoding="utf-8")
        return peers[0]

    def _commit(self, root: Path, ref: str | None) -> None:
        env = {**os.environ, "GIT_AUTHOR_NAME": "lane", "GIT_AUTHOR_EMAIL": "lane@example.invalid",
               "GIT_COMMITTER_NAME": "lane", "GIT_COMMITTER_EMAIL": "lane@example.invalid"}
        subprocess.run(["git", "init", "-q"], cwd=root, check=True, env=env)
        subprocess.run(["git", "add", "-A"], cwd=root, check=True, env=env)
        subprocess.run(["git", "commit", "-q", "-m", "ledger"], cwd=root, check=True, env=env)
        if ref:
            subprocess.run(["git", "update-ref", ref, "HEAD"], cwd=root, check=True, env=env)

    def test_a_missing_ledger_ref_is_unreachable_and_claims_no_authenticity(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            alpha = self._peer(base / "alpha", "Alpha")
            beta = self._peer(base / "beta", "Beta")
            self._commit(Path(alpha["root"]), None)
            self._commit(Path(beta["root"]), None)
            report = run_live([alpha, beta], fetch=False)
        self.assertEqual(report["hop_count"], 2)
        self.assertTrue(all(hop["status"] == "UNREACHABLE" for hop in report["hops"]))
        self.assertFalse(report["authenticity_claimed"])
        self.assertTrue(all(hop["authenticity_claimed"] is False for hop in report["hops"]))
        for hop in report["hops"]:
            _assert_six(self, hop)
        text = render_markdown(report)
        self.assertIsNone(_GRANT.search(text))
        self.assertIn("UNREACHABLE", text)

    def test_read_back_receipts_pass_and_a_partial_ledger_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            alpha = self._peer(base / "alpha", "Alpha")
            beta = self._peer(base / "beta", "Beta")
            self._write_both(Path(alpha["root"]), Path(beta["root"]))
            self._commit(Path(alpha["root"]), LEDGER_REF)
            self._commit(Path(beta["root"]), LEDGER_REF)
            report = run_live([alpha, beta], fetch=False, writer_introduction=_WRITER_BEFORE_EVERY_RECEIPT)
            self.assertEqual(report["counts"]["PASS"], 2, [hop["findings"] for hop in report["hops"]])
            self.assertTrue(report["authenticity_claimed"])
            self.assertTrue(all(hop["authenticity_claimed"] for hop in report["hops"]))
            # Drop Beta's ref. Hops that need Beta degrade; nothing is appended.
            subprocess.run(["git", "update-ref", "-d", LEDGER_REF], cwd=beta["root"], check=True)
            degraded = run_live([alpha, beta], fetch=False, writer_introduction=_WRITER_BEFORE_EVERY_RECEIPT)
            self.assertTrue(all(hop["status"] == "UNREACHABLE" for hop in degraded["hops"]))
            self.assertFalse(degraded["authenticity_claimed"])

    def test_a_read_pair_still_passes_when_another_organization_cannot_be_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            alpha = self._peer(base / "alpha", "Alpha")
            beta = self._peer(base / "beta", "Beta")
            self._write_both(Path(alpha["root"]), Path(beta["root"]))
            self._commit(Path(alpha["root"]), LEDGER_REF)
            self._commit(Path(beta["root"]), LEDGER_REF)
            unread, silent = discover_peers_from_github(
                ["SV-011"], read_file=lambda repository, path: ("HTTP_404", None))
            self.assertEqual(silent, [])
            report = run_live([alpha, beta, unread[0]], fetch=True, writer_introduction=_WRITER_BEFORE_EVERY_RECEIPT)
        by_pair = {(hop["sender_slug"], hop["destination_slug"]): hop for hop in report["hops"]}
        self.assertEqual(by_pair[("alpha", "beta")]["status"], "PASS", by_pair[("alpha", "beta")]["findings"])
        self.assertEqual(by_pair[("beta", "alpha")]["status"], "PASS")
        self.assertTrue(by_pair[("alpha", "beta")]["authenticity_claimed"])
        self.assertEqual(by_pair[("alpha", "sv-011")]["status"], "UNREACHABLE")
        self.assertFalse(by_pair[("sv-011", "beta")]["authenticity_claimed"])
        self.assertEqual(report["counts"], {"PASS": 2, "FAIL": 0, "UNREACHABLE": 4, lane.DURABLE_QUEUE: 0})
        self.assertTrue(report["authenticity_claimed"])
        self.assertIn("sv-011", report["matrix"]["alpha"])

    def _write_both(self, alpha: Path, beta: Path) -> None:
        forward_e, forward_c, forward_i = _pair_receipts(
            "Alpha", "Beta", "beta.intr-destination", "live-alpha-beta", "pkt-ab")
        back_e, back_c, back_i = _pair_receipts(
            "Beta", "Alpha", "alpha.intr-destination", "live-beta-alpha", "pkt-ba")
        self._write_org(alpha, "Alpha", [forward_e, forward_c, back_i])
        self._write_org(beta, "Beta", [back_e, back_c, forward_i])

    def _write_org(self, root: Path, organization: str, repo_receipts: list[dict]) -> None:
        linked = []
        previous = None
        for receipt in repo_receipts:
            body = {key: value for key, value in receipt.items() if key != "receipt_sha256"}
            body["previous_receipt_sha256"] = previous
            stamped = {**body, "receipt_sha256": sha256(body)}
            linked.append(stamped)
            previous = stamped["receipt_sha256"]
        org_linked = []
        previous = None
        for receipt in linked:
            org = _org(previous, receipt)
            org_linked.append(org)
            previous = org["receipt_sha256"]
        namespace = root / "repository-ledger" / organization / ".github"
        _store(root, org_linked, linked)
        _store(namespace, linked, [])


@unittest.skipUnless(os.environ.get("INTR_HOP_ORG_ROOTS"),
                     "fabricated crossings need organization checkouts in INTR_HOP_ORG_ROOTS")
class FabricatedCheckoutTests(unittest.TestCase):
    def test_every_ordered_pair_among_advertised_peers_passes(self):
        roots = [Path(item) for item in os.environ["INTR_HOP_ORG_ROOTS"].split(os.pathsep) if item]
        peers = discover_peers(roots)
        slugs = {peer["slug"] for peer in peers}
        self.assertTrue({"admissible-existence", "stegverse-labs", "stegverse-org", "sv-llm"} <= slugs)
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            report = run_fabricated(peers, mesh_root=work / "mesh", ledger_home=work / "ledgers")
        self.assertEqual(report["counts"]["FAIL"], 0, [hop for hop in report["hops"] if hop["status"] != "PASS"])
        self.assertEqual(report["counts"]["PASS"], len(peers) * (len(peers) - 1))
        self.assertEqual(report["evidence_class"], "FABRICATED_NON_AUTHENTIC")
        self.assertFalse(report["far_side_authentic"])
        self.assertFalse(report["authenticity_claimed"])
        self.assertFalse(report["federation_json_is_a_peer_source"])
        self.assertFalse(report["execution_runtime"]["peer_ledger_writer_used"])
        self.assertFalse(report["routing_in_scope"])
        self.assertFalse(report["governance_in_scope"])
        self.assertIsNone(_GRANT.search(render_markdown(report)))
        self.assertIsNone(_GRANT.search(json.dumps(report)))


def _advertised_documents(organization: str, *, bind: bool = True):
    slug = organization_slug(organization)
    service = slug + "." + PROFILE_ID
    overlay = {"ingress": {"capability_endpoint_bindings": [] if not bind else [{
        "profile_id": PROFILE_ID,
        "receiving_operation": {
            "addressed_service": service,
            "operation_id": "ORGANIZATION_INTR_DESTINATION_INGRESS",
        },
    }]}}
    registry = {"organization": organization, "services": [] if not bind else [{
        "service_id": service,
        "repository": organization + "/.github",
        "capability_profile_id": PROFILE_ID,
    }]}
    return overlay, registry


class GithubAdvertisementTests(unittest.TestCase):
    def test_the_candidate_set_is_the_eight_organizations(self):
        self.assertEqual(CANDIDATE_ORGANIZATIONS, (
            "StegVerse-org", "StegVerse-Labs", "SV-LLM", "SV-011",
            "GCAT-BCAT-Engine", "Admissible-Existence", "StegVerse-002", "StegGhost",
        ))

    def test_a_public_read_sends_no_token_and_a_set_token_is_only_a_bearer_header(self):
        seen = []

        class Response:
            status_code = 404
            content = b""

        def getter(url, headers=None, timeout=30):
            seen.append((url, dict(headers or {})))
            return Response()

        status, document = github_read_file("SV-011/.github", OVERLAY_RELATIVE, token=None, getter=getter)
        self.assertEqual(status, "HTTP_404")
        self.assertIsNone(document)
        self.assertNotIn("Authorization", seen[0][1])
        self.assertNotIn("token", seen[0][0])
        github_read_file("SV-011/.github", OVERLAY_RELATIVE, token="  ", getter=getter)
        self.assertNotIn("Authorization", seen[1][1])
        github_read_file("SV-011/.github", OVERLAY_RELATIVE, token="hop-lane-token-value", getter=getter)
        self.assertEqual(seen[2][1]["Authorization"], "Bearer hop-lane-token-value")
        self.assertNotIn("hop-lane-token-value", seen[2][0])
        self.assertEqual(seen[2][1]["Accept"], "application/vnd.github.raw")

    def test_an_unreadable_organization_stays_in_the_peer_set(self):
        files = {}
        for organization, bind in (("Alpha", True), ("Beta", True), ("Silent", False)):
            overlay, registry = _advertised_documents(organization, bind=bind)
            repository = organization + "/.github"
            files[(repository, OVERLAY_RELATIVE)] = ("ok", overlay)
            files[(repository, REGISTRY_RELATIVE)] = ("ok", registry)
            files[(repository, CONTRACT_RELATIVE)] = ("HTTP_404", None)
        for path in (OVERLAY_RELATIVE, REGISTRY_RELATIVE, CONTRACT_RELATIVE):
            files[("SV-011/.github", path)] = ("HTTP_404", None)
        requested = []

        def read(repository, path):
            requested.append((repository, path))
            return files[(repository, path)]

        peers, silent = discover_peers_from_github(["Alpha", "Silent", "SV-011", "Beta"], read_file=read)
        self.assertEqual([peer["slug"] for peer in peers], ["alpha", "beta", "sv-011"])
        self.assertEqual(silent, [{"organization": "Silent", "repository": "Silent/.github"}])
        unread = next(peer for peer in peers if peer["slug"] == "sv-011")
        self.assertFalse(unread["advertisement_readable"])
        self.assertEqual(unread["unreadable_reason"], "ADVERTISEMENT_NOT_READABLE_HTTP_404")
        self.assertTrue(all("federation.json" not in path for _, path in requested))
        self.assertIn(("SV-011/.github", OVERLAY_RELATIVE), requested)
        report = run_live(peers, fetch=False)
        self.assertEqual(report["hop_count"], 6)
        self.assertEqual(set(report["matrix"]), {"alpha", "beta", "sv-011"})
        involving = [hop for hop in report["hops"] if "sv-011" in (hop["sender_slug"], hop["destination_slug"])]
        self.assertEqual(len(involving), 4)
        for hop in involving:
            self.assertEqual(hop["status"], "UNREACHABLE")
            self.assertFalse(hop["authenticity_claimed"])
            if hop["sender_slug"] == "sv-011":
                self.assertEqual(hop["unreachable"]["sender"], "ADVERTISEMENT_NOT_READABLE_HTTP_404")
            if hop["destination_slug"] == "sv-011":
                self.assertEqual(hop["unreachable"]["destination"], "ADVERTISEMENT_NOT_READABLE_HTTP_404")
                self.assertEqual(hop["resolution_source"], "ADVERTISEMENT_NOT_READABLE")
        text = render_markdown(report)
        self.assertIn("kept in the peer set", text)
        self.assertNotIn("not peers", text)
        self.assertIsNone(_GRANT.search(text))

    def test_live_does_not_fetch_a_ledger_for_an_unread_advertisement(self):
        peers, _silent = discover_peers_from_github(
            ["SV-011", "StegGhost"],
            read_file=lambda repository, path: ("HTTP_403", None))

        def boom(*_args, **_kwargs):
            raise AssertionError("remote ledger fetch ran for an unread advertisement")

        original = lane.materialize_remote_ledger
        lane.materialize_remote_ledger = boom
        try:
            report = run_live(peers, fetch=True)
        finally:
            lane.materialize_remote_ledger = original
        self.assertEqual(report["counts"]["UNREACHABLE"], 2)
        self.assertEqual(report["counts"]["FAIL"], 0)
        self.assertFalse(report["authenticity_claimed"])

    def test_live_cli_queries_every_candidate_and_does_not_record_the_token(self):
        token = "hop-lane-token-value"
        captured = {}

        def fake_discover(organizations, *, token=None, read_file=None):
            captured["organizations"] = tuple(organizations)
            captured["token"] = token
            return [lane._unreachable_peer(organization, "ADVERTISEMENT_NOT_READABLE_HTTP_404")
                    for organization in organizations], []

        original = lane.discover_peers_from_github
        previous = os.environ.get(FEDERATION_READ_TOKEN_ENV)
        lane.discover_peers_from_github = fake_discover
        os.environ[FEDERATION_READ_TOKEN_ENV] = token
        try:
            with tempfile.TemporaryDirectory() as tmp:
                code = main(["--mode", "live", "--fetch-ledger-refs", "--out-dir", tmp])
                report = json.loads((Path(tmp) / "intr-destination-hop-lane.json").read_text(encoding="utf-8"))
                text = (Path(tmp) / "intr-destination-hop-lane.md").read_text(encoding="utf-8")
        finally:
            lane.discover_peers_from_github = original
            if previous is None:
                os.environ.pop(FEDERATION_READ_TOKEN_ENV, None)
            else:
                os.environ[FEDERATION_READ_TOKEN_ENV] = previous
        self.assertEqual(code, 0)
        self.assertEqual(captured["organizations"], CANDIDATE_ORGANIZATIONS)
        self.assertEqual(captured["token"], token)
        self.assertEqual({peer["organization"] for peer in report["peers"]}, set(CANDIDATE_ORGANIZATIONS))
        self.assertTrue(all(peer["advertisement_readable"] is False for peer in report["peers"]))
        self.assertEqual(report["hop_count"], len(CANDIDATE_ORGANIZATIONS) * (len(CANDIDATE_ORGANIZATIONS) - 1))
        self.assertTrue(all(hop["status"] == "UNREACHABLE" for hop in report["hops"]))
        self.assertFalse(report["authenticity_claimed"])
        self.assertEqual(report["peer_source"], "GITHUB_API_ORG_DOTGITHUB_ADVERTISEMENT")
        self.assertFalse(report["federation_json_is_a_peer_source"])
        self.assertNotIn(token, json.dumps(report))
        self.assertNotIn(token, text)
        self.assertIn(FEDERATION_READ_TOKEN_ENV, text)
        self.assertIsNone(_GRANT.search(text))
        self.assertIsNone(_GRANT.search(json.dumps(report)))


class LedgerIntegrityClassificationTests(unittest.TestCase):
    """Fabricated receipts on temporary ledgers. None of them is authentic."""

    def _views(self, repo_chain, org_chain, *, repo_times=None, org_times=None, sources=None):
        repo = {"present": True, "chain": repo_chain, "findings": [], "sources": {},
                "introduced_at": repo_times or {}}
        org = {"present": True, "chain": org_chain, "findings": [],
               "sources": sources if sources is not None else {
                   item["source_transition_sha256"]: next(s for s in repo_chain if s["receipt_sha256"] == item["repo_receipt_sha256"])
                   for item in org_chain if item.get("source_transition_sha256")},
               "introduced_at": org_times or {}}
        return repo, org

    def test_findings_on_receipts_before_the_writer_are_legacy_and_reported(self):
        emitted, closed, _ = _pair_receipts("Alpha", "Beta", "beta.intr-destination", "cid-1", "pkt-1")
        clocked = json.loads(json.dumps(emitted))
        clocked["hb_reference"]["derived_from_clock"] = True
        clocked = _repo(None, clocked["transition_id"], EMITTED_CLASS, clocked["evidence"], "Alpha/.github")
        body = {key: value for key, value in clocked.items() if key != "receipt_sha256"}
        body["hb_reference"] = {**body["hb_reference"], "derived_from_clock": True}
        clocked = {**body, "receipt_sha256": sha256(body)}
        linked = _org(None, clocked)
        orphan_source = _repo(None, "ORGANIZATION_LEDGER_OPENED:x", "ORGANIZATION_LEDGER_OPENED", {}, "Alpha/.github")
        orphan = _org(linked["receipt_sha256"], orphan_source)
        repo, org = self._views([clocked], [linked, orphan],
                                repo_times={clocked["receipt_sha256"]: 100},
                                org_times={linked["receipt_sha256"]: 100, orphan["receipt_sha256"]: 100},
                                sources={linked["source_transition_sha256"]: clocked})
        strict = lane.integrity_report(repo, org)
        self.assertIn("TIME_CONSTRAINT_DERIVED_FROM_CLOCK", strict["findings"])
        self.assertIn("ORPHAN_ORGANIZATION_RECEIPT", strict["findings"])
        self.assertEqual(strict["legacy_receipt_count"], 0)
        writer = {"commit": "c0ffee", "committed_at_unix": 200, "source": "TEST"}
        classified = lane.integrity_report(repo, org, writer_introduction=writer)
        self.assertEqual(classified["findings"], [])
        reported = {item["finding"]: item for item in classified["reported"]}
        self.assertEqual(reported["TIME_CONSTRAINT_DERIVED_FROM_CLOCK"]["classification"], "LEGACY")
        self.assertEqual(reported["ORPHAN_ORGANIZATION_RECEIPT"]["classification"], "LEGACY")
        self.assertEqual(classified["legacy_receipt_count"], 3)
        # A receipt the writer itself appended is not legacy: it still fails.
        later = lane.integrity_report(repo, org, writer_introduction={**writer, "committed_at_unix": 50})
        self.assertIn("TIME_CONSTRAINT_DERIVED_FROM_CLOCK", later["findings"])
        self.assertEqual(lane.integrity_findings(repo, org, writer_introduction=writer), [])

    def test_identical_duplicates_are_reported_and_divergent_ones_fail(self):
        first = _repo(None, "ORGANIZATION_INGRESS_MATERIALIZED:node", "ORGANIZATION_INGRESS_MATERIALIZED",
                      {"node": "n"}, "Alpha/.github")
        again = _repo(first["receipt_sha256"], first["transition_id"], first["transition_class"],
                      {"node": "n"}, "Alpha/.github")
        org = [_org(None, first)]
        org.append(_org(org[0]["receipt_sha256"], again))
        repo_view, org_view = self._views([first, again], org)
        report = lane.integrity_report(repo_view, org_view)
        self.assertEqual(report["findings"], [])
        identical, = [item for item in report["reported"] if item["finding"] == "IDENTICAL_DUPLICATE_REPOSITORY_RECEIPT"]
        self.assertEqual(identical["transition_id"], first["transition_id"])
        self.assertEqual(len(identical["receipt_sha256"]), 2)
        divergent = _repo(first["receipt_sha256"], first["transition_id"], first["transition_class"],
                          {"node": "other"}, "Alpha/.github")
        org2 = [_org(None, first)]
        org2.append(_org(org2[0]["receipt_sha256"], divergent))
        repo_view, org_view = self._views([first, divergent], org2)
        self.assertIn("DUPLICATE_REPOSITORY_RECEIPT", lane.integrity_findings(repo_view, org_view))
        times = {first["receipt_sha256"]: 10, divergent["receipt_sha256"]: 10}
        repo_view, org_view = self._views([first, divergent], org2, repo_times=times)
        legacy = lane.integrity_report(repo_view, org_view,
                                       writer_introduction={"committed_at_unix": 20})
        self.assertEqual(legacy["findings"], [])
        self.assertEqual([item["classification"] for item in legacy["reported"]
                          if item["finding"] == "DUPLICATE_REPOSITORY_RECEIPT"], ["LEGACY"])

    def test_an_organization_receipt_that_names_no_source_is_reported_not_compared(self):
        _emitted, _closed, arrived = _pair_receipts("Alpha", "Beta", "beta.intr-destination", "cid-1", "pkt-1")
        org = _org(None, arrived)
        body = {key: value for key, value in org.items() if key != "receipt_sha256"}
        body["source_transition_sha256"] = None
        org = {**body, "receipt_sha256": sha256(body)}
        repo_view, org_view = self._views([arrived], [org], sources={})
        report = lane.integrity_report(repo_view, org_view)
        self.assertEqual(report["findings"], [])
        self.assertEqual([item["finding"] for item in report["reported"]],
                         ["ORGANIZATION_RECEIPT_NAMES_NO_SOURCE_RECEIPT"])

    def test_receipt_introduction_times_come_from_the_ledger_ref_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env = {**os.environ, "GIT_AUTHOR_NAME": "lane", "GIT_AUTHOR_EMAIL": "lane@example.invalid",
                   "GIT_COMMITTER_NAME": "lane", "GIT_COMMITTER_EMAIL": "lane@example.invalid"}
            subprocess.run(["git", "init", "-q"], cwd=root, check=True, env=env)
            emitted, closed, _ = _pair_receipts("Alpha", "Beta", "beta.intr-destination", "cid-1", "pkt-1")
            org0 = _org(None, emitted)
            _store(root, [org0], [emitted])
            _store(root / "repository-ledger" / "Alpha" / ".github", [emitted], [])
            subprocess.run(["git", "add", "-A"], cwd=root, check=True, env=env)
            subprocess.run(["git", "commit", "-q", "-m", "one"], cwd=root, check=True,
                           env={**env, "GIT_COMMITTER_DATE": "1000000000 +0000", "GIT_AUTHOR_DATE": "1000000000 +0000"})
            org1 = _org(org0["receipt_sha256"], closed)
            _store(root, [org0, org1], [emitted, closed])
            _store(root / "repository-ledger" / "Alpha" / ".github", [emitted, closed], [])
            subprocess.run(["git", "add", "-A"], cwd=root, check=True, env=env)
            subprocess.run(["git", "commit", "-q", "-m", "two"], cwd=root, check=True,
                           env={**env, "GIT_COMMITTER_DATE": "1000000500 +0000", "GIT_AUTHOR_DATE": "1000000500 +0000"})
            subprocess.run(["git", "update-ref", LEDGER_REF, "HEAD"], cwd=root, check=True)
            org = lane.walk_git(root, LEDGER_REF)
            repo = lane.walk_git(root, LEDGER_REF, "repository-ledger/Alpha/.github")
        self.assertEqual(org["introduced_at"][org0["receipt_sha256"]], 1000000000)
        self.assertEqual(org["introduced_at"][org1["receipt_sha256"]], 1000000500)
        self.assertEqual(repo["introduced_at"][emitted["receipt_sha256"]], 1000000000)
        self.assertEqual(repo["introduced_at"][closed["receipt_sha256"]], 1000000500)
        report = lane.integrity_report(repo, org, writer_introduction={"committed_at_unix": 1000000100})
        self.assertEqual(report["legacy_receipt_count"], 2)

    def test_the_writer_marker_and_its_introduction(self):
        self.assertTrue(lane.writer_marker("    inputs:\n      hb_epoch:\n        required: true\nrun: x --self-close\n"))
        self.assertFalse(lane.writer_marker("run: x --self-close\n"))
        self.assertFalse(lane.writer_marker("      hb_epoch:\n"))
        listed = [
            {"sha": "new", "commit": {"committer": {"date": "2026-10-17T10:00:00Z"}}},
            {"sha": "mid", "commit": {"committer": {"date": "2026-10-16T10:00:00Z"}}},
            {"sha": "old", "commit": {"committer": {"date": "2026-10-15T10:00:00Z"}}},
        ]
        files = {"old": "run: --self-close\n", "mid": "      hb_epoch:\nrun: --self-close\n",
                 "new": "      hb_epoch:\nrun: --self-close\n"}
        seen = []

        class Response:
            def __init__(self, status, content):
                self.status_code, self.content = status, content

        def getter(url, headers=None, timeout=30):
            seen.append((url, dict(headers or {})))
            if "/commits?" in url:
                return Response(200, json.dumps(listed if "page=1" in url else []).encode())
            sha = url.rsplit("ref=", 1)[1]
            return Response(200, files[sha].encode())

        found = lane.writer_introduction_from_github("Alpha/.github", token="t-value", getter=getter)
        self.assertEqual(found["commit"], "mid")
        self.assertEqual(found["committed_at_unix"], 1792144800)
        self.assertTrue(all("t-value" not in url for url, _ in seen))
        self.assertTrue(all(headers["Authorization"] == "Bearer t-value" for _, headers in seen))
        overrides = lane.parse_writer_overrides(["Alpha=1792144800", "Beta=2026-10-16T10:00:00Z"])
        self.assertEqual(overrides["Alpha"]["committed_at_unix"], overrides["Beta"]["committed_at_unix"])
        with self.assertRaises(ValueError):
            lane.parse_writer_overrides(["Alpha"])

    def test_the_remote_ledger_header_is_basic_and_the_history_is_full(self):
        header = lane.git_auth_header("t-value")
        self.assertTrue(header.startswith("Authorization: Basic "))
        import base64
        self.assertEqual(base64.b64decode(header.split()[-1]).decode(), "x-access-token:t-value")
        source = Path(lane.__file__).read_text(encoding="utf-8")
        fetch = source.split("def materialize_remote_ledger(")[1].split("\ndef ")[0]
        self.assertNotIn("--depth", fetch)


class OrchestrationTests(unittest.TestCase):
    """No workflow is dispatched here. The dispatcher and the ledger probe are fakes."""

    def _peers(self, count=8):
        names = ["StegVerse-org", "StegVerse-Labs", "SV-LLM", "SV-011", "GCAT-BCAT-Engine",
                 "Admissible-Existence", "StegVerse-002", "StegGhost"][:count]
        return [{"organization": name, "slug": organization_slug(name),
                 "address": organization_slug(name) + "." + PROFILE_ID,
                 "repository": name + "/.github"} for name in names]

    def test_waves_cover_every_ordered_pair_once_with_disjoint_organizations(self):
        peers = self._peers()
        waves = lane.hop_waves(peers)
        self.assertEqual(len(waves), 14)
        pairs = []
        for wave in waves:
            self.assertEqual(len(wave), 4)
            members = [peer["slug"] for hop in wave for peer in hop]
            self.assertEqual(len(members), len(set(members)))
            pairs.extend((sender["slug"], dest["slug"]) for sender, dest in wave)
        expected = {(s["slug"], d["slug"]) for s, d in ordered_pairs(peers)}
        self.assertEqual(len(pairs), 56)
        self.assertEqual(set(pairs), expected)
        odd = lane.hop_waves(self._peers(5))
        self.assertEqual(sum(len(wave) for wave in odd), 20)
        for wave in odd:
            members = [peer["slug"] for hop in wave for peer in hop]
            self.assertEqual(len(members), len(set(members)))

    def test_orchestration_dispatches_once_per_organization_and_never_waits(self):
        peers = self._peers()
        dispatched = []

        def dispatcher(sender, dest, *, communication_id, hb_epoch):
            dispatched.append((sender["slug"], dest["slug"], communication_id, hb_epoch))
            return True, "DISPATCHED"

        result = lane.run_orchestrate(peers, hb_epoch=1000, token="t-value", dispatcher=dispatcher)
        # One transition: four disjoint hops are sent; the rest wait for a later transition.
        self.assertEqual(len(dispatched), 4)
        members = [slug for hop in dispatched for slug in hop[:2]]
        self.assertEqual(len(members), len(set(members)))
        self.assertEqual(result["dispatched"], 4)
        self.assertEqual(result["outcomes"], {lane.DURABLE_QUEUE: 4,
                                              "DEFERRED_ORGANIZATION_LEDGER_CONCURRENCY": 52})
        self.assertEqual(len(result["hops"]), 56)
        first = dispatched[0]
        self.assertEqual(first[2], "intr-hop:%s:%s:1000" % (first[0], first[1]))
        self.assertTrue(all(hop[3] == 1000 for hop in dispatched))
        for hop in result["hops"]:
            if hop["outcome"] == lane.DURABLE_QUEUE:
                self.assertIs(hop["always_on_receiver_required"], False)
                self.assertEqual(hop["failure_code"], lane.DURABLE_QUEUE)
                self.assertEqual(hop["send_transition_disposition"], "ALLOW")
            _assert_six(self, hop)
        self.assertIs(result["receiver_wait"], False)
        self.assertIs(result["always_on_receiver_required"], False)
        self.assertNotIn("t-value", json.dumps(result))
        self.assertEqual(result["time_constraint"], "SUPPLIED_HB_EPOCH")

    def test_ledger_state_directs_the_next_transition(self):
        peers = self._peers(4)
        slugs = [peer["slug"] for peer in peers]
        a, b, c, d = slugs
        states = {(a, b): "CLOSED", (b, a): "REFUSED", (c, d): "OPEN"}
        sent = []
        result = lane.run_orchestrate(
            peers, hb_epoch=40, token="t-value", ledger_state=states,
            dispatcher=lambda s, t, **kw: (sent.append((s["slug"], t["slug"])) or True, "DISPATCHED"))
        by_pair = {(hop["sender_slug"], hop["destination_slug"]): hop for hop in result["hops"]}
        self.assertEqual(by_pair[(a, b)]["outcome"], "CLOSED_IN_READ_LEDGERS")
        self.assertEqual(by_pair[(b, a)]["outcome"], "CLOSURE_REFUSED")
        _assert_six(self, by_pair[(b, a)])
        self.assertEqual(by_pair[(c, d)]["outcome"], lane.DURABLE_QUEUE)
        self.assertIs(by_pair[(c, d)]["always_on_receiver_required"], False)
        _assert_six(self, by_pair[(c, d)])
        # c and d hold an open hop: nothing touching them is sent; a and b are free.
        # a -> b is closed and b -> a refused, so nothing is left to send this transition.
        self.assertEqual(sent, [])
        self.assertEqual(result["outcomes"]["DEFERRED_ORGANIZATION_LEDGER_CONCURRENCY"], 9)
        # Once c -> d closes, the next transition sends from ledger state.
        states[(c, d)] = "CLOSED"
        lane.run_orchestrate(
            peers, hb_epoch=41, token="t-value", ledger_state=states,
            dispatcher=lambda s, t, **kw: (sent.append((s["slug"], t["slug"])) or True, "DISPATCHED"))
        self.assertEqual(len(sent), 2)
        members = [slug for pair in sent for slug in pair]
        self.assertEqual(len(members), len(set(members)))
        self.assertTrue(all(pair not in states for pair in sent))

    def test_unreachable_and_failed_dispatch_carry_the_six_fields(self):
        peers = self._peers(3)
        peers[2]["advertisement_readable"] = False

        def dispatcher(sender, dest, *, communication_id, hb_epoch):
            return False, "DISPATCH_HTTP_404"

        result = lane.run_orchestrate(peers, hb_epoch=40, token="t-value", dispatcher=dispatcher)
        outcomes = {hop["outcome"] for hop in result["hops"]}
        self.assertEqual(outcomes, {"NOT_DISPATCHED", "UNREACHABLE"})
        self.assertEqual(len(result["hops"]), 6)
        for hop in result["hops"]:
            _assert_six(self, hop)
        failed = [hop for hop in result["hops"] if hop["outcome"] == "NOT_DISPATCHED"]
        self.assertTrue(all(hop["failure_code"] == "INTR_HOP_SEND_DISPATCH_DISPATCH_HTTP_404" for hop in failed))
        self.assertNotIn("TIMEOUT", json.dumps(result))
        absent = lane.run_orchestrate(peers, hb_epoch=40, token=" ", dispatcher=dispatcher)
        self.assertEqual(absent["disposition"], "FAIL_CLOSED")
        self.assertEqual(absent["failure_code"], "HOP_DISPATCH_CREDENTIAL_ABSENT")
        self.assertEqual(absent["dispatched"], 0)
        _assert_six(self, absent)
        refused = lane.run_orchestrate(peers, hb_epoch=-1, token="t-value", dispatcher=dispatcher)
        self.assertEqual(refused["disposition"], "FAIL_CLOSED")
        _assert_six(self, refused)

    def test_pair_ledger_state_reads_the_sender_chain(self):
        emitted, closed, _ = _pair_receipts("Alpha", "Beta", "beta.intr-destination", "cid-1", "pkt-1")
        self.assertEqual(lane.pair_ledger_state([], "Beta", "beta.intr-destination"), "UNSENT")
        self.assertEqual(lane.pair_ledger_state([emitted], "Beta", "beta.intr-destination"), "OPEN")
        self.assertEqual(lane.pair_ledger_state([emitted, closed], "Beta", "beta.intr-destination"), "CLOSED")
        refused = dict(closed, transition_class=lane.CLOSURE_REFUSED_CLASS)
        self.assertEqual(lane.pair_ledger_state([emitted, refused], "Beta", "beta.intr-destination"), "REFUSED")
        self.assertEqual(lane.pair_ledger_state([emitted], "Gamma", "gamma.intr-destination"), "UNSENT")

    def test_the_lane_source_and_workflow_carry_no_receiver_wait(self):
        source = Path(lane.__file__).read_text(encoding="utf-8")
        for waiting in ("time.sleep", "sleep(", "monotonic", "wave_timeout", "poll_seconds", '"TIMEOUT"'):
            self.assertNotIn(waiting, source)
        workflows = Path(__file__).resolve().parents[1] / ".github/workflows"
        workflow = "\n".join((workflows / name).read_text(encoding="utf-8") for name in (
            "intr-destination-hop-lane.yml", "intr-destination-hop-lane-live.yml",
            "intr-destination-hop-lane-orchestrate.yml"))
        self.assertNotIn("wave_timeout", workflow)
        self.assertNotIn("timeout-minutes: 350", workflow)
        self.assertNotIn("classic PAT", workflow)
        for line in workflow.splitlines():
            if '"disposition":"FAIL_CLOSED"' in line:
                for field in _SIX:
                    self.assertIn('"%s"' % field, line)

    def _no_dispatch(self):
        calls = []

        def dispatcher(sender, dest, **kw):
            calls.append((sender["slug"], dest["slug"], kw))
            return True, "DISPATCHED"

        return calls, dispatcher

    def _assert_hb_epoch_fail_closed(self, result, finding):
        self.assertEqual(result["disposition"], "FAIL_CLOSED")
        self.assertEqual(result["failure_code"],
                         "HB_EPOCH_NOT_SUPPLIED" if finding == "MISSING" else "HB_EPOCH_INVALID")
        self.assertEqual(result["failed_predicate"], "SUBMISSION_CARRIES_THE_SUPPLIED_HB_EPOCH")
        self.assertIs(result["derived_from_clock"], False)
        self.assertEqual(result["retry_entrypoint"],
                         ".github/workflows/intr-destination-hop-lane-orchestrate.yml hb_epoch=<supplied>")
        self.assertEqual(result["hb_epoch_finding"], finding)
        self.assertEqual(result["dispatched"], 0)
        self.assertEqual(result["hops"], [])
        self.assertIs(result["consequence_committed"], False)
        _assert_six(self, result)

    def test_a_missing_hb_epoch_fails_closed_and_dispatches_nothing(self):
        peers = self._peers()
        calls, dispatcher = self._no_dispatch()
        result = lane.run_orchestrate(peers, hb_epoch=None, token="t-value", dispatcher=dispatcher)
        self._assert_hb_epoch_fail_closed(result, "MISSING")
        self.assertEqual(calls, [])
        # A blank string is supplied but not ASCII [0-9]+ under the shared rule.
        for blank in ("", "   "):
            calls, dispatcher = self._no_dispatch()
            result = lane.run_orchestrate(peers, hb_epoch=blank, token="t-value", dispatcher=dispatcher)
            self._assert_hb_epoch_fail_closed(result, "MALFORMED")
            self.assertEqual(calls, [])

    def test_a_malformed_hb_epoch_fails_closed_and_dispatches_nothing(self):
        peers = self._peers()
        for malformed in (-1, "-1", "+7", " 7", "7 ", "1.5", "1e3", "1_000", "0x10", "abc",
                          "\u0663", 7.0, True, False, [7]):
            calls, dispatcher = self._no_dispatch()
            result = lane.run_orchestrate(peers, hb_epoch=malformed, token="t-value", dispatcher=dispatcher)
            self._assert_hb_epoch_fail_closed(result, "MALFORMED")
            self.assertEqual(calls, [], repr(malformed))

    def test_hb_epoch_reaches_every_hop_dispatch_in_the_writer_format(self):
        # The org hop workflow and the organization-ledger writer (StegVerse-Labs/.github#3205)
        # take hb_epoch as a workflow_dispatch string of ASCII decimal digits.
        self.assertEqual(lane.parse_hb_epoch("40"), 40)
        self.assertIsNone(lane.parse_hb_epoch("0"))
        self.assertIsNone(lane.parse_hb_epoch("31"))
        self.assertEqual(lane.parse_hb_epoch("32"), 32)
        self.assertEqual(lane.parse_hb_epoch(40), 40)
        posted = []

        class Response:
            status_code = 204
            content = b""

        def poster(url, json=None, headers=None, timeout=30):
            posted.append(json)
            return Response()

        peers = self._peers()
        dispatcher = lambda s, t, **kw: lane.dispatch_send_hop(s, t, token="t-value", poster=poster, **kw)
        result = lane.run_orchestrate(peers, hb_epoch="40", token="t-value", dispatcher=dispatcher)
        self.assertEqual(result["dispatched"], 4)
        self.assertEqual(len(posted), 4)
        for body in posted:
            self.assertEqual(body["inputs"]["hb_epoch"], "40")
            self.assertRegex(body["inputs"]["hb_epoch"], r"^[0-9]+$")
            self.assertTrue(body["inputs"]["communication_id"].endswith(":40"))
        # A malformed epoch handed straight to the dispatcher is not posted.
        before = len(posted)
        for malformed in ("-1", "x", None, True, "0", "31", 31):
            ok, detail = lane.dispatch_send_hop(peers[0], peers[1], communication_id="c", hb_epoch=malformed,
                                                token="t-value", poster=poster)
            self.assertFalse(ok)
            self.assertEqual(detail, "HB_EPOCH_INVALID")
        self.assertEqual(len(posted), before)

    def test_orchestrate_cli_fails_closed_on_a_missing_or_malformed_hb_epoch_before_any_read(self):
        reads = []
        original = lane.discover_peers_from_github
        lane.discover_peers_from_github = lambda *a, **kw: reads.append(a) or ([], [])
        previous = {name: os.environ.pop(name, None) for name in (lane.FEDERATION_HOP_TOKEN_ENV, FEDERATION_READ_TOKEN_ENV)}
        os.environ[lane.FEDERATION_HOP_TOKEN_ENV] = "t-value"
        try:
            for argv, finding in (([], "MISSING"), (["--hb-epoch", ""], "MALFORMED"),
                                  (["--hb-epoch", "abc"], "MALFORMED"), (["--hb-epoch=-1"], "MALFORMED"),
                                  (["--hb-epoch", "1.5"], "MALFORMED"), (["--hb-epoch", "0"], "BELOW_HB32_ANCHOR"),
                                  (["--hb-epoch", "31"], "BELOW_HB32_ANCHOR")):
                with tempfile.TemporaryDirectory() as tmp:
                    code = main(["--mode", "orchestrate", "--out-dir", tmp] + argv)
                    self.assertEqual(code, 1)
                    report = json.loads((Path(tmp) / "intr-destination-hop-lane.json").read_text(encoding="utf-8"))
                    self._assert_hb_epoch_fail_closed(report["orchestration"], finding)
                    self.assertNotIn("t-value", json.dumps(report))
            self.assertEqual(reads, [])
        finally:
            lane.discover_peers_from_github = original
            for name, value in previous.items():
                if value is None:
                    os.environ.pop(name, None)
                else:
                    os.environ[name] = value

    def test_the_orchestrate_workflow_carries_hb_epoch_and_resolves_it_first(self):
        workflows = Path(__file__).resolve().parents[1] / ".github/workflows"
        workflow = (workflows / "intr-destination-hop-lane-orchestrate.yml").read_text(encoding="utf-8")
        # SDK#543: the pull-request lane has no `mode` input and no dispatch-only job.
        pr_lane = (workflows / "intr-destination-hop-lane.yml").read_text(encoding="utf-8")
        self.assertNotIn("inputs.mode", pr_lane)
        self.assertNotIn("\n  orchestrate:\n", pr_lane)
        self.assertNotIn("pull_request", workflow.split("\njobs:")[0])
        self.assertRegex(workflow, r"(?m)^      hb_epoch:\n(?:        .*\n)*?        type: string$")
        job = workflow[workflow.index("\n  orchestrate:\n"):]
        self.assertIn("HB_EPOCH: ${{ inputs.hb_epoch }}", job)
        guard = job.index("hb_epoch_fail_closed(supplied)")
        self.assertLess(guard, job.index("FEDERATION_HOP_TOKEN:-"))
        self.assertLess(guard, job.index("python -m stegverse.intr_destination_hop_lane"))
        self.assertIn('--hb-epoch "$HB_EPOCH"', job)
        self.assertNotIn("DISPATCH_HB_EPOCH_INVALID", workflow)
        # Run the workflow's own gate on the exact head: 0, 31, blank, abc refuse; 32 passes.
        root = Path(__file__).resolve().parents[1]
        for supplied, code in (("0", "HB_EPOCH_INVALID"), ("31", "HB_EPOCH_INVALID"), ("", "HB_EPOCH_NOT_SUPPLIED"),
                               ("abc", "HB_EPOCH_INVALID"), ("32", None)):
            done = subprocess.run([sys.executable, "-c", _workflow_epoch_gate(job)], cwd=root, capture_output=True,
                                  text=True, env={**os.environ, "HB_EPOCH": supplied, "PYTHONPATH": str(root)})
            if code is None:
                self.assertEqual(done.returncode, 0, done.stderr)
                self.assertEqual(done.stdout, "")
                continue
            self.assertEqual(done.returncode, 1, (supplied, done.stderr))
            echoed = json.loads(done.stdout)
            self.assertEqual(echoed["disposition"], "FAIL_CLOSED")
            self.assertEqual(echoed["failure_code"], code)
            self.assertEqual(echoed["failed_predicate"], "SUBMISSION_CARRIES_THE_SUPPLIED_HB_EPOCH")
            self.assertEqual(echoed["dispatched"], 0)
            _assert_six(self, echoed)

    def test_the_send_dispatch_names_the_hop_workflow_and_keeps_the_token_in_a_header(self):
        seen = {}

        class Response:
            status_code = 204
            content = b""

        def poster(url, json=None, headers=None, timeout=30):
            seen.update(url=url, json=json, headers=headers)
            return Response()

        peers = self._peers(2)
        ok, detail = lane.dispatch_send_hop(peers[0], peers[1], communication_id="intr-hop:a:b:40",
                                            hb_epoch=40, token="t-value", poster=poster)
        self.assertTrue(ok)
        self.assertEqual(detail, "DISPATCHED")
        self.assertEqual(seen["url"], "https://api.github.com/repos/StegVerse-org/.github/actions/workflows/"
                         "intr-destination-hop.yml/dispatches")
        self.assertEqual(seen["json"]["inputs"], {"phase": "send", "destination_slug": "stegverse-labs",
                                                  "communication_id": "intr-hop:a:b:40", "hb_epoch": "40",
                                                  "forward": "true"})
        self.assertEqual(seen["headers"]["Authorization"], "Bearer t-value")
        self.assertNotIn("t-value", seen["url"])

    def test_orchestrate_cli_requires_a_supplied_epoch_and_the_hop_token(self):
        previous = {name: os.environ.pop(name, None) for name in (lane.FEDERATION_HOP_TOKEN_ENV, FEDERATION_READ_TOKEN_ENV)}
        try:
            with tempfile.TemporaryDirectory() as tmp:
                os.environ[lane.FEDERATION_HOP_TOKEN_ENV] = "t-value"
                self.assertEqual(main(["--mode", "orchestrate", "--out-dir", tmp]), 1)
                os.environ.pop(lane.FEDERATION_HOP_TOKEN_ENV)
                self.assertEqual(main(["--mode", "orchestrate", "--hb-epoch", "40", "--out-dir", tmp]), 1)
                report = json.loads((Path(tmp) / "intr-destination-hop-lane.json").read_text(encoding="utf-8"))
                self.assertEqual(report["orchestration"]["failure_code"], "HOP_DISPATCH_CREDENTIAL_ABSENT")
                self.assertEqual(report["orchestration"]["dispatched"], 0)
                _assert_six(self, report["orchestration"])
        finally:
            for name, value in previous.items():
                if value is None:
                    os.environ.pop(name, None)
                else:
                    os.environ[name] = value

    def test_live_reads_fall_back_to_the_hop_token(self):
        captured = {}

        def fake_discover(organizations, *, token=None, read_file=None):
            captured["token"] = token
            return [lane._unreachable_peer(organization, "ADVERTISEMENT_NOT_READABLE_HTTP_404")
                    for organization in organizations], []

        original = lane.discover_peers_from_github
        previous = {name: os.environ.pop(name, None) for name in (lane.FEDERATION_HOP_TOKEN_ENV, FEDERATION_READ_TOKEN_ENV)}
        lane.discover_peers_from_github = fake_discover
        os.environ[lane.FEDERATION_HOP_TOKEN_ENV] = "hop-token-value"
        try:
            with tempfile.TemporaryDirectory() as tmp:
                main(["--mode", "live", "--out-dir", tmp, "--no-writer-lookup"])
                text = (Path(tmp) / "intr-destination-hop-lane.md").read_text(encoding="utf-8")
                report = (Path(tmp) / "intr-destination-hop-lane.json").read_text(encoding="utf-8")
        finally:
            lane.discover_peers_from_github = original
            for name, value in previous.items():
                if value is None:
                    os.environ.pop(name, None)
                else:
                    os.environ[name] = value
        self.assertEqual(captured["token"], "hop-token-value")
        self.assertNotIn("hop-token-value", text + report)
        self.assertIn(lane.FEDERATION_HOP_TOKEN_ENV, text)
        self.assertIsNone(_GRANT.search(text))


class HB32EpochFloorTests(unittest.TestCase):
    """Exact-head negatives for the HB32 floor under the shared supplied_epoch_failure rule.

    No workflow is dispatched and no ledger is read: the dispatcher is a fake
    that records calls, and the GitHub reads are replaced by a recorder.
    """

    # sha256 of `def supplied_epoch_failure ... return None` in org-kernel/kernel.py
    # (StegVerse-Labs/.github#3225 core head e6ba9601, StegVerse-org/.github#185).
    SHARED_RULE_SHA256 = "726248a585904b52cfe2eec1754e7ce582f67d6b501bd664bb7bee80bce9b7ef"

    def _peers(self):
        return OrchestrationTests._peers(self, 4)

    def _run(self, epoch):
        calls = []

        def dispatcher(sender, dest, **kw):
            calls.append((sender["slug"], dest["slug"], kw))
            return True, "DISPATCHED"

        return lane.run_orchestrate(self._peers(), hb_epoch=epoch, token="t-value", dispatcher=dispatcher), calls

    def _assert_refused(self, result, calls, code):
        self.assertEqual(result["disposition"], "FAIL_CLOSED")
        self.assertEqual(result["failure_code"], code)
        self.assertEqual(result["failed_predicate"], "SUBMISSION_CARRIES_THE_SUPPLIED_HB_EPOCH")
        self.assertIs(result["derived_from_clock"], False)
        self.assertIs(result["consequence_committed"], False)
        self.assertEqual(result["dispatched"], 0)
        self.assertEqual(result["hops"], [])
        self.assertIsNone(result["hb_epoch"])
        self.assertEqual(calls, [])
        _assert_six(self, result)
        self.assertNotIn("PENDING", json.dumps(result))

    def test_the_vendored_rule_is_the_shared_supplied_epoch_failure(self):
        source = Path(lane.__file__).read_text(encoding="utf-8")
        start = source.index("def supplied_epoch_failure")
        end = source.index("\ndef ", start + 5)
        self.assertEqual(hashlib.sha256(source[start:end].rstrip().encode()).hexdigest(), self.SHARED_RULE_SHA256)
        self.assertEqual(lane.HB_EPOCH_PREDICATE, "SUBMISSION_CARRIES_THE_SUPPLIED_HB_EPOCH")
        self.assertEqual(lane.HB32_ANCHOR, 32)

    def test_epochs_0_and_31_are_fail_closed_invalid_and_nothing_is_dispatched(self):
        for epoch in (0, 31, "0", "31", "00", "031"):
            result, calls = self._run(epoch)
            self._assert_refused(result, calls, "HB_EPOCH_INVALID")
            self.assertEqual(result["hb_epoch_finding"], "BELOW_HB32_ANCHOR", repr(epoch))
            self.assertIn("HB32", result["required_evidence_or_repair"])

    def test_epoch_32_is_accepted_and_carried_to_every_dispatch(self):
        for epoch in (32, "32", "0032"):
            result, calls = self._run(epoch)
            self.assertNotIn("disposition", result)
            self.assertEqual(result["hb_epoch"], 32)
            self.assertEqual(result["dispatched"], 2)
            self.assertEqual(len(calls), 2)
            self.assertTrue(all(kw["hb_epoch"] == 32 for _, _, kw in calls))
            self.assertTrue(all(kw["communication_id"].endswith(":32") for _, _, kw in calls))

    def test_a_missing_epoch_is_not_supplied_and_a_non_digit_string_is_invalid(self):
        result, calls = self._run(None)
        self._assert_refused(result, calls, "HB_EPOCH_NOT_SUPPLIED")
        self.assertEqual(result["hb_epoch_finding"], "MISSING")
        for epoch in ("abc", "3x", "+32", " 32", "32 ", "3_2", "32.0", "1e2", "\u0663\u0662", 32.0, True, [32]):
            result, calls = self._run(epoch)
            self._assert_refused(result, calls, "HB_EPOCH_INVALID")
            self.assertEqual(result["hb_epoch_finding"], "MALFORMED", repr(epoch))

    def test_a_clock_derived_reference_is_invalid(self):
        self.assertEqual(lane.supplied_epoch_failure(32, {"derived_from_clock": True})[0], "HB_EPOCH_INVALID")
        self.assertEqual(lane.supplied_epoch_failure(32, "not-an-object")[0], "HB_EPOCH_INVALID")
        self.assertIsNone(lane.supplied_epoch_failure(32, {"derived_from_clock": False}))
        self.assertIsNone(lane.supplied_epoch_failure("32"))

    def test_the_send_dispatch_refuses_below_32_and_posts_nothing(self):
        posted = []
        peers = self._peers()
        for epoch in (0, 31, "31"):
            ok, detail = lane.dispatch_send_hop(peers[0], peers[1], communication_id="c", hb_epoch=epoch,
                                                token="t-value", poster=lambda *a, **kw: posted.append(kw))
            self.assertFalse(ok)
            self.assertEqual(detail, "HB_EPOCH_INVALID")
        self.assertEqual(posted, [])

    def test_the_cli_writes_only_the_refusal_and_reads_nothing_for_0_and_31(self):
        reads = []
        original = lane.discover_peers_from_github
        lane.discover_peers_from_github = lambda *a, **kw: reads.append(a) or ([], [])
        previous = {name: os.environ.pop(name, None) for name in (lane.FEDERATION_HOP_TOKEN_ENV, FEDERATION_READ_TOKEN_ENV)}
        os.environ[lane.FEDERATION_HOP_TOKEN_ENV] = "t-value"
        try:
            for epoch in ("0", "31"):
                with tempfile.TemporaryDirectory() as tmp:
                    self.assertEqual(main(["--mode", "orchestrate", "--hb-epoch", epoch, "--out-dir", tmp]), 1)
                    written = sorted(path.name for path in Path(tmp).rglob("*"))
                    self.assertEqual(written, ["intr-destination-hop-lane.json"])
                    report = json.loads((Path(tmp) / "intr-destination-hop-lane.json").read_text(encoding="utf-8"))
                    self._assert_refused(report["orchestration"], [], "HB_EPOCH_INVALID")
            self.assertEqual(reads, [])
        finally:
            lane.discover_peers_from_github = original
            for name, value in previous.items():
                if value is None:
                    os.environ.pop(name, None)
                else:
                    os.environ[name] = value


class LaneInputRefusalTests(unittest.TestCase):
    def test_a_refused_lane_input_is_fail_closed_with_the_six_fields(self):
        original = lane.discover_peers_from_github

        def duplicate(*_args, **_kwargs):
            raise ValueError("two organizations resolve to the same intr-destination address: a.intr-destination")

        lane.discover_peers_from_github = duplicate
        try:
            for argv in (["--mode", "live"], ["--mode", "live", "--writer-introduced", "Alpha"]):
                with tempfile.TemporaryDirectory() as tmp:
                    self.assertEqual(main(argv + ["--out-dir", tmp]), 1)
                    report = json.loads((Path(tmp) / "intr-destination-hop-lane.json").read_text(encoding="utf-8"))
                refusal = report["refusal"]
                self.assertEqual(refusal["disposition"], "FAIL_CLOSED")
                self.assertEqual(refusal["failure_code"], "INTR_HOP_LANE_INPUT_REFUSED")
                self.assertEqual(refusal["dispatched"], 0)
                _assert_six(self, refusal)
        finally:
            lane.discover_peers_from_github = original


class LegacyOnlyCorrelationTests(unittest.TestCase):
    """LEGACY receipts are reported, never live-mesh evidence. All receipts are fabricated."""

    _peer = LiveLedgerTests._peer
    _commit = LiveLedgerTests._commit
    _write_both = LiveLedgerTests._write_both
    _write_org = LiveLedgerTests._write_org

    def _ledgers(self, base):
        alpha = self._peer(base / "alpha", "Alpha")
        beta = self._peer(base / "beta", "Beta")
        self._write_both(Path(alpha["root"]), Path(beta["root"]))
        self._commit(Path(alpha["root"]), LEDGER_REF)
        self._commit(Path(beta["root"]), LEDGER_REF)
        return alpha, beta

    def test_a_pair_correlated_only_by_legacy_receipts_is_refused_with_the_six_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            alpha, beta = self._ledgers(Path(tmp))
            later = {"commit": "writer", "committed_at_unix": 2 ** 40, "source": "TEST"}
            report = run_live([alpha, beta], fetch=False, writer_introduction=lambda peer: later)
            earlier = run_live([alpha, beta], fetch=False,
                               writer_introduction=lambda peer: {**later, "committed_at_unix": 1})
        self.assertEqual(report["counts"]["PASS"], 0)
        self.assertFalse(report["authenticity_claimed"])
        for hop in report["hops"]:
            self.assertEqual(hop["status"], "FAIL")
            self.assertEqual(hop["findings"], [lane.LEGACY_ONLY_FINDING])
            self.assertEqual(hop["failure_code"], "INTR_HOP_CORRELATED_ONLY_BY_LEGACY_RECEIPTS")
            self.assertEqual(hop["failed_predicate"], "LIVE_HOP_CORRELATION_USES_NON_LEGACY_RECEIPTS")
            self.assertEqual(hop["communication_ids_read_back"], [])
            self.assertEqual(len(hop["legacy_communication_ids_reported"]), 1)
            self.assertEqual(hop["ledger_state"], "UNSENT")
            self.assertIs(hop["authenticity_claimed"], False)
            _assert_six(self, hop)
        # The same receipts appended after the writer's introduction correlate and pass.
        self.assertEqual(earlier["counts"]["PASS"], 2, [hop["findings"] for hop in earlier["hops"]])
        self.assertTrue(all(hop["legacy_communication_ids_reported"] == [] for hop in earlier["hops"]))

    def test_orchestrate_sends_a_legacy_only_pair_again(self):
        with tempfile.TemporaryDirectory() as tmp:
            alpha, beta = self._ledgers(Path(tmp))
            later = {"commit": "writer", "committed_at_unix": 2 ** 40, "source": "TEST"}
            report = run_live([alpha, beta], fetch=False, writer_introduction=lambda peer: later)
        states = {(hop["sender_slug"], hop["destination_slug"]): hop["ledger_state"] for hop in report["hops"]}
        sent = []
        result = lane.run_orchestrate([alpha, beta], hb_epoch=32, token="t-value", ledger_state=states,
                                      dispatcher=lambda s, t, **kw: (sent.append((s["slug"], t["slug"])) or True,
                                                                     "DISPATCHED"))
        self.assertEqual(len(sent), 1)
        self.assertNotIn("CLOSED_IN_READ_LEDGERS", result["outcomes"])

    def test_pair_state_ignores_legacy_receipts(self):
        emitted, closed, _ = _pair_receipts("Alpha", "Beta", "beta.intr-destination", "cid-1", "pkt-1")
        chain = [emitted, closed]
        self.assertEqual(lane.pair_ledger_state(chain, "Beta", "beta.intr-destination"), "CLOSED")
        everything = [emitted["receipt_sha256"], closed["receipt_sha256"]]
        self.assertEqual(lane.pair_ledger_state(chain, "Beta", "beta.intr-destination", legacy=everything), "UNSENT")
        self.assertEqual(lane.pair_ledger_state(chain, "Beta", "beta.intr-destination",
                                                legacy=[closed["receipt_sha256"]]), "OPEN")

    def test_only_declared_findings_are_reported_on_legacy_receipts(self):
        self.assertNotIn("CHAIN_PREDECESSOR_MISMATCH", lane.LEGACY_REPORTABLE)
        repo = {"present": True, "chain": [], "findings": ["CHAIN_PREDECESSOR_MISMATCH"], "sources": {}, "introduced_at": {}}
        org = {"present": True, "chain": [], "findings": [], "sources": {}, "introduced_at": {}}
        report = lane.integrity_report(repo, org, writer_introduction={"committed_at_unix": 2 ** 40})
        self.assertIn("CHAIN_PREDECESSOR_MISMATCH", report["findings"])
        self.assertEqual(report["legacy_receipts"], {"repository": [], "organization": []})


class CorrelationEvidenceClassTests(unittest.TestCase):
    """The declared table, and the refusal of a class it does not list. Receipts are fabricated."""

    _peer = LiveLedgerTests._peer
    _commit = LiveLedgerTests._commit
    _write_both = LiveLedgerTests._write_both
    _write_org = LiveLedgerTests._write_org

    def _swap(self, table):
        original = dict(lane.CORRELATION_EVIDENCE_CLASSES)
        lane.CORRELATION_EVIDENCE_CLASSES.clear()
        lane.CORRELATION_EVIDENCE_CLASSES.update(table)
        self.addCleanup(lambda: (lane.CORRELATION_EVIDENCE_CLASSES.clear(),
                                 lane.CORRELATION_EVIDENCE_CLASSES.update(original)))

    def _assert_refusal(self, refusal, evidence_class=None):
        self.assertEqual(refusal["disposition"], "FAIL_CLOSED")
        self.assertEqual(refusal["failure_code"], "CORRELATION_EVIDENCE_CLASS_NOT_DECLARED")
        self.assertEqual(refusal["failed_predicate"], "RECEIPT_CLASS_IS_A_DECLARED_CORRELATION_EVIDENCE_CLASS")
        self.assertIs(refusal["consequence_committed"], False)
        if evidence_class is not None:
            self.assertEqual(refusal["evidence_class"], evidence_class)
        _assert_six(self, refusal)

    def test_the_table_is_pinned(self):
        self.assertEqual(lane.CORRELATION_EVIDENCE_CLASSES, {
            "LIVE_SUPPLIED_EPOCH": "LIVE_EVIDENCE",
            "LEGACY": "REPORTABLE",
            "IDENTICAL_DUPLICATE": "REPORTABLE",
            "DIVERGENT_DUPLICATE": "REFUSED",
            "ORG_RECEIPT_SOURCE_UNNAMED": "REPORTABLE",
        })
        live = [name for name, value in lane.CORRELATION_EVIDENCE_CLASSES.items() if value == "LIVE_EVIDENCE"]
        self.assertEqual(live, ["LIVE_SUPPLIED_EPOCH"])
        source = Path(lane.__file__).read_text(encoding="utf-8")
        self.assertIn("Q-G4 (JOINT DISCOVERY", source)

    def test_an_unlisted_class_is_fail_closed_with_the_six_fields(self):
        for unlisted in ("NOT_A_CLASS", "", None, 7):
            disposition, refusal = lane.correlation_evidence_disposition(unlisted)
            self.assertIsNone(disposition)
            self._assert_refusal(refusal, unlisted)
        disposition, refusal = lane.correlation_evidence_disposition("LEGACY", {"LEGACY": "MAYBE"})
        self.assertIsNone(disposition)
        self._assert_refusal(refusal, "LEGACY")
        self.assertEqual(lane.correlation_evidence_disposition("LEGACY"), ("REPORTABLE", None))

    def test_the_readback_reads_the_table_for_reported_cases(self):
        first = _repo(None, "ORGANIZATION_INGRESS_MATERIALIZED:node", "ORGANIZATION_INGRESS_MATERIALIZED",
                      {"node": "n"}, "Alpha/.github")
        again = _repo(first["receipt_sha256"], first["transition_id"], first["transition_class"],
                      {"node": "n"}, "Alpha/.github")
        org = [_org(None, first)]
        org.append(_org(org[0]["receipt_sha256"], again))
        repo_view, org_view = LedgerIntegrityClassificationTests._views(self, [first, again], org)
        self.assertEqual(lane.integrity_report(repo_view, org_view)["findings"], [])
        table = dict(lane.CORRELATION_EVIDENCE_CLASSES)
        del table["IDENTICAL_DUPLICATE"]
        self._swap(table)
        report = lane.integrity_report(repo_view, org_view)
        self.assertIn("CORRELATION_EVIDENCE_CLASS_NOT_DECLARED", report["findings"])
        self._assert_refusal(report["evidence_class_refusals"][0], "IDENTICAL_DUPLICATE")
        self.assertNotIn("IDENTICAL_DUPLICATE_REPOSITORY_RECEIPT", [item["finding"] for item in report["reported"]])

    def test_an_undeclared_live_class_correlates_nothing(self):
        table = dict(lane.CORRELATION_EVIDENCE_CLASSES)
        del table["LIVE_SUPPLIED_EPOCH"]
        self._swap(table)
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            alpha = self._peer(base / "alpha", "Alpha")
            beta = self._peer(base / "beta", "Beta")
            self._write_both(Path(alpha["root"]), Path(beta["root"]))
            self._commit(Path(alpha["root"]), LEDGER_REF)
            self._commit(Path(beta["root"]), LEDGER_REF)
            report = run_live([alpha, beta], fetch=False)
        self.assertEqual(report["counts"]["PASS"], 0)
        self.assertFalse(report["authenticity_claimed"])
        for hop in report["hops"]:
            self.assertEqual(hop["status"], "FAIL")
            self.assertIn("CORRELATION_EVIDENCE_CLASS_NOT_DECLARED", hop["findings"])
            self.assertEqual(hop["failure_code"], "CORRELATION_EVIDENCE_CLASS_NOT_DECLARED")
            self.assertEqual(hop["communication_ids_read_back"], [])
            _assert_six(self, hop)
        for detail in report["ledger_integrity"].values():
            self.assertEqual(detail["failure_code"], "CORRELATION_EVIDENCE_CLASS_NOT_DECLARED")
            self._assert_refusal(detail["evidence_class_refusals"][0], "LIVE_SUPPLIED_EPOCH")


class WriterIntroductionNotObservedTests(unittest.TestCase):
    """Without an observed writer introduction nothing is LEGACY, so the hop is FAIL_CLOSED.

    Pre-writer receipts must never PASS or claim authenticity just because the
    introduction was not found or the lookup was turned off. Fabricated
    temporary ledgers only; nothing is dispatched or appended.
    """

    def _two(self, base: Path):
        helper = LiveLedgerTests()
        alpha = helper._peer(base / "alpha", "Alpha")
        beta = helper._peer(base / "beta", "Beta")
        helper._write_both(Path(alpha["root"]), Path(beta["root"]))
        helper._commit(Path(alpha["root"]), LEDGER_REF)
        helper._commit(Path(beta["root"]), LEDGER_REF)
        return alpha, beta

    def _assert_fail_closed(self, report, reason):
        self.assertEqual(report["hop_count"], 2)
        self.assertEqual(report["counts"].get("PASS", 0), 0, [hop["findings"] for hop in report["hops"]])
        self.assertIs(report["authenticity_claimed"], False)
        self.assertEqual(set(report["writer_introduction_not_observed"].values()), {reason})
        for hop in report["hops"]:
            self.assertEqual(hop["status"], "FAIL")
            self.assertEqual(hop["disposition"], "FAIL_CLOSED")
            self.assertIn(lane.WRITER_INTRODUCTION_NOT_OBSERVED, hop["findings"])
            self.assertEqual(hop["failure_code"], "WRITER_INTRODUCTION_NOT_OBSERVED")
            self.assertEqual(hop["failed_predicate"], lane.WRITER_INTRODUCTION_PREDICATE)
            self.assertEqual(hop["owning_existing_goal"], "INTERLOCK-INTR-RUNTIME-INDEPENDENT-PROTOCOL-001")
            self.assertIs(hop["authenticity_claimed"], False)
            self.assertIsNone(hop["authenticity_basis"])
            self.assertEqual(hop["communication_ids_read_back"], [])
            self.assertTrue(hop["unclassified_communication_ids_reported"])
            for field in lane.NON_ALLOW_FIELDS:
                self.assertIsInstance(hop.get(field), str, field)
                self.assertTrue(hop[field].strip(), field)

    def test_control_an_observed_introduction_passes_the_same_ledgers(self):
        with tempfile.TemporaryDirectory() as tmp:
            peers = self._two(Path(tmp))
            report = run_live(list(peers), fetch=False, writer_introduction=_WRITER_BEFORE_EVERY_RECEIPT)
        self.assertEqual(report["counts"]["PASS"], 2, [hop["findings"] for hop in report["hops"]])
        self.assertEqual(report["writer_introduction_not_observed"], {})

    def test_a_writer_introduction_not_found_fails_closed_and_never_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            peers = self._two(Path(tmp))
            report = run_live(list(peers), fetch=False, writer_introduction=lambda peer: None)
        self._assert_fail_closed(report, lane.WRITER_INTRODUCTION_NOT_FOUND)

    def test_a_malformed_introduction_is_not_observed(self):
        for bad in ({}, {"committed_at_unix": None}, {"committed_at_unix": "1"}, {"committed_at_unix": True}, "x"):
            with tempfile.TemporaryDirectory() as tmp:
                peers = self._two(Path(tmp))
                report = run_live(list(peers), fetch=False, writer_introduction=lambda peer, bad=bad: bad)
            self._assert_fail_closed(report, lane.WRITER_INTRODUCTION_NOT_FOUND)

    def test_one_side_without_an_introduction_fails_both_of_its_hops(self):
        with tempfile.TemporaryDirectory() as tmp:
            peers = self._two(Path(tmp))
            report = run_live(list(peers), fetch=False, writer_introduction=lambda peer: (
                None if peer["slug"] == "beta" else _WRITER_BEFORE_EVERY_RECEIPT(peer)))
        self.assertEqual(report["writer_introduction_not_observed"], {"beta": lane.WRITER_INTRODUCTION_NOT_FOUND})
        for hop in report["hops"]:
            self.assertEqual(hop["failure_code"], "WRITER_INTRODUCTION_NOT_OBSERVED")
            self.assertEqual(hop["writer_introduction_not_observed"], {"beta": lane.WRITER_INTRODUCTION_NOT_FOUND})
            self.assertIs(hop["authenticity_claimed"], False)

    def test_no_writer_introduction_argument_is_lookup_disabled(self):
        with tempfile.TemporaryDirectory() as tmp:
            peers = self._two(Path(tmp))
            report = run_live(list(peers), fetch=False)
        self._assert_fail_closed(report, lane.WRITER_LOOKUP_DISABLED)

    def test_cli_no_writer_lookup_fails_closed_with_six_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            peers = self._two(Path(tmp) / "orgs")
            original = lane.discover_peers_from_github
            lane.discover_peers_from_github = lambda organizations, *, token=None, read_file=None: (
                [dict(peer) for peer in peers], [])
            try:
                out = Path(tmp) / "out"
                code = main(["--mode", "live", "--out-dir", str(out), "--no-writer-lookup",
                             "--organization", "Alpha", "--organization", "Beta"])
            finally:
                lane.discover_peers_from_github = original
            report = json.loads((out / "intr-destination-hop-lane.json").read_text(encoding="utf-8"))
        self.assertEqual(code, 1)
        self._assert_fail_closed(report, lane.WRITER_LOOKUP_DISABLED)

    def test_cli_writer_override_still_classifies_with_lookup_disabled(self):
        with tempfile.TemporaryDirectory() as tmp:
            peers = self._two(Path(tmp) / "orgs")
            original = lane.discover_peers_from_github
            lane.discover_peers_from_github = lambda organizations, *, token=None, read_file=None: (
                [dict(peer) for peer in peers], [])
            try:
                out = Path(tmp) / "out"
                code = main(["--mode", "live", "--out-dir", str(out), "--no-writer-lookup",
                             "--organization", "Alpha", "--organization", "Beta",
                             "--writer-introduced", "Alpha=1", "--writer-introduced", "Beta=1"])
            finally:
                lane.discover_peers_from_github = original
            report = json.loads((out / "intr-destination-hop-lane.json").read_text(encoding="utf-8"))
        self.assertEqual(code, 0, [hop["findings"] for hop in report["hops"]])
        self.assertEqual(report["counts"]["PASS"], 2)
        self.assertEqual(report["writer_introduction_not_observed"], {})


if __name__ == "__main__":
    unittest.main()
