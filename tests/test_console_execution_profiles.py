"""Console governance execution-profile source contract."""
import json
from pathlib import Path
import unittest

from stegverse.manifest_builder import (
    ECOSYSTEM_CONNECTED,
    LOCAL_CONFORMANCE,
    build_manifest,
)
from stegverse.route_resolution import (
    CANONICAL_PRODUCTION_ROUTE_ID,
    CUSTOMER_LOCAL_GOVERNANCE_ROUTE_ID,
    route_from_manifest,
)

ROOT = Path(__file__).resolve().parent.parent / "inspection" / "examples"


class ConsoleExecutionProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads((ROOT / "sdk-tt-shared-source.json").read_text())
        cls.request = json.loads((ROOT / "elan-governance-request.example.json").read_text())

    def build(self, profile):
        return build_manifest(
            data=self.source,
            source_framework="execution-profile-test",
            source_output_id=profile,
            processor_request=self.request,
            process="governance",
            execution_profile=profile,
            created_at="2026-10-04T00:00:00Z",
        )

    def test_local_profile_selects_only_customer_local_route(self):
        manifest = self.build(LOCAL_CONFORMANCE)
        self.assertEqual(manifest["processing"]["route_id"], CUSTOMER_LOCAL_GOVERNANCE_ROUTE_ID)
        self.assertEqual(manifest["extensions"]["manifest_builder"]["execution_profile"], LOCAL_CONFORMANCE)
        self.assertIsNone(manifest["completion"])
        self.assertEqual(route_from_manifest(manifest)["route_id"], CUSTOMER_LOCAL_GOVERNANCE_ROUTE_ID)

    def test_connected_profile_selects_only_canonical_route(self):
        manifest = self.build(ECOSYSTEM_CONNECTED)
        self.assertEqual(manifest["processing"]["route_id"], CANONICAL_PRODUCTION_ROUTE_ID)
        self.assertEqual(manifest["extensions"]["manifest_builder"]["execution_profile"], ECOSYSTEM_CONNECTED)
        self.assertIsNotNone(manifest["completion"])
        self.assertEqual(route_from_manifest(manifest)["route_id"], CANONICAL_PRODUCTION_ROUTE_ID)

    def test_default_remains_ecosystem_connected(self):
        manifest = build_manifest(
            data=self.source, source_framework="compat", source_output_id="default",
            processor_request=self.request, process="governance",
            created_at="2026-10-04T00:00:00Z",
        )
        self.assertEqual(manifest["processing"]["route_id"], CANONICAL_PRODUCTION_ROUTE_ID)

    def test_local_profile_cannot_select_non_governance(self):
        with self.assertRaisesRegex(ValueError, "only for governance"):
            build_manifest(
                data=self.source, source_framework="negative", source_output_id="negative",
                processor_request={}, process="ecosystem_diagnostic",
                execution_profile=LOCAL_CONFORMANCE, created_at="2026-10-04T00:00:00Z",
            )

    def test_unknown_profile_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "unsupported execution_profile"):
            self.build("FALLBACK_TO_WHATEVER_WORKS")


if __name__ == "__main__":
    unittest.main()
