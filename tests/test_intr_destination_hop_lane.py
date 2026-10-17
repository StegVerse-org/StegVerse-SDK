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
import subprocess
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
            report = run_live([alpha, beta], fetch=False)
            self.assertEqual(report["counts"]["PASS"], 2, [hop["findings"] for hop in report["hops"]])
            self.assertTrue(report["authenticity_claimed"])
            self.assertTrue(all(hop["authenticity_claimed"] for hop in report["hops"]))
            # Drop Beta's ref. Hops that need Beta degrade; nothing is appended.
            subprocess.run(["git", "update-ref", "-d", LEDGER_REF], cwd=beta["root"], check=True)
            degraded = run_live([alpha, beta], fetch=False)
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
            report = run_live([alpha, beta, unread[0]], fetch=True)
        by_pair = {(hop["sender_slug"], hop["destination_slug"]): hop for hop in report["hops"]}
        self.assertEqual(by_pair[("alpha", "beta")]["status"], "PASS", by_pair[("alpha", "beta")]["findings"])
        self.assertEqual(by_pair[("beta", "alpha")]["status"], "PASS")
        self.assertTrue(by_pair[("alpha", "beta")]["authenticity_claimed"])
        self.assertEqual(by_pair[("alpha", "sv-011")]["status"], "UNREACHABLE")
        self.assertFalse(by_pair[("sv-011", "beta")]["authenticity_claimed"])
        self.assertEqual(report["counts"], {"PASS": 2, "FAIL": 0, "UNREACHABLE": 4})
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

    def test_orchestration_dispatches_send_per_wave_and_waits_for_closure(self):
        peers = self._peers()
        dispatched = []
        ledgers: dict[str, list] = {peer["slug"]: [] for peer in peers}

        def dispatcher(sender, dest, *, communication_id, hb_epoch):
            dispatched.append((sender["slug"], dest["slug"], communication_id, hb_epoch))
            # The fabricated sender ledger closes the hop (non-authentic).
            klass = CLOSED_CLASS if dest["slug"] != "stegghost" else lane.CLOSURE_REFUSED_CLASS
            ledgers[sender["slug"]].append({"schema": REPO_SCHEMA, "transition_class": klass,
                                            "evidence": {"communication_id": communication_id}})
            return True, "DISPATCHED"

        slept = []
        result = lane.run_orchestrate(
            peers, hb_epoch_base=1000, token="t-value", dispatcher=dispatcher,
            probe=lambda sender: ledgers[sender["slug"]], sleep=slept.append)
        self.assertEqual(len(dispatched), 56)
        self.assertEqual(result["dispatched"], 56)
        self.assertEqual([wave["hb_epoch"] for wave in result["waves"]], [1000 + 3 * i for i in range(14)])
        self.assertEqual(result["outcomes"], {"CLOSED": 49, "REFUSED": 7})
        first = dispatched[0]
        self.assertEqual(first[2], "intr-hop:%s:%s:1000" % (first[0], first[1]))
        self.assertEqual(slept, [])
        self.assertNotIn("t-value", json.dumps(result))
        self.assertEqual(result["time_constraint"], "SUPPLIED_HB_EPOCH")

    def test_an_open_hop_times_out_and_a_failed_dispatch_is_recorded(self):
        peers = self._peers(2)
        ticks = iter(range(0, 10000, 100))

        def dispatcher(sender, dest, *, communication_id, hb_epoch):
            return (sender["slug"] == "stegverse-org"), ("DISPATCHED" if sender["slug"] == "stegverse-org" else "DISPATCH_HTTP_404")

        result = lane.run_orchestrate(
            peers, hb_epoch_base=40, token="t-value", dispatcher=dispatcher, probe=lambda sender: [],
            sleep=lambda seconds: None, monotonic=lambda: next(ticks), wave_timeout_seconds=250)
        outcomes = {(hop["sender_slug"], hop["outcome"]) for wave in result["waves"] for hop in wave["hops"]}
        self.assertEqual(outcomes, {("stegverse-org", "TIMEOUT"), ("stegverse-labs", "NOT_DISPATCHED")})
        with self.assertRaises(ValueError):
            lane.run_orchestrate(peers, hb_epoch_base=40, token=" ", dispatcher=dispatcher, probe=lambda s: [])

    def test_the_send_dispatch_names_the_hop_workflow_and_keeps_the_token_in_a_header(self):
        seen = {}

        class Response:
            status_code = 204
            content = b""

        def poster(url, json=None, headers=None, timeout=30):
            seen.update(url=url, json=json, headers=headers)
            return Response()

        peers = self._peers(2)
        ok, detail = lane.dispatch_send_hop(peers[0], peers[1], communication_id="intr-hop:a:b:7",
                                            hb_epoch=7, token="t-value", poster=poster)
        self.assertTrue(ok)
        self.assertEqual(detail, "DISPATCHED")
        self.assertEqual(seen["url"], "https://api.github.com/repos/StegVerse-org/.github/actions/workflows/"
                         "intr-destination-hop.yml/dispatches")
        self.assertEqual(seen["json"]["inputs"], {"phase": "send", "destination_slug": "stegverse-labs",
                                                  "communication_id": "intr-hop:a:b:7", "hb_epoch": "7",
                                                  "forward": "true"})
        self.assertEqual(seen["headers"]["Authorization"], "Bearer t-value")
        self.assertNotIn("t-value", seen["url"])

    def test_orchestrate_cli_requires_a_supplied_epoch_and_the_hop_token(self):
        previous = {name: os.environ.pop(name, None) for name in (lane.FEDERATION_HOP_TOKEN_ENV, FEDERATION_READ_TOKEN_ENV)}
        try:
            with tempfile.TemporaryDirectory() as tmp:
                os.environ[lane.FEDERATION_HOP_TOKEN_ENV] = "t-value"
                with self.assertRaises(SystemExit):
                    main(["--mode", "orchestrate", "--out-dir", tmp])
                os.environ.pop(lane.FEDERATION_HOP_TOKEN_ENV)
                with self.assertRaises(SystemExit):
                    main(["--mode", "orchestrate", "--hb-epoch-base", "40", "--out-dir", tmp])
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


if __name__ == "__main__":
    unittest.main()
