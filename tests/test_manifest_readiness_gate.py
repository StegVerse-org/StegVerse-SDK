"""SDK#368 readiness gate: negative controls from acceptance contract item 7.

These are source tests over caller-supplied evidence fixtures. They are not
original live runtime receipts and claim no runtime observation.
"""
from __future__ import annotations

import contextlib
import copy
import io
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from stegverse.capability_inventory import (
    ATTEMPTED_TRANSITION,
    INCOMPATIBLE,
    INVOCATION_PROBE,
    NON_OPERATIONAL,
    NOT_REQUIRED,
    OFFLINE,
    OPERATIONAL,
    READINESS_EVIDENCE_SCHEMA,
    READY,
    UNVERIFIED,
    hmac_evidence_verifier,
    sign_readiness_evidence,
)
from stegverse.cli import main
from stegverse.manifest_builder import (
    LOCAL_CONFORMANCE,
    WORKAROUND_SELECTION_EXTENSION,
    apply_workaround_selection,
    build_manifest,
    build_qualified_manifest,
    qualify_draft_manifest,
)
from stegverse.manifest_contract import validate_ingress_manifest
from stegverse.manifest_plan import (
    INCIDENT_NOTIFICATION_ROUTE_EXTENSION,
    NO_VERIFIED_WORKAROUND,
    NOT_READY,
    QUALIFIED_READY,
    deliver_incident_notification,
    derive_readiness_dag,
    enumerate_workarounds,
    qualify_manifest_readiness,
    readiness_invocation_binding,
    require_ready_qualification,
)
from stegverse.route_resolution import (
    CANONICAL_PRODUCTION_ROUTE_ID,
    CUSTOMER_LOCAL_GOVERNANCE_ROUTE_ID,
    PUBLISHED_ROUTES,
    STEGBROWSER_ROUTE_ID,
)
from tests.test_organization_batch_manifest_task_binding import canonical_request, governance_request

NOW = datetime(2026, 10, 9, 23, 50, tzinfo=timezone.utc)
KEY_ID = "steghealth-fixture-key"
KEY = "11" * 32
VERIFY = hmac_evidence_verifier({KEY_ID: KEY})
ATTEMPT = "attempt-1"
REMEDIATION = "STEGHEALTH-ECOSYSTEM-FAILURE-REMEDIATION-001"


def _iso(moment):
    return moment.isoformat().replace("+00:00", "Z")


def _build_kwargs(**overrides):
    payload = canonical_request()
    kwargs = {
        "data": payload,
        "source_framework": "fixture-framework",
        "source_output_id": "readiness-fixture",
        "processor_request": governance_request(payload),
        "process": "governance",
        "created_at": "2026-10-09T23:49:00Z",
    }
    kwargs.update(overrides)
    return kwargs


def _draft(**overrides):
    return build_manifest(**_build_kwargs(**overrides))


def _binding(manifest, route_id=None, attempt=ATTEMPT):
    return readiness_invocation_binding(
        manifest_sha256=validate_ingress_manifest(manifest)["canonical_manifest_sha256"],
        attempt_id=attempt,
        route_id=route_id or manifest["processing"]["route_id"],
        processing_capability=manifest["processing"]["capability"],
        payload_sha256=manifest["hashes"]["payload_sha256"],
        source_framework=manifest["source_framework"],
        source_output_id=manifest["source_output_id"],
    )


def _evidence(manifest, node, *, state=OPERATIONAL, kind=INVOCATION_PROBE, at=None,
              attempt=ATTEMPT, contract_ref=None, sign=True, route_id=None):
    record = {
        "schema": READINESS_EVIDENCE_SCHEMA,
        "node_id": node["node_id"],
        "contract_ref": contract_ref or node["contract_ref"],
        "invocation_binding_sha256": _binding(manifest, route_id or node["route_id"], attempt),
        "observation_kind": kind,
        "observed_state": state,
        "observed_at": _iso(at or NOW - timedelta(seconds=60)),
        "provenance": "fixture:" + node["role"],
        "evidence_ref": "evidence://fixture/" + node["node_id"],
    }
    return sign_readiness_evidence(record, key_id=KEY_ID, key=KEY) if sign else record


def _all_ready(manifest, route_id=None, *, skip=(), at=None):
    return [
        _evidence(manifest, node, at=at)
        for node in derive_readiness_dag(manifest, route_id=route_id)
        if node["required"] and node["role"] not in skip
    ]


def _node(manifest, role, route_id=None):
    return next(n for n in derive_readiness_dag(manifest, route_id=route_id) if n["role"] == role)


def _qualify(manifest, evidence=(), **kwargs):
    kwargs.setdefault("evidence_verifier", VERIFY)
    kwargs.setdefault("now", NOW)
    return qualify_manifest_readiness(manifest, attempt_id=ATTEMPT, readiness_evidence=evidence, **kwargs)


def _state(qualification, role):
    return next(n for n in qualification["nodes"] if n["role"] == role)


class ReadinessDagTests(unittest.TestCase):
    def test_dag_is_manifest_selected_and_covers_contract_roles(self):
        manifest = _draft()
        dag = derive_readiness_dag(manifest)
        self.assertEqual({n["route_id"] for n in dag}, {CANONICAL_PRODUCTION_ROUTE_ID})
        self.assertEqual(
            [n["role"] for n in dag],
            ["ingress", "authorization", "route", "processor", "consequence", "custody", "return", "publisher"],
        )
        required = {n["role"] for n in dag if n["required"]}
        self.assertEqual(required, {"ingress", "authorization", "route", "processor", "custody", "return"})
        for node in dag:
            for parent in node["depends_on"]:
                self.assertIn(parent, {n["node_id"] for n in dag})

    def test_declared_consequence_and_publisher_become_required(self):
        manifest = _draft(publisher_destination={"type": "SDK_CONSOLE_SESSION", "session_ref": "s-1"})
        self.assertTrue(_node(manifest, "publisher")["required"])
        self.assertTrue(_node(manifest, "consequence", STEGBROWSER_ROUTE_ID)["required"])

    def test_all_ready_is_non_authorizing_readiness_only(self):
        manifest = _draft()
        q = _qualify(manifest, _all_ready(manifest))
        self.assertEqual(q["qualification"], QUALIFIED_READY)
        self.assertEqual(q["disposition"], "ALLOW")
        self.assertEqual(q["disposition_scope"], "READINESS_QUALIFICATION_ONLY")
        self.assertIs(q["executable"], True)
        self.assertIs(q["execution_authorized"], False)
        self.assertIs(q["runtime_allow_claimed"], False)
        self.assertIsNone(q["workarounds"])
        self.assertEqual(_state(q, "consequence")["state"], NOT_REQUIRED)
        self.assertEqual(q["manifest_sha256"], validate_ingress_manifest(manifest)["canonical_manifest_sha256"])


class NegativeControlTests(unittest.TestCase):
    def test_route_installed_without_evidence_is_unverified_never_ready_or_offline(self):
        manifest = _draft()
        self.assertIs(PUBLISHED_ROUTES[CANONICAL_PRODUCTION_ROUTE_ID]["runtime_installed"], True)
        q = _qualify(manifest)
        self.assertEqual(q["qualification"], NOT_READY)
        self.assertEqual(q["disposition"], "FAIL_CLOSED")
        self.assertIs(q["executable"], False)
        for node in q["failing_nodes"]:
            self.assertEqual(node["state"], UNVERIFIED)
            self.assertEqual(node["failed_predicate"], "AUTHENTICATED_INVOCATION_BOUND_EVIDENCE_PRESENT")
            self.assertIs(node["source_runtime_installed"], True)
            self.assertIs(node["runtime_installed_is_readiness"], False)
        self.assertEqual(q["incident_notifications"], [])

    def test_route_installed_but_offline_on_attempted_transition(self):
        manifest = _draft()
        offline = _evidence(manifest, _node(manifest, "processor"), state=NON_OPERATIONAL, kind=ATTEMPTED_TRANSITION)
        q = _qualify(manifest, _all_ready(manifest, skip={"processor"}) + [offline])
        node = _state(q, "processor")
        self.assertEqual(q["qualification"], NOT_READY)
        self.assertEqual(node["state"], OFFLINE)
        self.assertEqual(node["failed_predicate"], "COMPONENT_OPERATIONAL_ON_ATTEMPTED_TRANSITION")
        self.assertEqual(node["observed_at"], offline["observed_at"])
        self.assertEqual(node["provenance"], offline["provenance"])
        self.assertEqual(node["evidence_ref"], offline["evidence_ref"])
        self.assertEqual([n["role"] for n in q["failing_nodes"]], ["processor"])
        (incident,) = q["incident_notifications"]
        self.assertEqual(incident["remediation_owner"]["owner_task"], REMEDIATION)
        self.assertEqual(incident["original_evidence"], offline)
        self.assertEqual(incident["manifest_sha256"], q["manifest_sha256"])
        self.assertIsNone(incident["transport"])
        (delivery,) = q["incident_notification_delivery"]
        self.assertEqual(delivery["disposition"], "FAIL_CLOSED")
        self.assertEqual(delivery["failed_predicate"], "NOTIFICATION_ROUTE_NOT_RESOLVED")
        self.assertIs(delivery["delivered_by_sdk"], False)

    def test_unknown_capability_is_distinct_from_offline(self):
        unknown = build_qualified_manifest(attempt_id=ATTEMPT, **_build_kwargs(process="not_a_capability"))
        self.assertEqual(unknown["state"], "CAPABILITY_DEVELOPMENT_REQUESTED")
        self.assertEqual(unknown["disposition"], "FAIL_CLOSED")
        self.assertIs(unknown["executable"], False)
        # A non-operational observation that is not an attempted transition is not OFFLINE.
        manifest = _draft()
        probe = _evidence(manifest, _node(manifest, "processor"), state=NON_OPERATIONAL, kind=INVOCATION_PROBE)
        node = _state(_qualify(manifest, [probe]), "processor")
        self.assertEqual(node["state"], UNVERIFIED)
        self.assertEqual(node["failed_predicate"], "OFFLINE_REQUIRES_ATTEMPTED_TRANSITION")

    def test_stale_future_falsified_unbound_and_unsigned_evidence_is_unverified(self):
        manifest = _draft()
        node = _node(manifest, "route")
        tampered = _evidence(manifest, node)
        tampered["observed_state"] = NON_OPERATIONAL
        cases = {
            "EVIDENCE_FRESH": [_evidence(manifest, node, at=NOW - timedelta(hours=1))],
            "EVIDENCE_AUTHENTICATED": [tampered],
            "EVIDENCE_INVOCATION_BOUND": [_evidence(manifest, node, attempt="another-attempt")],
        }
        cases_future = [_evidence(manifest, node, at=NOW + timedelta(minutes=5))]
        for predicate, evidence in list(cases.items()) + [("EVIDENCE_FRESH", cases_future)]:
            result = _state(_qualify(manifest, evidence), "route")
            self.assertEqual((result["state"], result["failed_predicate"]), (UNVERIFIED, predicate))
        unsigned = _state(_qualify(manifest, [_evidence(manifest, node, sign=False)]), "route")
        self.assertEqual(unsigned["failed_predicate"], "EVIDENCE_AUTHENTICATED")
        no_trust_root = _state(_qualify(manifest, [_evidence(manifest, node)], evidence_verifier=None), "route")
        self.assertEqual(no_trust_root["failed_predicate"], "EVIDENCE_AUTHENTICATED")
        wrong_key = _state(
            _qualify(manifest, [_evidence(manifest, node)], evidence_verifier=hmac_evidence_verifier({KEY_ID: "22" * 32})),
            "route",
        )
        self.assertEqual(wrong_key["failed_predicate"], "EVIDENCE_AUTHENTICATED")
        # A newer forged record masks an older valid one: fail closed, never open.
        older = _evidence(manifest, node, at=NOW - timedelta(seconds=120))
        newer = _evidence(manifest, node, at=NOW - timedelta(seconds=10), sign=False)
        self.assertEqual(_state(_qualify(manifest, [older, newer]), "route")["state"], UNVERIFIED)

    def test_missing_authorization_evidence_fails_closed(self):
        manifest = _draft()
        q = _qualify(manifest, _all_ready(manifest, skip={"authorization"}))
        self.assertEqual(q["qualification"], NOT_READY)
        self.assertEqual([n["role"] for n in q["failing_nodes"]], ["authorization"])
        self.assertEqual(q["failing_nodes"][0]["component"], "TVC_RELAY_AUTHORIZATION_INTERLOCK_INTR")

    def test_incompatible_contract_version(self):
        manifest = _draft()
        bad = _evidence(manifest, _node(manifest, "ingress"), contract_ref="0" * 64)
        q = _qualify(manifest, _all_ready(manifest, skip={"ingress"}) + [bad])
        node = _state(q, "ingress")
        self.assertEqual((node["state"], node["failed_predicate"]), (INCOMPATIBLE, "COMPONENT_CONTRACT_COMPATIBLE"))
        self.assertEqual(len(q["incident_notifications"]), 1)

    def test_alternate_route_lacking_custody_or_consequence_is_inadmissible(self):
        no_custody = dict(PUBLISHED_ROUTES[CUSTOMER_LOCAL_GOVERNANCE_ROUTE_ID],
                          route_id="fixture.no-custody", runtime_binding="stegverse.fixture.execute_manifest")
        no_consequence = dict(PUBLISHED_ROUTES[STEGBROWSER_ROUTE_ID],
                              route_id="fixture.no-consequence", external_consequence_enabled=False)
        routes = {**PUBLISHED_ROUTES, "fixture.no-custody": no_custody, "fixture.no-consequence": no_consequence}
        called = []

        def qualify(route_id):
            called.append(route_id)
            return {"qualification": QUALIFIED_READY}

        governance = enumerate_workarounds(
            _draft(), qualify=qualify, alternative_routes=["fixture.no-custody"], published_routes=routes,
        )
        by_route = {c["route_id"]: c for c in governance["candidates"]}
        self.assertEqual(by_route["fixture.no-custody"]["candidate_state"], "INADMISSIBLE")
        self.assertEqual(by_route["fixture.no-custody"]["failed_predicate"], "ALTERNATE_ROUTE_CUSTODY_SEMANTICS_PRESENT")
        browser = enumerate_workarounds(
            {"extensions": {"stegverse_route": {"route_id": STEGBROWSER_ROUTE_ID}}},
            qualify=qualify, alternative_routes=["fixture.no-consequence"], published_routes=routes,
        )
        (candidate,) = browser["candidates"]
        self.assertEqual(candidate["failed_predicate"], "ALTERNATE_ROUTE_CONSEQUENCE_SEMANTICS_PRESENT")
        self.assertEqual(browser["state"], NO_VERIFIED_WORKAROUND)
        self.assertEqual(browser["remediation_reference"]["owner_task"], REMEDIATION)
        self.assertNotIn("fixture.no-custody", called)
        self.assertNotIn("fixture.no-consequence", called)

    def test_no_verified_workaround_names_steghealth_remediation(self):
        q = _qualify(_draft())
        self.assertEqual(q["workarounds"]["state"], NO_VERIFIED_WORKAROUND)
        self.assertEqual(q["workarounds"]["remediation_reference"]["owner_task"], REMEDIATION)
        self.assertEqual(q["workarounds"]["remediation_reference"]["issue"], "StegVerse-Labs/StegHealth#51")
        self.assertIs(q["workarounds"]["automatic_selection_permitted"], False)
        (candidate,) = q["workarounds"]["candidates"]
        self.assertEqual(candidate["route_id"], CUSTOMER_LOCAL_GOVERNANCE_ROUTE_ID)
        self.assertEqual(candidate["candidate_state"], "NOT_VERIFIED")

    def test_notification_delivery_is_its_own_fail_closed_transition(self):
        manifest = _draft()
        offline = _evidence(manifest, _node(manifest, "custody"), state=NON_OPERATIONAL, kind=ATTEMPTED_TRANSITION)
        (record,) = _qualify(manifest, [offline])["incident_notifications"]
        routes = {**PUBLISHED_ROUTES, "fixture.notify": {"route_id": "fixture.notify",
                                                         "processor_capability": "incident_notification"}}
        declared = copy.deepcopy(manifest)
        declared["extensions"][INCIDENT_NOTIFICATION_ROUTE_EXTENSION] = "fixture.notify"

        def deliver(**kwargs):
            return deliver_incident_notification(record, published_routes=routes, **kwargs)

        self.assertEqual(deliver(manifest=manifest)["failed_predicate"], "NOTIFICATION_ROUTE_NOT_RESOLVED")
        self.assertEqual(deliver(manifest=declared)["failed_predicate"], "NOTIFICATION_TRANSPORT_NOT_BOUND")

        def broken(_record, _route):
            raise ConnectionError("intake unavailable")

        failed = deliver(manifest=declared, deliver=broken)
        self.assertEqual((failed["disposition"], failed["failed_predicate"]), ("FAIL_CLOSED", "NOTIFICATION_DELIVERY_FAILED"))
        self.assertIn("intake unavailable", failed["evidence"])
        unbound = deliver(manifest=declared, deliver=lambda r, _: {"idempotency_key": "other", "ack_ref": "a"})
        self.assertEqual(unbound["failed_predicate"], "NOTIFICATION_ACK_BOUND_TO_RECORD")
        acked = deliver(manifest=declared, deliver=lambda r, _: {"idempotency_key": r["idempotency_key"], "ack_ref": "ack-1"})
        self.assertEqual(acked["disposition"], "ALLOW")
        self.assertIs(acked["delivered_by_sdk"], False)

    def test_incident_is_idempotent(self):
        manifest = _draft()
        offline = _evidence(manifest, _node(manifest, "return"), state=NON_OPERATIONAL, kind=ATTEMPTED_TRANSITION)
        first = _qualify(manifest, [offline])["incident_notifications"]
        second = _qualify(manifest, [copy.deepcopy(offline)])["incident_notifications"]
        self.assertEqual(first, second)
        self.assertEqual(first[0]["idempotency_key"], second[0]["idempotency_key"])
        other = qualify_manifest_readiness(
            manifest, attempt_id="attempt-2", now=NOW, evidence_verifier=VERIFY,
            readiness_evidence=[_evidence(manifest, _node(manifest, "return"), state=NON_OPERATIONAL,
                                          kind=ATTEMPTED_TRANSITION, attempt="attempt-2")],
        )["incident_notifications"]
        self.assertNotEqual(first[0]["idempotency_key"], other[0]["idempotency_key"])

    def test_exact_manifest_and_qualification_lineage(self):
        manifest = _draft()
        ready = _qualify(manifest, _all_ready(manifest))
        require_ready_qualification(manifest, ready)
        other = _draft(source_output_id="another-output")
        with self.assertRaisesRegex(ValueError, "READINESS_QUALIFICATION_MANIFEST_DIGEST_MISMATCH"):
            require_ready_qualification(other, ready)
        not_ready = _qualify(manifest)
        with self.assertRaisesRegex(ValueError, "MANIFEST_NOT_READY"):
            require_ready_qualification(manifest, not_ready)
        forged = dict(not_ready, qualification=QUALIFIED_READY, executable=True)
        with self.assertRaisesRegex(ValueError, "READINESS_QUALIFICATION_DIGEST_MISMATCH"):
            require_ready_qualification(manifest, forged)

    def test_evidence_cannot_be_reused_for_changed_manifest_semantics(self):
        manifest = _draft()
        evidence = _all_ready(manifest)
        self.assertEqual(_qualify(manifest, evidence)["qualification"], QUALIFIED_READY)
        changes = {
            "requested_consequence": "a different consequence",
            "declared_intent": "a different intent",
            "source_instance": "a different initiator instance",
            "return_projection": {"depth": "result-only"},
            "extensions": {**manifest["extensions"], "authority_context": {"claim_ref": "different-claim"}},
        }
        for field, value in changes.items():
            with self.subTest(field=field):
                changed = copy.deepcopy(manifest)
                changed[field] = value
                q = _qualify(changed, evidence)
                self.assertEqual(q["qualification"], NOT_READY)
                self.assertTrue(q["failing_nodes"])
                self.assertEqual({n["failed_predicate"] for n in q["failing_nodes"]}, {"EVIDENCE_INVOCATION_BOUND"})
                self.assertEqual(_qualify(changed, _all_ready(changed))["qualification"], QUALIFIED_READY)

    def test_explicit_user_approved_degraded_fallback(self):
        kwargs = _build_kwargs()
        manifest = build_manifest(**kwargs)
        alt_evidence = _all_ready(manifest, CUSTOMER_LOCAL_GOVERNANCE_ROUTE_ID)
        result = qualify_draft_manifest(
            manifest, attempt_id=ATTEMPT, readiness_evidence=alt_evidence, evidence_verifier=VERIFY, now=NOW,
        )
        self.assertIs(result["executable"], False)
        workarounds = result["qualification"]["workarounds"]
        self.assertEqual(workarounds["state"], "VERIFIED_WORKAROUND_AVAILABLE")
        (candidate,) = workarounds["candidates"]
        self.assertEqual(candidate["candidate_state"], "VERIFIED_REQUIRES_USER_SELECTION")
        self.assertTrue(candidate["semantics_changed"])
        self.assertIn("custody:ORGANIZATION_LEDGER_CUSTODY->CUSTOMER_CONTROLLED_CUSTODY", candidate["degraded_functions"])
        selection = {
            "explicit": True,
            "selected_by": "user:fixture",
            "selected_route_id": CUSTOMER_LOCAL_GOVERNANCE_ROUTE_ID,
            "original_manifest_sha256": result["draft_manifest_sha256"],
            "acknowledged_degraded_functions": candidate["degraded_functions"],
        }
        select = dict(build_kwargs=kwargs, attempt_id=ATTEMPT, readiness_evidence=alt_evidence,
                      evidence_verifier=VERIFY, now=NOW)
        for bad in ({**selection, "explicit": False},
                    {**selection, "acknowledged_degraded_functions": candidate["degraded_functions"][:1]},
                    {**selection, "original_manifest_sha256": "0" * 64}):
            with self.assertRaisesRegex(ValueError, "EXPLICIT_USER_SELECTION_REQUIRED"):
                apply_workaround_selection(result, route_id=CUSTOMER_LOCAL_GOVERNANCE_ROUTE_ID, user_selection=bad, **select)
        with self.assertRaisesRegex(ValueError, "WORKAROUND_NOT_VERIFIED"):
            apply_workaround_selection(result, route_id="fixture.unknown", user_selection=selection, **select)
        chosen = apply_workaround_selection(
            result, route_id=CUSTOMER_LOCAL_GOVERNANCE_ROUTE_ID, user_selection=selection, **select,
        )
        self.assertNotEqual(chosen["draft_manifest_sha256"], result["draft_manifest_sha256"])
        self.assertEqual(chosen["draft_manifest"]["processing"]["route_id"], CUSTOMER_LOCAL_GOVERNANCE_ROUTE_ID)
        bound = chosen["draft_manifest"]["extensions"][WORKAROUND_SELECTION_EXTENSION]
        self.assertEqual(bound["supersedes_manifest_sha256"], result["draft_manifest_sha256"])
        self.assertIs(bound["automatic"], False)
        # Evidence for the original draft's candidate route is not evidence for
        # the newly selected manifest, which binds the explicit user decision.
        self.assertEqual(chosen["qualification"]["qualification"], NOT_READY)
        self.assertEqual({n["failed_predicate"] for n in chosen["qualification"]["failing_nodes"]},
                         {"EVIDENCE_INVOCATION_BOUND"})
        fresh = qualify_draft_manifest(
            chosen["draft_manifest"], attempt_id=ATTEMPT,
            readiness_evidence=_all_ready(chosen["draft_manifest"]), evidence_verifier=VERIFY, now=NOW,
        )
        self.assertEqual(fresh["qualification"]["qualification"], QUALIFIED_READY)
        self.assertEqual(chosen["qualification"]["manifest_sha256"], chosen["draft_manifest_sha256"])
        self.assertEqual(
            build_manifest(**_build_kwargs(execution_profile=LOCAL_CONFORMANCE))["processing"]["route_id"],
            CUSTOMER_LOCAL_GOVERNANCE_ROUTE_ID,
        )

    def test_recovered_component_with_fresh_evidence(self):
        manifest = _draft()
        old = _evidence(manifest, _node(manifest, "processor"), state=NON_OPERATIONAL,
                        kind=ATTEMPTED_TRANSITION, at=NOW - timedelta(seconds=200))
        rest = _all_ready(manifest, skip={"processor"})
        self.assertEqual(_qualify(manifest, rest + [old])["qualification"], NOT_READY)
        recovered = _evidence(manifest, _node(manifest, "processor"), at=NOW - timedelta(seconds=5))
        q = _qualify(manifest, rest + [old, recovered])
        self.assertEqual(q["qualification"], QUALIFIED_READY)
        self.assertEqual(_state(q, "processor")["state"], READY)

    def test_no_passive_polling_or_device_discovery(self):
        manifest = _draft()
        with patch("urllib.request.urlopen", side_effect=AssertionError("no probe")), \
                patch("socket.create_connection", side_effect=AssertionError("no discovery")):
            q = _qualify(manifest)
        self.assertEqual(q["reassessment"]["trigger"], "NEW_AUTHENTICATED_EVIDENCE_OR_NEW_ATTEMPTED_TRANSITION")
        for flag in ("passive_polling", "device_discovery", "scheduled"):
            self.assertIs(q["reassessment"][flag], False)
        self.assertNotIn("WAITING", json.dumps(q))


class Cli0AReadinessGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def _write(self, name, value):
        path = Path(self.tmp.name) / name
        path.write_text(json.dumps(value), encoding="utf-8")
        return str(path)

    def _args(self):
        kwargs = _build_kwargs()
        return kwargs, [
            "governance", "--select", "0A",
            "--input", self._write("data.json", kwargs["data"]),
            "--processor-request", self._write("request.json", kwargs["processor_request"]),
            "--source-framework", kwargs["source_framework"],
            "--source-output-id", kwargs["source_output_id"],
            "--created-at", kwargs["created_at"],
            "--attempt-id", ATTEMPT,
        ]

    def _run(self, argv):
        out = io.StringIO()
        handoff = {"disposition": "ALLOW", "state": "MANIFESTED_FOR_INTERLOCK_INTR_HANDOFF"}
        with patch("stegverse.manifest_execution.execute_manifest", return_value=handoff) as execute, \
                contextlib.redirect_stdout(out):
            rc = main(argv)
        text = out.getvalue()
        return rc, json.loads(text[text.rfind("\n{\n") + 1:]), execute

    def test_not_ready_draft_is_never_dispatched(self):
        _, argv = self._args()
        rc, output, execute = self._run(argv)
        self.assertEqual(rc, 2)
        execute.assert_not_called()
        self.assertEqual(output["disposition"], "FAIL_CLOSED")
        self.assertEqual(output["failed_predicate"], "MANIFEST_READINESS_QUALIFIED")
        self.assertIs(output["executable"], False)
        self.assertIs(output["draft_preserved"], True)
        self.assertEqual(output["manifest"]["processing"]["route_id"], CANONICAL_PRODUCTION_ROUTE_ID)
        self.assertTrue(output["evidence"]["failing_nodes"])

    def test_ready_draft_reaches_canonical_entrypoint(self):
        kwargs, argv = self._args()
        manifest = build_manifest(**kwargs)
        fresh = datetime.now(timezone.utc) - timedelta(seconds=5)
        evidence = _all_ready(manifest, at=fresh)
        argv += ["--readiness-evidence", self._write("evidence.json", evidence),
                 "--readiness-keys", self._write("keys.json", {KEY_ID: KEY})]
        rc, output, execute = self._run(argv)
        self.assertEqual(rc, 0)
        execute.assert_called_once()
        self.assertIs(output["executable"], True)
        self.assertEqual(output["readiness_qualification"]["qualification"], QUALIFIED_READY)
        self.assertIs(output["readiness_qualification"]["runtime_allow_claimed"], False)

    def test_evidence_without_trust_root_is_not_ready(self):
        kwargs, argv = self._args()
        manifest = build_manifest(**kwargs)
        evidence = _all_ready(manifest, at=datetime.now(timezone.utc) - timedelta(seconds=5))
        rc, output, execute = self._run(argv + ["--readiness-evidence", self._write("e.json", evidence)])
        self.assertEqual(rc, 2)
        execute.assert_not_called()
        predicates = {n["failed_predicate"] for n in output["evidence"]["failing_nodes"]}
        self.assertEqual(predicates, {"EVIDENCE_AUTHENTICATED"})


if __name__ == "__main__":
    unittest.main()
