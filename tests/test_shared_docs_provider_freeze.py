from __future__ import annotations

import unittest

from stegverse.shared_docs_freeze import FROZEN, REVIEW_OPEN, create_revision, freeze_revision
from stegverse.shared_docs_provider_freeze import (
    SharedDocsProviderFreezeError,
    bind_provider_revision,
    create_provider_observation,
    project_freeze_metadata,
    provider_observation_from_active_probe,
    successor_from_admitted_provider_edit,
    validate_provider_observation,
)


REVIEWERS = [
    {"reviewer_id": "mir", "reviewer_role": "HISTORY_CUSTODIAN"},
    {"reviewer_id": "stegverse", "reviewer_role": "GOVERNANCE_OWNER"},
]


def digest(char: str) -> str:
    return "sha256:" + char * 64


def base_revision():
    revision = create_revision(
        document_id="doc:shared:001",
        revision_id="rev:001",
        review_epoch="epoch:001",
        content=b"alpha",
        eligible_reviewers=REVIEWERS,
        created_at="2026-09-11T15:00:00Z",
    )
    first = freeze_revision(revision, reviewer_id="mir", frozen_at="2026-09-11T15:01:00Z")
    return freeze_revision(first, reviewer_id="stegverse", frozen_at="2026-09-11T15:02:00Z")


def observation_for(revision, *, version="provider-v1", content_digest=None):
    return create_provider_observation(
        provider="GOOGLE_DRIVE",
        provider_document_id="drive-file-001",
        provider_version_id=version,
        content_digest=content_digest or revision["content_digest"],
        observed_at="2026-09-11T15:03:00Z",
        observation_ref="tvc:provider-observation:001",
    )


def active_probe_for(revision, *, include_content=True):
    probe = {
        "provider": "google_drive",
        "provider_file_id": "drive-file-001",
        "provider_version_id": "42",
        "observed_at": "2026-09-11T15:03:00Z",
        "evidence_ref": "tvc:google-drive:request:receipt",
        "credential_authority": "TV/TVC",
        "provider_operation_authority_transferred": False,
    }
    if include_content:
        probe["provider_content_sha256"] = revision["content_digest"]
    return probe


class SharedDocsProviderFreezeTests(unittest.TestCase):
    def test_provider_observation_is_deterministic_and_evidence_only(self):
        revision = base_revision()
        first = observation_for(revision)
        second = observation_for(revision)
        self.assertEqual(first, second)
        self.assertFalse(first["provider_mutation_performed"])
        self.assertEqual(first["provider_authority"], "TV/TVC")
        self.assertEqual(validate_provider_observation(first), first)

    def test_provider_version_binds_to_exact_immutable_revision_digest(self):
        revision = base_revision()
        binding = bind_provider_revision(revision, observation_for(revision))
        self.assertEqual(binding["document_id"], revision["document_id"])
        self.assertEqual(binding["revision_id"], revision["revision_id"])
        self.assertEqual(binding["content_digest"], revision["content_digest"])
        self.assertEqual(binding["provider_version_id"], "provider-v1")
        self.assertEqual(binding["provider_authority"], "TV/TVC")
        self.assertEqual(binding["transition_authority"], "Interlock/InTr")

    def test_tvc_backed_active_probe_materializes_exact_provider_observation(self):
        revision = base_revision()
        observation = provider_observation_from_active_probe(active_probe_for(revision))
        self.assertEqual(observation["provider"], "GOOGLE_DRIVE")
        self.assertEqual(observation["provider_document_id"], "drive-file-001")
        self.assertEqual(observation["provider_version_id"], "42")
        self.assertEqual(observation["content_digest"], revision["content_digest"])
        binding = bind_provider_revision(revision, observation)
        self.assertEqual(binding["revision_id"], revision["revision_id"])

    def test_tvc_backed_metadata_without_content_sha_cannot_be_promoted_to_freeze_binding(self):
        revision = base_revision()
        with self.assertRaisesRegex(
            SharedDocsProviderFreezeError,
            "content SHA-256 unavailable",
        ):
            provider_observation_from_active_probe(active_probe_for(revision, include_content=False))

    def test_provider_digest_mismatch_fails_closed(self):
        revision = base_revision()
        bad = observation_for(revision, content_digest=digest("0"))
        with self.assertRaisesRegex(SharedDocsProviderFreezeError, "content digest does not match"):
            bind_provider_revision(revision, bad)

    def test_freeze_projection_never_mutates_reviewed_bytes_or_writes_provider(self):
        revision = base_revision()
        binding = bind_provider_revision(revision, observation_for(revision))
        projection = project_freeze_metadata(revision, binding)
        self.assertEqual(projection["freeze_state"], FROZEN)
        self.assertFalse(projection["reviewed_bytes_mutated"])
        self.assertFalse(projection["provider_write_performed"])
        self.assertEqual(projection["content_digest"], revision["content_digest"])

    def test_admitted_provider_edit_creates_unfrozen_successor_and_preserves_prior(self):
        revision = base_revision()
        binding = bind_provider_revision(revision, observation_for(revision))
        next_observation = observation_for(
            revision,
            version="provider-v2",
            content_digest=digest("1"),
        )
        prior, current, new_binding = successor_from_admitted_provider_edit(
            revision,
            binding,
            next_observation,
            new_revision_id="rev:002",
            new_review_epoch="epoch:002",
            created_at="2026-09-11T15:05:00Z",
            admitted_transition_ref="intr:admitted:provider-edit:001",
        )
        self.assertEqual(prior["freeze_state"], FROZEN)
        self.assertEqual(len(prior["freeze_receipts"]), 2)
        self.assertEqual(current["freeze_state"], REVIEW_OPEN)
        self.assertEqual(current["freeze_receipts"], [])
        self.assertEqual(current["content_digest"], digest("1"))
        self.assertEqual(current["supersedes_revision_id"], revision["revision_id"])
        self.assertEqual(new_binding["revision_id"], "rev:002")
        self.assertEqual(new_binding["provider_version_id"], "provider-v2")

    def test_provider_edit_requires_interlock_transition_reference(self):
        revision = base_revision()
        binding = bind_provider_revision(revision, observation_for(revision))
        next_observation = observation_for(revision, version="provider-v2", content_digest=digest("2"))
        with self.assertRaisesRegex(SharedDocsProviderFreezeError, "transition reference required"):
            successor_from_admitted_provider_edit(
                revision,
                binding,
                next_observation,
                new_revision_id="rev:002",
                new_review_epoch="epoch:002",
                created_at="2026-09-11T15:05:00Z",
                admitted_transition_ref="",
            )

    def test_same_provider_version_cannot_be_replayed_as_successor(self):
        revision = base_revision()
        binding = bind_provider_revision(revision, observation_for(revision))
        replay = observation_for(revision, version="provider-v1", content_digest=digest("3"))
        with self.assertRaisesRegex(SharedDocsProviderFreezeError, "version did not advance"):
            successor_from_admitted_provider_edit(
                revision,
                binding,
                replay,
                new_revision_id="rev:002",
                new_review_epoch="epoch:002",
                created_at="2026-09-11T15:05:00Z",
                admitted_transition_ref="intr:admitted:provider-edit:001",
            )

    def test_provider_document_identity_change_is_rejected(self):
        revision = base_revision()
        binding = bind_provider_revision(revision, observation_for(revision))
        changed = create_provider_observation(
            provider="GOOGLE_DRIVE",
            provider_document_id="other-file",
            provider_version_id="provider-v2",
            content_digest=digest("4"),
            observed_at="2026-09-11T15:04:00Z",
            observation_ref="tvc:provider-observation:002",
        )
        with self.assertRaisesRegex(SharedDocsProviderFreezeError, "document identity changed"):
            successor_from_admitted_provider_edit(
                revision,
                binding,
                changed,
                new_revision_id="rev:002",
                new_review_epoch="epoch:002",
                created_at="2026-09-11T15:05:00Z",
                admitted_transition_ref="intr:admitted:provider-edit:001",
            )


if __name__ == "__main__":
    unittest.main()
