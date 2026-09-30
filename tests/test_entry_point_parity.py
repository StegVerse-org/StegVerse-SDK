"""Chat equates to a console entry, or the gap is declared.

Granular control belongs to the entry point. If Chat cannot reach a console
capability, someone using Chat gives up an ability — and the ones that matter
most are replay and reconstruction, because they are how a result is verified
rather than trusted. The evaluator for Tests 1-3 was iPhone-only and needed
another operator to drive the console; this gate exists so that cannot recur
silently.

The parity map is a set of claims. These tests exercise the Chat entry contract
itself, so a claim that Chat reaches a capability fails here when it does not.

Non-authorizing: request validation only. Nothing is submitted, replayed or
reconstructed.
"""
from __future__ import annotations

import hashlib
import json
import unittest

from stegverse.ecosystem_chat_entry import (
    ASK,
    COMPOSE,
    OPERATIONS,
    RECONSTRUCT,
    REPLAY,
    SCHEMA,
    SUBMIT_MANIFEST,
    SUBMIT_RAW,
    VERIFICATION_FIELDS,
    console_equivalent_request,
    validate_chat_entry,
)
from stegverse.entry_point_parity import (
    AVAILABLE,
    NODE_REGISTRATION_REQUIRED,
    CANONICAL_TASK_ID,
    CONTRACT_ONLY,
    PROSE_PROHIBITION,
    PROSE_RETENTION_STORAGE,
    CHAT_CAPABILITIES,
    DECLARED_GAP,
    DECLARED_GAPS,
    GAP_REQUIRED_FIELDS,
    _expired,
    reconcile_entry_point_parity,
)

RECEIPT_ID = "MR-A1B2C3D4E5F60718"


def _component(branch: str, provider: str, model: str) -> dict:
    marker = f"MARKER-{branch}"
    result = {
        "schema": "stegbrowser.llm-profile-result.v1",
        "profile": "llm.v1",
        "request_commitment": f"sha256:{branch * 8}",
        "response_marker": marker,
        "provider": provider,
        "model": model,
        "response_text": f"One answer. {marker}",
        "journey_id": f"FAN-PARITY:{branch}",
    }
    result["response_commitment"] = _sha256(result)
    return result


def _sha256(value) -> str:
    data = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "sha256:" + hashlib.sha256(data.encode("utf-8")).hexdigest()


COMPOSITION_COMPONENTS = (
    _component("b0", "anthropic", "claude-opus"),
    _component("b1", "openai", "gpt"),
)


def _ask_branch(branch_id: str, out: str, ret: str) -> dict:
    return {
        "branch_id": branch_id,
        "ephemeral_endpoint": f"stegbrowser:ephemeral:{branch_id}",
        "outbound_manifest_sha256": out,
        "return_manifest_sha256": ret,
        "return_predecessor_manifest_sha256": out,
        "provider": "credential-free",
        "model": f"model-{branch_id}",
        "response_marker": f"MARKER-{branch_id}",
        "secure_url": f"https://{branch_id}.example.test/chat",
    }


ASK_JOURNEY = {
    "schema": "stegverse.packet-carried-endpoint-receipt-journey/v2",
    "journey_id": "parity-ask",
    "origin_endpoint": "stegverse:ecosystem-chat",
    "branches": [
        _ask_branch("b0", f"sha256:{'a' * 64}", f"sha256:{'b' * 64}"),
        _ask_branch("b1", f"sha256:{'c' * 64}", f"sha256:{'d' * 64}"),
    ],
}


def entry(operation, **extra):
    payload = {"schema": SCHEMA, "operation": operation}
    if operation == SUBMIT_RAW:
        payload.update(user_request="verify my claim", declared_goal="obtain a governed result")
    elif operation == SUBMIT_MANIFEST:
        payload["manifest"] = {"manifest_profile": "stegverse.ingress-manifest.v1"}
    elif operation == ASK:
        payload.update(question="what does the ecosystem govern?", journey=ASK_JOURNEY)
    elif operation == COMPOSE:
        payload.update(
            composition_id="CMP-PARITY-1",
            fan_journey_id="FAN-PARITY",
            components=list(COMPOSITION_COMPONENTS),
        )
    else:
        payload["manifest_receipt_id"] = RECEIPT_ID
    payload.update(extra)
    return validate_chat_entry(payload)


class EntryPointParityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.report = reconcile_entry_point_parity()

    # --- the map may not claim what the contract does not carry -------------

    def test_every_capability_claimed_at_chat_is_actually_reachable(self) -> None:
        """The claim is exercised, not trusted."""
        reachable = {e["capability"] for e in
                     (entry(op) for op in OPERATIONS)}
        # Projection and label control are carried on every operation.
        sample = entry(SUBMIT_RAW)
        if sample.get("return_projection"):
            reachable.add("RETURN_PROJECTION_CONTROL")
        if sample.get("manifest_labels"):
            reachable.add("MANIFEST_LABEL_CONTROL")
        self.assertEqual(
            set(CHAT_CAPABILITIES) - reachable, set(),
            "the parity map claims a capability the Chat entry contract does not carry",
        )

    def test_no_console_capability_drifts_out_of_reach_undeclared(self) -> None:
        drift = [r for r in self.report["rows"] if r["disposition"] not in
                 {AVAILABLE, DECLARED_GAP}]
        self.assertEqual(self.report["drift_count"], 0, f"undeclared gap: {drift}")

    def test_verification_is_never_an_acceptable_gap(self) -> None:
        """Submitting without being able to verify is the failure this prevents."""
        self.assertEqual(
            sorted(self.report["verification_capabilities"]),
            ["ASK_GOVERNED_QUESTION", "COMPOSE_GOVERNED_RESPONSE",
             "RECONSTRUCT_BY_RECEIPT_LOCATOR", "REPLAY_BY_RECEIPT_LOCATOR"],
        )
        for row in self.report["rows"]:
            if row["verification_capability"]:
                # A verification capability may be contract-carried while the
                # surface catches up, or wait on MyKV continuity, but it may
                # never be a declared gap.
                self.assertIn(row["disposition"], {AVAILABLE, CONTRACT_ONLY},
                              row["capability"])

    def test_a_phone_can_verify_at_least_one_result_on_the_surface(self) -> None:
        """The original failure was a Chat user who could submit but not check."""
        self.assertTrue(self.report["verification_available_at_chat"])
        self.assertIn("ASK_GOVERNED_QUESTION",
                      self.report["verification_served_by_surface"])

    def test_the_report_follows_the_postures_rather_than_a_hardcoded_answer(self) -> None:
        """Dropping the prohibition from a posture must change what is reported."""
        import stegverse.entry_point_parity as parity
        from stegverse.security_posture import POSTURES

        declaring = [pid for pid, p in POSTURES.items()
                     if (p.get("prohibitions") or {}).get(PROSE_PROHIBITION)]
        self.assertTrue(declaring, "no posture declares the prohibition")
        target = declaring[0]
        original = POSTURES[target]["prohibitions"][PROSE_PROHIBITION]
        POSTURES[target]["prohibitions"][PROSE_PROHIBITION] = False
        try:
            report = parity.reconcile_entry_point_parity()
            self.assertIn(target, report["postures_not_declaring_prose_prohibition"])
            self.assertNotIn(target, report["postures_prohibiting_prose"])
        finally:
            POSTURES[target]["prohibitions"][PROSE_PROHIBITION] = original
        restored = parity.reconcile_entry_point_parity()
        self.assertIn(target, restored["postures_prohibiting_prose"])

    def test_where_the_prose_prohibition_is_declared_is_reported_not_assumed(self) -> None:
        """It is declared at HIGH and HIGHEST but not at SECURE.

        Collapsing that into "prohibited everywhere" would be a broader claim
        than the postures support, so the report names both sets.
        """
        report = self.report
        self.assertEqual(report["prose_prohibited_by"], PROSE_PROHIBITION)
        prohibiting = set(report["postures_prohibiting_prose"])
        missing = set(report["postures_not_declaring_prose_prohibition"])
        self.assertTrue(prohibiting)
        self.assertFalse(prohibiting & missing)
        self.assertEqual(
            prohibiting | missing, set(report["prose_prohibition_by_posture"]))

    def test_replay_verifies_transitions_and_decisions_not_prose(self) -> None:
        """What a receipt locator establishes, stated rather than assumed.

        Replay and reconstruction display the state transition path and make the
        decision verifiable from the Ecosystem. Neither returns the question or
        answer text. Reading them as "get my conversation back" would be wrong.
        """
        self.assertEqual(
            sorted(self.report["capabilities_verifying_transitions"]),
            ["RECONSTRUCT_BY_RECEIPT_LOCATOR", "REPLAY_BY_RECEIPT_LOCATOR"],
        )
        for row in self.report["rows"]:
            if row["verifies"]:
                self.assertEqual(
                    sorted(row["verifies"]), ["DECISION", "STATE_TRANSITION_PATH"])
                self.assertFalse(row["retains_prose"], row["capability"])

    def test_the_ecosystem_retains_no_prose_and_says_where_it_lives(self) -> None:
        """Retaining query and response text needs user-based storage, not the
        Ecosystem. That is MyKV, and chat continuity depends on it.

        The prohibition is pre-existing: every declared posture already forbids
        raw sensitive data in an audit receipt. This reads that rather than
        asserting it independently.
        """
        self.assertEqual(self.report["capabilities_retaining_prose"], [])
        self.assertEqual(self.report["capabilities_retaining_prose"], [])
        self.assertEqual(self.report["prose_retention_storage"], PROSE_RETENTION_STORAGE)
        self.assertEqual(self.report["chat_continuity_requires"], PROSE_RETENTION_STORAGE)

    def test_contract_carried_but_unserved_capabilities_are_counted_not_hidden(self) -> None:
        """The map once read green while the surface served no operation at all."""
        contract_only = self.report["contract_only_capabilities"]
        self.assertEqual(self.report["contract_only_count"], len(contract_only))
        served = set(self.report["served_by_chat_surface"])
        self.assertTrue(served)
        self.assertFalse(served & set(contract_only))
        for row in self.report["rows"]:
            if row["disposition"] == CONTRACT_ONLY:
                self.assertTrue(row["carried_by_chat_contract"])
                self.assertFalse(row["served_by_chat_surface"])

    # --- transportability is a node capability, never a device property -----

    def test_no_capability_is_ever_gated_on_a_device(self) -> None:
        """A device is interchangeable; gating on device identity is prohibited."""
        for row in self.report["rows"]:
            with self.subTest(capability=row["capability"]):
                self.assertEqual(row["device_identity_gate"], "NONE_PROHIBITED")
        self.assertIs(self.report["transportability_conferred_by_device"], False)
        self.assertEqual(self.report["transportability_conferred_by"], "NODE_REGISTRATION")

    def test_a_transport_capability_is_conditioned_on_node_registration(self) -> None:
        for row in self.report["rows"]:
            with self.subTest(capability=row["capability"]):
                expected = NODE_REGISTRATION_REQUIRED if row["requires_transportability"] else "NONE"
                self.assertEqual(row["precondition"], expected)

    def test_moving_data_requires_transportability_and_shaping_a_request_does_not(self) -> None:
        """Submission and verification cross to custody; projection and labels shape a return."""
        self.assertEqual(
            sorted(self.report["requires_transportability"]),
            ["ASK_GOVERNED_QUESTION", "COMPOSE_GOVERNED_RESPONSE",
             "RECONSTRUCT_BY_RECEIPT_LOCATOR", "REPLAY_BY_RECEIPT_LOCATOR",
             "SUBMIT_PREFORMATTED_MANIFEST", "SUBMIT_RAW_USER_DATA"],
        )
        self.assertEqual(
            sorted(self.report["available_without_node_registration"]),
            [],  # both shaping capabilities are contract-carried, not yet served
        )

    def test_registration_confers_transportability_and_no_authority(self) -> None:
        """A node moves data; user verification stays exclusively with KV/SKAP."""
        self.assertIs(self.report["node_confers_user_verifier_authority"], False)
        self.assertIs(self.report["grants_execution_authority"], False)

    # --- gaps are granted, and they expire ----------------------------------

    def test_every_gap_is_actionable_and_granted_against_an_existing_goal(self) -> None:
        for name, gap in DECLARED_GAPS.items():
            with self.subTest(gap=name):
                for field in GAP_REQUIRED_FIELDS:
                    self.assertTrue(str(gap.get(field, "")).strip(), f"{name} missing {field}")
                goal = gap["owning_existing_goal"]
                self.assertRegex(goal, CANONICAL_TASK_ID)
                self.assertIn(goal, gap["granted_by"], "a gap may not grant itself")
                self.assertIsInstance(gap["observed_registry_generation"], int)

    def test_no_gap_has_outlived_its_review_date(self) -> None:
        self.assertEqual(self.report["expired_gap_count"], 0)

    def test_a_malformed_review_date_counts_as_expired(self) -> None:
        from datetime import date
        self.assertTrue(_expired("2026-01-01", today=date(2026, 9, 29)))
        self.assertFalse(_expired("2026-12-31", today=date(2026, 9, 29)))
        self.assertTrue(_expired(None))

    # --- the contract itself -------------------------------------------------

    def test_chat_interfaces_with_the_builder_rather_than_building(self) -> None:
        for operation in (SUBMIT_RAW, SUBMIT_MANIFEST):
            with self.subTest(operation=operation):
                row = entry(operation)
                self.assertIs(row["chat_builds_manifest"], False)
                self.assertIs(row["builder_directive"]["manifest_constructed_by_chat"], False)
                self.assertTrue(row["builder_directive"]["builder"])

    def test_a_verification_names_the_fields_a_person_compares(self) -> None:
        for operation in (REPLAY, RECONSTRUCT):
            with self.subTest(operation=operation):
                verification = entry(operation)["verification"]
                self.assertEqual(tuple(verification["compare_fields"]), VERIFICATION_FIELDS)
                self.assertIn("receipt_sha256", verification["verified_when"])
                self.assertIs(verification["consequence_reexecuted_expected"], False)
                self.assertIs(verification["legible_without_a_console"], True)

    def test_a_receipt_locator_is_canonicalized_and_a_bad_one_is_rejected(self) -> None:
        self.assertEqual(entry(REPLAY, manifest_receipt_id=RECEIPT_ID.lower())["manifest_receipt_id"],
                         RECEIPT_ID)
        for bad in ("mr-2f8a", "MR-ZZZZZZZZZZZZZZZZ", "", "A1B2C3D4E5F60718"):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                entry(REPLAY, manifest_receipt_id=bad)

    def test_chat_and_console_hand_the_same_request_to_the_same_handlers(self) -> None:
        request = console_equivalent_request(entry(RECONSTRUCT))
        self.assertEqual(request["selection"], RECONSTRUCT)
        self.assertEqual(request["manifest_receipt_id"], RECEIPT_ID)
        self.assertEqual(request["originating_entry_point"], "ECOSYSTEM_CHAT")
        raw = console_equivalent_request(entry(SUBMIT_RAW))
        self.assertIn("raw_submission", raw)
        self.assertNotIn("manifest", raw, "chat does not hand over a manifest it built")

    def test_projection_controls_the_return_and_never_custody(self) -> None:
        row = entry(REPLAY, return_projection={"mode": "SELECTED",
                                               "transition_classes": ["INGRESS_ADMITTED"]})
        projection = row["return_projection"]
        self.assertEqual(projection["mode"], "SELECTED")
        self.assertIs(projection["suppresses_master_records_custody"], False)
        self.assertIs(projection["erases_ecosystem_transitions"], False)
        self.assertIs(projection["grants_authority"], False)

    def test_an_unknown_operation_and_a_bad_schema_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            validate_chat_entry({"schema": SCHEMA, "operation": "9"})
        with self.assertRaises(ValueError):
            validate_chat_entry({"schema": "something/v9", "operation": REPLAY})

    def test_the_entry_grants_no_authority(self) -> None:
        for operation in OPERATIONS:
            with self.subTest(operation=operation):
                row = entry(operation)
                self.assertIs(row["grants_execution_authority"], False)
                self.assertEqual(row["authority_effect"], "NONE_ENTRY_REQUEST_ONLY")
        self.assertIs(self.report["grants_execution_authority"], False)


if __name__ == "__main__":
    unittest.main()
