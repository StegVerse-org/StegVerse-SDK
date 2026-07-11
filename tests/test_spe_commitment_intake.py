from __future__ import annotations

import copy
import unittest

from stegverse.spe_commitment_intake import (
    build_spe_commitment_candidate,
    build_spe_intake_envelope,
)
from stegverse.transition_candidate import emit_sdk_transition_candidate


class SPECommitmentIntakeTests(unittest.TestCase):
    def _transition(self) -> dict:
        return emit_sdk_transition_candidate(
            transition_id="transition.sdk.spe.test",
            run_id="run-sdk-spe-test",
            event_id="event-sdk-spe-test",
            actor_ref="actor:test",
            target_ref="target:test",
            repository_ref="StegVerse-org/StegVerse-SDK",
            task_ref="task:spe-intake",
            handoff_ref="SDK_MIRROR_HANDOFF.md",
            policy_refs=["policy://sdk/spe-intake/v0.1"],
            evidence_refs=["evidence://sdk/candidate/001"],
        )

    def _candidate(self) -> dict:
        return build_spe_commitment_candidate(
            self._transition(),
            action="evaluate_commit_time_standing",
            bounded_scope={"repository": "StegVerse-org/StegVerse-SDK"},
            review_ref="review://sdk/spe/001",
            policy_context={"refs": ["policy://sdk/spe-intake/v0.1"]},
            delegation_context={"refs": []},
            validity_window={"not_before": None, "not_after": None},
            execution_context={"mode": "evaluation_only"},
            recoverability_profile={"reconstructable": True, "rollback_supported": False},
        )

    def test_candidate_remains_non_authorizing(self) -> None:
        candidate = self._candidate()
        self.assertFalse(candidate["authorizing"])
        self.assertFalse(candidate["inherits_review_authority"])
        self.assertFalse(candidate["implies_standing"])
        self.assertTrue(candidate["requires_fresh_standing_determination"])
        self.assertEqual(candidate["transition_id"], "transition.sdk.spe.test")
        self.assertTrue(candidate["candidate_hash"])

    def test_envelope_is_deterministic(self) -> None:
        candidate = self._candidate()
        left = build_spe_intake_envelope(candidate)
        right = build_spe_intake_envelope(copy.deepcopy(candidate))
        self.assertEqual(left["envelope_hash"], right["envelope_hash"])
        self.assertEqual(left["destination_repo"], "StegVerse-Labs/Standing-Proof-Engine")
        self.assertEqual(left["expected_result"], ["ALLOW", "DENY", "FAIL_CLOSED"])

    def test_rejects_non_declared_transition(self) -> None:
        transition = self._transition()
        transition["lifecycle_state"] = "EXECUTED"
        with self.assertRaisesRegex(ValueError, "must remain DECLARED"):
            build_spe_commitment_candidate(
                transition,
                action="evaluate_commit_time_standing",
                bounded_scope={},
                review_ref="review://sdk/spe/001",
                policy_context={},
                delegation_context={},
                validity_window={},
                execution_context={},
                recoverability_profile={},
            )


if __name__ == "__main__":
    unittest.main()
