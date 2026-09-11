from __future__ import annotations

import unittest

from stegverse.shared_docs_freeze import (
    CURRENT,
    FROZEN,
    PARTIALLY_FROZEN,
    REVIEW_OPEN,
    SUPERSEDED,
    SharedDocsFreezeError,
    content_digest,
    create_revision,
    freeze_revision,
    successor_revision,
)


REVIEWERS = [
    {"reviewer_id": "mir", "reviewer_role": "HISTORY_CUSTODIAN"},
    {"reviewer_id": "stegverse", "reviewer_role": "GOVERNANCE_OWNER"},
]


def revision():
    return create_revision(
        document_id="doc:mir-stegverse-v0.3",
        revision_id="rev:001",
        review_epoch="epoch:001",
        content="frozen candidate",
        eligible_reviewers=REVIEWERS,
        created_at="2026-09-10T23:00:00Z",
    )


class SharedDocsFreezeTests(unittest.TestCase):
    def test_first_reviewer_creates_partial_freeze(self):
        result = freeze_revision(
            revision(),
            reviewer_id="stegverse",
            frozen_at="2026-09-10T23:10:00Z",
        )
        self.assertEqual(result["freeze_state"], PARTIALLY_FROZEN)
        self.assertEqual(len(result["freeze_receipts"]), 1)

    def test_all_eligible_reviewers_freeze_exact_revision(self):
        first = freeze_revision(
            revision(), reviewer_id="stegverse", frozen_at="2026-09-10T23:10:00Z"
        )
        result = freeze_revision(first, reviewer_id="mir", frozen_at="2026-09-11T01:31:00Z")
        self.assertEqual(result["freeze_state"], FROZEN)
        self.assertEqual({r["reviewer_id"] for r in result["freeze_receipts"]}, {"mir", "stegverse"})

    def test_stale_revision_or_digest_is_rejected(self):
        source = revision()
        with self.assertRaisesRegex(SharedDocsFreezeError, "stale revision"):
            freeze_revision(
                source,
                reviewer_id="mir",
                frozen_at="2026-09-11T01:31:00Z",
                expected_revision_id="rev:000",
            )
        with self.assertRaisesRegex(SharedDocsFreezeError, "stale content digest"):
            freeze_revision(
                source,
                reviewer_id="mir",
                frozen_at="2026-09-11T01:31:00Z",
                expected_content_digest="sha256:" + "0" * 64,
            )

    def test_edit_after_freeze_creates_unfrozen_successor_and_preserves_prior(self):
        first = freeze_revision(
            revision(), reviewer_id="stegverse", frozen_at="2026-09-10T23:10:00Z"
        )
        frozen = freeze_revision(first, reviewer_id="mir", frozen_at="2026-09-11T01:31:00Z")
        prior, current = successor_revision(
            frozen,
            new_revision_id="rev:002",
            new_review_epoch="epoch:002",
            created_at="2026-09-11T02:00:00Z",
            content="changed text",
        )
        self.assertEqual(prior["revision_status"], SUPERSEDED)
        self.assertEqual(prior["freeze_state"], FROZEN)
        self.assertEqual(len(prior["freeze_receipts"]), 2)
        self.assertEqual(current["revision_status"], CURRENT)
        self.assertEqual(current["freeze_state"], REVIEW_OPEN)
        self.assertEqual(current["freeze_receipts"], [])
        self.assertNotEqual(current["content_digest"], frozen["content_digest"])

    def test_reviewer_set_change_requires_new_review_epoch_even_when_content_is_same(self):
        source = revision()
        prior, current = successor_revision(
            source,
            new_revision_id="rev:002",
            new_review_epoch="epoch:002",
            created_at="2026-09-11T02:00:00Z",
            eligible_reviewers=REVIEWERS + [{"reviewer_id": "third", "reviewer_role": "REVIEWER"}],
        )
        self.assertEqual(prior["revision_status"], SUPERSEDED)
        self.assertEqual(current["freeze_state"], REVIEW_OPEN)
        self.assertEqual(current["freeze_receipts"], [])
        self.assertEqual(current["content_digest"], source["content_digest"])
        self.assertEqual(len(current["eligible_reviewers"]), 3)

    def test_freeze_receipt_is_bound_to_exact_digest_and_epoch(self):
        source = revision()
        result = freeze_revision(
            source, reviewer_id="mir", frozen_at="2026-09-11T01:31:00Z"
        )
        receipt = result["freeze_receipts"][0]
        self.assertEqual(receipt["content_digest"], content_digest("frozen candidate"))
        self.assertEqual(receipt["revision_id"], "rev:001")
        self.assertEqual(receipt["review_epoch"], "epoch:001")
        self.assertTrue(receipt["freeze_receipt_id"].startswith("freeze:"))

    def test_ineligible_and_duplicate_reviewer_freezes_fail_closed(self):
        source = revision()
        with self.assertRaisesRegex(SharedDocsFreezeError, "not eligible"):
            freeze_revision(source, reviewer_id="outsider", frozen_at="2026-09-11T01:31:00Z")
        first = freeze_revision(source, reviewer_id="mir", frozen_at="2026-09-11T01:31:00Z")
        with self.assertRaisesRegex(SharedDocsFreezeError, "already froze"):
            freeze_revision(first, reviewer_id="mir", frozen_at="2026-09-11T01:32:00Z")


if __name__ == "__main__":
    unittest.main()
