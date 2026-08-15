from __future__ import annotations

import unittest

from stegverse.mcp_governance import build_governed_request, build_portable_packet
from stegverse.mcp_reference_server import tool_definitions
from stegverse.public_inspection import validate_public_inspection_request


class MCPRequestBoundaryTests(unittest.TestCase):
    def test_mcp_request_is_non_authorizing_and_accepted_by_sovereign_intake_validator(self):
        packet = build_portable_packet(
            descriptor_name="stegverse-general-mcp",
            protocol_version="2025-06-18",
            server_info={"name": "stegverse-general-mcp", "version": "1.0.0"},
            tool=tool_definitions()[0],
            arguments={},
        )
        request = build_governed_request(packet)
        self.assertFalse(request["execution_provenance"]["external_consequence_enabled"])
        self.assertFalse(request["authority_claim"])
        normalized = validate_public_inspection_request(request)
        self.assertEqual("PRODUCTION_VALIDATION", normalized["execution_provenance"]["lane_class"])
        self.assertEqual("PRODUCTION_ROUTE_BOUNDED_CONSEQUENCE", normalized["execution_provenance"]["containment"])


if __name__ == "__main__":
    unittest.main()
