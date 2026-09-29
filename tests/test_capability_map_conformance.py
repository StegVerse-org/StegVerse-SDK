"""Every installed route is evaluator-invocable, or carries a declared exemption.

The SDK's demo surface is the residue of its passed tests: `inspection/examples`
holds the exact fixture pairs the evaluator ran for Tests 1-5. Nothing kept that
surface in step with the route table, so routes could be published as installed
while no console command could reach them. This gate closes that: a new route
that ships without a builder binding and a working example pair fails here
rather than going quietly missing from the evaluator's view.

Non-authorizing: this validates source reconciliation and manifest construction.
It mints no receipt, admits nothing and observes no runtime.
"""
from __future__ import annotations

import json
from pathlib import Path
import unittest

from stegverse.capability_map import (
    BUILDER_BINDING_EXEMPTIONS,
    CANONICAL_TASK_ID,
    DECLARED_EXEMPTION,
    EVALUATOR_EXAMPLES,
    EVALUATOR_INVOCABLE,
    EXAMPLE_ROOT,
    EXEMPTION_BASELINE,
    EXEMPTION_REQUIRED_FIELDS,
    ROUTE_SELECTION_EXEMPTIONS,
    _expired,
    reconcile_capability_map,
)
from stegverse.manifest_builder import build_manifest

ACTIONABLE_FIELDS = EXEMPTION_REQUIRED_FIELDS


class CapabilityMapConformanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.report = reconcile_capability_map()

    def test_no_installed_route_drifts_out_of_the_evaluator_surface(self) -> None:
        drift = [r for r in self.report["rows"] if r["disposition"] not in
                 {EVALUATOR_INVOCABLE, DECLARED_EXEMPTION}]
        self.assertEqual(
            self.report["drift_count"], 0,
            "installed route is neither invocable nor exempt: "
            + json.dumps(drift, indent=2, sort_keys=True),
        )

    def test_every_declared_example_actually_builds_on_its_own_route(self) -> None:
        """The demo is the test: each declared pair is built, not merely present."""
        source = json.loads((EXAMPLE_ROOT / "sdk-tt-shared-source.json").read_text(encoding="utf-8"))
        for row in self.report["rows"]:
            if row["disposition"] != EVALUATOR_INVOCABLE:
                continue
            with self.subTest(capability=row["capability_id"]):
                request = json.loads(
                    (EXAMPLE_ROOT / row["example"]["processor_request"]).read_text(encoding="utf-8")
                )
                manifest = build_manifest(
                    data=source,
                    source_framework="external_evaluator",
                    source_output_id=f"capability-map-{row['capability_id']}",
                    processor_request=request,
                    process=row["capability_id"],
                    return_depth="full-trace",
                    created_at="2026-09-29T00:00:00Z",
                )
                self.assertEqual(manifest.get("manifest_profile"), "stegverse.ingress-manifest.v1")
                self.assertEqual(manifest["processing"]["capability"], row["capability_id"])
                self.assertEqual(manifest["processing"]["route_id"], row["route_id"])

    def test_declared_example_files_exist_and_are_json_objects(self) -> None:
        for capability, entry in EVALUATOR_EXAMPLES.items():
            with self.subTest(capability=capability):
                for path in (EXAMPLE_ROOT / entry["source"], EXAMPLE_ROOT / entry["processor_request"]):
                    self.assertTrue(path.is_file(), f"missing declared example {path}")
                    self.assertIsInstance(json.loads(path.read_text(encoding="utf-8")), dict)

    def test_every_exemption_is_actionable_not_a_bare_unknown(self) -> None:
        """An exemption names the unsatisfied predicate, its repair and its owner."""
        for name, exemption in {**BUILDER_BINDING_EXEMPTIONS, **ROUTE_SELECTION_EXEMPTIONS}.items():
            with self.subTest(exemption=name):
                for field in ACTIONABLE_FIELDS:
                    self.assertTrue(str(exemption.get(field, "")).strip(), f"{name} missing {field}")

    def test_an_exemption_never_reports_itself_invocable(self) -> None:
        for row in self.report["rows"]:
            if row["disposition"] != DECLARED_EXEMPTION:
                continue
            with self.subTest(route=row["route_id"]):
                self.assertNotEqual(row["builder_binding"], "BOUND")
                self.assertNotEqual(row["evaluator_example"], "PRESENT")
                for field in ACTIONABLE_FIELDS:
                    self.assertTrue(str(row.get(field, "")).strip())

    def test_exemptions_are_declared_only_for_published_routes(self) -> None:
        """A stale exemption for a route that no longer exists must not linger."""
        capabilities = {row["capability_id"] for row in self.report["rows"]}
        route_ids = {row["route_id"] for row in self.report["rows"]}
        self.assertLessEqual(set(BUILDER_BINDING_EXEMPTIONS), capabilities)
        self.assertLessEqual(set(ROUTE_SELECTION_EXEMPTIONS), route_ids)

    def test_an_exemption_is_granted_against_an_existing_canonical_goal(self) -> None:
        """An exemption cites a registry goal and generation, not the SDK itself."""
        for name, exemption in {**BUILDER_BINDING_EXEMPTIONS, **ROUTE_SELECTION_EXEMPTIONS}.items():
            with self.subTest(exemption=name):
                goal = exemption["owning_existing_goal"]
                self.assertRegex(goal, CANONICAL_TASK_ID,
                                 f"{name} owning goal is not a canonical task id")
                self.assertTrue(exemption["registry_repository"].strip())
                self.assertIsInstance(exemption["observed_registry_generation"], int)
                self.assertGreater(exemption["observed_registry_generation"], 0)
                self.assertIn(goal, exemption["granted_by"],
                              f"{name} must be granted by its owning goal, not self-declared")

    def test_the_granted_exemption_set_matches_its_declared_baseline(self) -> None:
        """Granting an exemption is a deliberate edit, never a side effect."""
        report = self.report
        self.assertEqual(report["undeclared_exemptions"], [],
                         "exemption granted without being declared in EXEMPTION_BASELINE")
        self.assertEqual(report["stale_baseline_entries"], [],
                         "EXEMPTION_BASELINE names an exemption that no longer exists")
        self.assertTrue(report["exemption_baseline_matches"])
        self.assertEqual(
            len(EXEMPTION_BASELINE),
            len(BUILDER_BINDING_EXEMPTIONS) + len(ROUTE_SELECTION_EXEMPTIONS),
        )

    def test_no_exemption_has_outlived_its_review_date(self) -> None:
        """An exemption that never lapses is a permanent carve-out."""
        self.assertEqual(
            self.report["expired_exemption_count"], 0,
            "a declared exemption is past its review_by: re-grant it against its "
            "owning goal or do the repair it names",
        )

    def test_review_dates_expire_and_a_malformed_date_is_treated_as_expired(self) -> None:
        from datetime import date
        self.assertTrue(_expired("2026-01-01", today=date(2026, 9, 29)))
        self.assertFalse(_expired("2026-12-31", today=date(2026, 9, 29)))
        self.assertTrue(_expired(None))
        self.assertTrue(_expired("not-a-date"))

    def test_reconciliation_grants_no_authority(self) -> None:
        self.assertIs(self.report["grants_execution_authority"], False)
        self.assertEqual(self.report["authority_effect"], "NONE_RECONCILIATION_ONLY")
        self.assertTrue(all(r["execution_authorized"] is False for r in self.report["rows"]))


if __name__ == "__main__":
    unittest.main()
