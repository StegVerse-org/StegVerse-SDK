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


if __name__ == "__main__":
    unittest.main()
