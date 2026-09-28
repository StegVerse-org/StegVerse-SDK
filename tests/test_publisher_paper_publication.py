from __future__ import annotations
from copy import deepcopy
import hashlib
import unittest

from stegverse.governance_navigation import canonical_sha256
from stegverse.security_posture_request import build_security_posture_request
from stegverse.publisher_paper_publication import (
    TASK_ID,
    TARGET_REPOSITORY,
    PROFILE,
    prepare_publisher_paper_manifest,
    publisher_paper_governance_candidate,
    validate_publisher_paper_candidate,
)
from stegverse.wiki_publication_transition import ACTIVE_TARGET_PROFILES


SOURCE = b"# Source-only Publisher fixture"


def candidate():
    return {
        "schema": PROFILE,
        "goal_task_id": TASK_ID,
        "target_repository": TARGET_REPOSITORY,
        "target_path": "papers/test-fixture.md",
        "source_commit_sha": "1" * 40,
        "source_sha256": hashlib.sha256(SOURCE).hexdigest(),
        "source_git_blob_sha": hashlib.sha1(b"blob " + str(len(SOURCE)).encode() + bytes([0]) + SOURCE).hexdigest(),
        "editorial_owner_approved": True,
        "review_policy": {
            "mode": "RESEARCH_PUBLICATION_WITH_DISCLOSED_UNVERIFIED_EXTERNAL_REVIEW",
            "policy_ref": "GCAT-BCAT-Engine/Publisher:docs/ENTITY_ECONOMY_VOLUME_III_INDEPENDENT_REVIEW_PACKET.md#2026-09-28-owner-policy-disposition",
            "external_review_claimed": False,
            "owner_attested_convergence": True,
            "economics_report_sha256": None,
            "legal_report_sha256": None,
        },
        "publication_executed": False,
        "authority_effect": "NONE",
    }


def request(c):
    return {
        "candidate": publisher_paper_governance_candidate(c),
        "judgment": {"refusal_available": True},
        "signal": {"admitted_signal_refs": []},
        "execution": {
            "actor_authority_current": False,
            "policy_current": False,
            "delegation_current": False,
        },
        "capability": {"allowed": False},
        "continuity": {"required": True},
        "approval": {"required": True},
        "permission_present": False,
    }


def posture():
    return build_security_posture_request(
        task_id=TASK_ID,
        selection_present=False,
        organization_minimum_tier="SECURE",
        data_class=PROFILE,
        channel="publisher-papers",
    )


class PublisherPaperManifestTests(unittest.TestCase):
    def test_exact_source_and_caller_governance_manifest_is_non_authorizing(self):
        c = candidate()
        m = prepare_publisher_paper_manifest(
            candidate=c, source_bytes=SOURCE, governance_request=request(c),
            security_posture_request=posture(), created_at="2026-09-27T00:00:00Z",
        )
        self.assertEqual(m["hashes"]["payload_sha256"], canonical_sha256(m["payload"]))
        self.assertEqual(m["completion"]["egress"]["destination_profile"], TARGET_REPOSITORY)
        self.assertTrue(m["completion"]["publisher"]["required"])
        self.assertEqual(m["extensions"]["security_posture_request"]["task_id"], TASK_ID)
        self.assertFalse(m["payload"]["candidate"]["publication_executed"])
        self.assertNotIn(TARGET_REPOSITORY, [v["repository"] for v in ACTIVE_TARGET_PROFILES.values()])
    def test_owner_policy_allows_research_release_without_fabricated_review_hashes(self):
        c = candidate()
        checked = validate_publisher_paper_candidate(c, source_bytes=SOURCE)
        self.assertFalse(checked["review_policy"]["external_review_claimed"])
        self.assertIsNone(checked["review_policy"]["economics_report_sha256"])
    def test_policy_may_not_claim_unverified_external_review(self):
        c = candidate()
        c["review_policy"]["external_review_claimed"] = True
        with self.assertRaisesRegex(ValueError, "claim_boundary_invalid"):
            validate_publisher_paper_candidate(c, source_bytes=SOURCE)
    def test_tampered_source_fails_closed(self):
        c = candidate()
        with self.assertRaisesRegex(ValueError, "source_sha256_mismatch"):
            validate_publisher_paper_candidate(c, source_bytes=SOURCE+b"tampered")
    def test_wrong_git_blob_fails_closed(self):
        c = candidate()
        c["source_git_blob_sha"] = "0" * 40
        with self.assertRaisesRegex(ValueError, "git_blob_sha_mismatch"):
            validate_publisher_paper_candidate(c, source_bytes=SOURCE)
    def test_wiki_target_and_path_traversal_rejected(self):
        for target, path in [("StegVerse-Labs/admissibility-wiki","papers/test.md"),(TARGET_REPOSITORY,"papers/../secret")]:
            c = candidate()
            c["target_repository"], c["target_path"] = target,path
            with self.assertRaises(ValueError):
                validate_publisher_paper_candidate(c, source_bytes=SOURCE)
    def test_unapproved_and_published_candidate_rejected(self):
        for field, value in (("editorial_owner_approved",False),("publication_executed",True),("authority_effect","ALLOW")):
            c = candidate()
            c[field] = value
            with self.assertRaises(ValueError):
                validate_publisher_paper_candidate(c, source_bytes=SOURCE)
    def test_wrong_posture_or_governance_binding_fails_closed(self):
        c = candidate()
        bad = request(c)
        bad["candidate"]["target"] = "StegVerse-Labs/admissibility-wiki:docs/test"
        with self.assertRaisesRegex(ValueError,"exact_binding_mismatch"):
            prepare_publisher_paper_manifest(candidate=c,source_bytes=SOURCE,governance_request=bad,security_posture_request=posture())
        p=posture()
        p["task_id"]="GOVERNED-WIKI-PUBLICATION-TRANSITION-001"
        with self.assertRaisesRegex(ValueError,"posture_task_binding_mismatch"):
            prepare_publisher_paper_manifest(candidate=c,source_bytes=SOURCE,governance_request=request(c),security_posture_request=p)
if __name__=="__main__":
    unittest.main()
