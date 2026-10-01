"""A surface that merely overlaps a frozen declaration is a different condition.

The assertion runs against what was served, not what was meant to be served,
and it holds the evidence emitter so a divergent surface cannot emit by a
caller forgetting to check first.
"""
import unittest

from stegverse.served_surface_assertion import (
    AUTHORITY_BOUNDARY,
    CONTENT_SUBSTITUTED,
    DECLARATION_ALTERED,
    DECLARED_NOT_SERVED,
    EVIDENCE_WITHHELD,
    EXTRA_SERVED,
    POST_ATTEMPT_PROVENANCE,
    SERVED_FROM_CACHE,
    SURFACE_CONFORMS,
    SURFACE_DIVERGED,
    ServedSurfaceRefused,
    assert_served_surface,
    declare_frozen_surface,
    emit_under_served_surface_assertion,
)

GOAL = "SDK-SERVED-SURFACE-ASSERTION-001"
PRIOR_LANE = "PRIOR-ATTEMPT-LANE-001"


def digest(seed: str) -> str:
    return "sha256:" + (seed * 64)[:64]


def frozen_surface(*resource_ids, excluded=(PRIOR_LANE,)):
    return declare_frozen_surface(
        [{"resource_id": rid, "content_sha256": digest(str(index + 1))}
         for index, rid in enumerate(resource_ids)],
        declaration_id="FROZEN-READ-SURFACE-001",
        excluded_provenance=excluded)


def served(*pairs, **flags):
    return [dict({"resource_id": rid, "content_sha256": content}, **flags)
            for rid, content in pairs]


def predicates(result):
    return [item["failed_predicate"] for item in result["divergences"]]


class DeclarationTest(unittest.TestCase):
    def test_declaration_is_frozen_by_its_own_digest(self):
        declaration = frozen_surface("TT", "RTG")
        self.assertTrue(declaration["declaration_is_frozen"])
        self.assertTrue(declaration["declaration_sha256"].startswith("sha256:"))
        self.assertEqual([r["resource_id"] for r in declaration["resources"]], ["RTG", "TT"])

    def test_an_empty_surface_cannot_be_declared(self):
        with self.assertRaises(ServedSurfaceRefused):
            declare_frozen_surface([], declaration_id="F-1")

    def test_a_duplicate_resource_is_refused_not_collapsed(self):
        with self.assertRaises(ServedSurfaceRefused):
            declare_frozen_surface(
                [{"resource_id": "TT", "content_sha256": digest("1")},
                 {"resource_id": "TT", "content_sha256": digest("2")}],
                declaration_id="F-1")

    def test_a_resource_without_content_is_refused(self):
        with self.assertRaises(ServedSurfaceRefused):
            declare_frozen_surface([{"resource_id": "TT"}], declaration_id="F-1")


class ConformanceTest(unittest.TestCase):
    def test_an_exactly_equal_surface_conforms(self):
        declaration = frozen_surface("TT", "RTG")
        result = assert_served_surface(
            declaration, served(("TT", digest("1")), ("RTG", digest("2"))),
            owning_existing_goal=GOAL)
        self.assertEqual(result["state"], SURFACE_CONFORMS)
        self.assertEqual(result["disposition"], "ALLOW")
        self.assertEqual(result["divergences"], [])
        self.assertNotIn("failed_predicate", result)

    def test_overlapping_surface_with_substituted_membership_fails_closed(self):
        """The divergence class that matters: the overlap looks like success.

        One declared resource is served and the rest of the surface is a
        different set entirely. Nothing errors, every resource is well-formed,
        and the condition under test has been replaced.
        """
        declaration = frozen_surface("TT", "RTG", "GTG", "AE", "SNAPSHOT")
        result = assert_served_surface(declaration, served(
            ("CONTRACT", digest("a")),
            ("ENVIRONMENT", digest("b")),
            ("SNAPSHOT", digest("5")),
            ("IDENTITY", digest("c")),
        ), owning_existing_goal=GOAL)
        self.assertEqual(result["disposition"], "FAIL_CLOSED")
        extra = [d["resource_id"] for d in result["divergences"]
                 if d["failed_predicate"] == EXTRA_SERVED]
        missing = [d["resource_id"] for d in result["divergences"]
                   if d["failed_predicate"] == DECLARED_NOT_SERVED]
        self.assertEqual(extra, ["CONTRACT", "ENVIRONMENT", "IDENTITY"])
        self.assertEqual(missing, ["AE", "GTG", "RTG", "TT"])


class DivergenceClassTest(unittest.TestCase):
    def test_extra_resource(self):
        result = assert_served_surface(
            frozen_surface("TT"),
            served(("TT", digest("1")), ("INJECTED", digest("9"))),
            owning_existing_goal=GOAL)
        self.assertEqual(predicates(result), [EXTRA_SERVED])

    def test_declared_resource_not_served(self):
        result = assert_served_surface(
            frozen_surface("TT", "RTG"), served(("TT", digest("1"))),
            owning_existing_goal=GOAL)
        self.assertEqual(predicates(result), [DECLARED_NOT_SERVED])

    def test_substituted_content_reports_both_digests(self):
        result = assert_served_surface(
            frozen_surface("TT"), served(("TT", digest("9"))),
            owning_existing_goal=GOAL)
        self.assertEqual(predicates(result), [CONTENT_SUBSTITUTED])
        entry = result["divergences"][0]
        self.assertEqual(entry["declared_content_sha256"], digest("1"))
        self.assertEqual(entry["served_content_sha256"], digest("9"))

    def test_a_cached_resource_is_divergent_even_with_matching_content(self):
        result = assert_served_surface(
            frozen_surface("TT"),
            [{"resource_id": "TT", "content_sha256": digest("1"), "cached": True}],
            owning_existing_goal=GOAL)
        self.assertEqual(predicates(result), [SERVED_FROM_CACHE])

    def test_prior_attempt_provenance_is_excluded(self):
        result = assert_served_surface(
            frozen_surface("TT"),
            [{"resource_id": "TT", "content_sha256": digest("1"),
              "provenance_refs": ["SOME-OTHER-REF", PRIOR_LANE]}],
            owning_existing_goal=GOAL)
        self.assertEqual(predicates(result), [POST_ATTEMPT_PROVENANCE])
        self.assertEqual(result["divergences"][0]["excluded_provenance_matched"], [PRIOR_LANE])

    def test_cache_and_provenance_are_checked_on_undeclared_resources_too(self):
        """A prior-attempt artifact is usually not in the declaration at all."""
        result = assert_served_surface(
            frozen_surface("TT"),
            [{"resource_id": "TT", "content_sha256": digest("1")},
             {"resource_id": "PRIOR_RECEIPT", "content_sha256": digest("9"),
              "cached": True, "provenance_refs": [PRIOR_LANE]}],
            owning_existing_goal=GOAL)
        self.assertEqual(
            sorted(set(predicates(result))),
            sorted({EXTRA_SERVED, SERVED_FROM_CACHE, POST_ATTEMPT_PROVENANCE}))

    def test_a_duplicate_served_resource_is_refused(self):
        with self.assertRaises(ServedSurfaceRefused):
            assert_served_surface(
                frozen_surface("TT"),
                served(("TT", digest("1")), ("TT", digest("1"))),
                owning_existing_goal=GOAL)


class AlteredDeclarationTest(unittest.TestCase):
    def test_an_altered_declaration_fails_before_any_comparison(self):
        declaration = dict(frozen_surface("TT"))
        declaration["excluded_provenance"] = []
        result = assert_served_surface(
            declaration, served(("TT", digest("1"))), owning_existing_goal=GOAL)
        self.assertEqual(result["disposition"], "FAIL_CLOSED")
        self.assertFalse(result["declaration_intact"])
        self.assertEqual(predicates(result), [DECLARATION_ALTERED])

    def test_an_altered_declaration_does_not_mask_itself_with_a_matching_surface(self):
        declaration = dict(frozen_surface("TT", "RTG"))
        declaration["resources"] = [{"resource_id": "TT", "content_sha256": digest("1")}]
        result = assert_served_surface(
            declaration, served(("TT", digest("1"))), owning_existing_goal=GOAL)
        self.assertEqual(predicates(result), [DECLARATION_ALTERED])


class EmissionOrderingTest(unittest.TestCase):
    def test_an_injected_extra_resource_aborts_before_evidence_is_emitted(self):
        """The acceptance criterion, asserted on the emitter rather than inferred."""
        calls = []
        result = emit_under_served_surface_assertion(
            frozen_surface("TT"),
            served(("TT", digest("1")), ("INJECTED", digest("9"))),
            owning_existing_goal=GOAL, evidence_emitter=calls.append)
        self.assertEqual(calls, [])
        self.assertFalse(result["evidence_emitted"])
        self.assertEqual(result["evidence_state"], EVIDENCE_WITHHELD)
        self.assertEqual(result["state"], SURFACE_DIVERGED)

    def test_a_conforming_surface_emits_once_and_returns_the_reference(self):
        calls = []

        def emitter(assertion):
            calls.append(assertion)
            return "EVIDENCE-REF-1"

        result = emit_under_served_surface_assertion(
            frozen_surface("TT"), served(("TT", digest("1"))),
            owning_existing_goal=GOAL, evidence_emitter=emitter)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["disposition"], "ALLOW")
        self.assertTrue(result["evidence_emitted"])
        self.assertEqual(result["evidence_reference"], "EVIDENCE-REF-1")

    def test_no_emitter_is_refused_rather_than_skipped(self):
        with self.assertRaises(ServedSurfaceRefused):
            emit_under_served_surface_assertion(
                frozen_surface("TT"), served(("TT", digest("1"))),
                owning_existing_goal=GOAL, evidence_emitter=None)


class DispositionContractTest(unittest.TestCase):
    def test_every_divergence_names_its_repair_and_owner(self):
        """ECOSYSTEM_STATE_TRANSITION_DISPOSITION_INVARIANT: no bare blocker."""
        result = assert_served_surface(
            frozen_surface("TT", "RTG"),
            [{"resource_id": "TT", "content_sha256": digest("9"), "cached": True,
              "provenance_refs": [PRIOR_LANE]},
             {"resource_id": "INJECTED", "content_sha256": digest("8")}],
            owning_existing_goal=GOAL)
        self.assertTrue(result["divergences"])
        for entry in result["divergences"]:
            with self.subTest(failed_predicate=entry["failed_predicate"]):
                for field in ("failed_predicate", "required_evidence_or_repair",
                              "retry_entrypoint", "owning_existing_goal", "disposition"):
                    self.assertTrue(entry.get(field), field)
                self.assertEqual(entry["owning_existing_goal"], GOAL)

    def test_an_owning_goal_is_required(self):
        with self.assertRaises(ServedSurfaceRefused):
            assert_served_surface(frozen_surface("TT"), served(("TT", digest("1"))),
                                  owning_existing_goal="")

    def test_comparison_claims_nothing(self):
        result = assert_served_surface(
            frozen_surface("TT"), served(("TT", digest("1"))), owning_existing_goal=GOAL)
        self.assertEqual(result["authority_boundary"], AUTHORITY_BOUNDARY)
        self.assertEqual(result["authority_effect"], "NONE_SURFACE_COMPARISON_ONLY")
        for claim, value in AUTHORITY_BOUNDARY.items():
            with self.subTest(claim=claim):
                self.assertFalse(value)


if __name__ == "__main__":
    unittest.main()
