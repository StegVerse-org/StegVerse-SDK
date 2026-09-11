import unittest

from stegverse.public_inspection import PublicInspectionRequestError, validate_public_inspection_request


class PublicInspectionProcessorCapabilityTests(unittest.TestCase):
    def request(self, capability="governance"):
        return {
            "schema_version": "1.0",
            "request_id": "processor-capability-regression",
            "requester_label": "regression",
            "case_profile": "ordinary",
            "execution_provenance": {
                "route_id": "stegverse.route.canonical-governed.v1",
                "processor_capability": capability,
                "route_declaration_hash": "a" * 64,
                "state_binding_hash": "b" * 64,
                "lane_class": "PRODUCTION_VALIDATION",
                "routing_surface": "CANONICAL_PRODUCTION",
                "containment": "PRODUCTION_ROUTE_BOUNDED_CONSEQUENCE",
                "sandbox_required": False,
                "sandbox_tier": "NONE",
                "origin_surface": "test",
                "external_consequence_enabled": False,
                "third_party_host_required": False,
            },
            "input": {"value": "bounded"},
            "return_projection": "ALL",
            "manifest_labels": True,
            "authority_claim": False,
        }

    def test_processor_capability_is_preserved(self):
        normalized = validate_public_inspection_request(self.request())
        self.assertEqual(
            "governance",
            normalized["execution_provenance"]["processor_capability"],
        )

    def test_empty_processor_capability_is_rejected(self):
        with self.assertRaises(PublicInspectionRequestError):
            validate_public_inspection_request(self.request(""))


if __name__ == "__main__":
    unittest.main()
