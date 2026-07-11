from __future__ import annotations

import unittest

from stegverse.transition_candidate import emit_sdk_transition_candidate


class SDKTransitionCandidateTests(unittest.TestCase):
    def test_emits_declared_non_authorizing_candidate(self) -> None:
        record = emit_sdk_transition_candidate(
            transition_id="transition.sdk.test",
            run_id="run-sdk-test",
            event_id="event-sdk-test",
            actor_ref="actor:test",
            target_ref="bridge:hybrid-collab",
            repository_ref="StegVerse-org/StegVerse-SDK",
            task_ref="task:test",
        )
        self.assertEqual(record["origin"]["origin_class"], "SDK_INPUT")
        self.assertEqual(record["lifecycle_state"], "DECLARED")
        self.assertEqual(record["governance"]["admissibility_result"], "PENDING")
        self.assertIsNone(record["execution"]["action_ref"])
        self.assertIsNone(record["continuity"]["final_receipt_id"])
        self.assertEqual(record["continuity"]["master_record_status"], "NOT_YET_SUBMITTED")

    def test_requires_identity_fields(self) -> None:
        with self.assertRaises(ValueError):
            emit_sdk_transition_candidate(
                transition_id="",
                run_id="run",
                event_id="event",
                actor_ref="actor",
                target_ref="target",
                repository_ref="repo",
            )


if __name__ == "__main__":
    unittest.main()
