from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from stegverse.mcp_governance import build_governed_request, build_portable_packet, run_mcp_governed_test
from stegverse.mcp_navigation import guidance_for
from stegverse.mcp_reference_server import tool_definitions
from stegverse.mcp_transport import MCPTransportError, StdioMCPClient, reference_descriptor, validate_descriptor
from stegverse.sdk_surfaces import get_sdk_surface


class MCPProductionArtifactUnitTests(unittest.TestCase):
    def test_reference_server_is_inspectable_ordinary_mcp(self):
        names = [tool["name"] for tool in tool_definitions()]
        self.assertEqual(
            ["inspect_state", "write_bounded_value", "create_resource", "single_use_operation"],
            names,
        )
        for tool in tool_definitions():
            self.assertIn("inputSchema", tool)
            self.assertNotIn("steggate", json.dumps(tool).lower())
            self.assertNotIn("authority", json.dumps(tool).lower())

    def test_reference_transport_initializes_lists_and_calls(self):
        with StdioMCPClient(reference_descriptor()) as client:
            self.assertEqual("stegverse-general-mcp", client.server_info["name"])
            tools = client.list_tools()
            self.assertEqual(4, len(tools))
            result = client.call_tool("inspect_state", {})
            self.assertFalse(result["isError"])
            self.assertEqual("OK", result["structuredContent"]["status"])

    def test_packet_binds_exact_discovered_contract_and_arguments(self):
        base_tool = tool_definitions()[1]
        p1 = build_portable_packet(
            descriptor_name="reference",
            protocol_version="2025-06-18",
            server_info={"name": "x", "version": "1"},
            tool=base_tool,
            arguments={"value": 42},
        )
        p2 = build_portable_packet(
            descriptor_name="reference",
            protocol_version="2025-06-18",
            server_info={"name": "x", "version": "1"},
            tool=base_tool,
            arguments={"value": 42},
        )
        self.assertEqual(p1["mcp_contract_hash"], p2["mcp_contract_hash"])
        self.assertEqual(p1["proposed_call_hash"], p2["proposed_call_hash"])

        changed_args = build_portable_packet(
            descriptor_name="reference",
            protocol_version="2025-06-18",
            server_info={"name": "x", "version": "1"},
            tool=base_tool,
            arguments={"value": 43},
        )
        self.assertEqual(p1["mcp_contract_hash"], changed_args["mcp_contract_hash"])
        self.assertNotEqual(p1["proposed_call_hash"], changed_args["proposed_call_hash"])

        drifted_tool = json.loads(json.dumps(base_tool))
        drifted_tool["inputSchema"]["properties"]["value"]["maximum"] = 1000
        drifted = build_portable_packet(
            descriptor_name="reference",
            protocol_version="2025-06-18",
            server_info={"name": "x", "version": "1"},
            tool=drifted_tool,
            arguments={"value": 42},
        )
        self.assertNotEqual(p1["mcp_contract_hash"], drifted["mcp_contract_hash"])
        self.assertNotEqual(p1["proposed_call_hash"], drifted["proposed_call_hash"])

    def test_packet_maps_to_ordinary_steggate_request_without_authority_token(self):
        packet = build_portable_packet(
            descriptor_name="reference",
            protocol_version="2025-06-18",
            server_info={"name": "x", "version": "1"},
            tool=tool_definitions()[0],
            arguments={},
        )
        request = build_governed_request(packet)
        candidate = request["input"]["steggate_request"]["candidate"]
        self.assertEqual("mcp.tools.call:inspect_state", candidate["action"])
        self.assertEqual(packet["mcp_contract_hash"], candidate["parameters"]["mcp_contract_hash"])
        self.assertFalse(request["authority_claim"])
        self.assertNotIn("token", json.dumps(request).lower())

    def test_external_descriptor_rejects_caller_credentials(self):
        safe = validate_descriptor({"transport": "stdio", "command": [sys.executable, "-m", "example"], "name": "x"})
        self.assertEqual("stdio", safe["transport"])
        for descriptor in (
            {"transport": "stdio", "command": ["x"], "token": "bad"},
            {"transport": "stdio", "command": ["x"], "headers": {"Authorization": "bad"}},
            {"transport": "stdio", "command": ["x"], "env": {"API_KEY": "bad"}},
        ):
            with self.assertRaises(MCPTransportError):
                validate_descriptor(descriptor)

    def test_selected_mode_000_documents_canonical_route_and_custody(self):
        text = guidance_for("000")
        self.assertIn("tools/list", text)
        self.assertIn("StegGate", text)
        self.assertIn("Master Records", text)
        self.assertIn("return ingestion/CGE", text)
        self.assertIn("tools/call", text)

    def test_mcp_test_is_discoverable_from_generic_sdk_surfaces(self):
        surface = get_sdk_surface("mcp")
        self.assertIsNotNone(surface)
        assert surface is not None
        self.assertEqual("mcp-production-artifact-test", surface["id"])
        self.assertIn("stegverse-mcp-test", surface["command"])
        self.assertEqual("NONE_UNTIL_CANONICAL_GOVERNANCE", surface["authority_effect"])

    def test_mcp_call_is_passed_as_bounded_consequence_not_preexecuted(self):
        captured = {}

        def fake_governed(request, **kwargs):
            captured["request"] = request
            captured["kwargs"] = kwargs
            self.assertIn("consequence_executor", kwargs)
            result = kwargs["consequence_executor"]()
            captured["execution"] = result
            return {
                "manifest_receipt_id": "MR-" + "A" * 64,
                "master_records_custody_status": "RECORDED",
                "governance_state": "ALLOW",
                "external_side_effect": True,
                "execution_result": result,
            }

        with patch("stegverse.mcp_governance.run_sovereign_validation", side_effect=fake_governed):
            result = run_mcp_governed_test(
                source="reference",
                descriptor_path=None,
                tool_name="inspect_state",
                arguments={},
                custody_db=":memory:",
            )
        self.assertEqual("RECORDED", result["master_records_custody_status"])
        self.assertEqual("MCP_TOOL_RESULT_OBSERVED", captured["execution"]["status"])
        self.assertEqual("canonical-ingestion/CGE->SDK", result["return_path"])
        self.assertEqual(
            captured["request"]["input"]["input_data"]["mcp_packet"]["mcp_contract_hash"],
            captured["execution"]["mcp_contract_hash"],
        )


class MCPProductionArtifactGovernedIntegrationTests(unittest.TestCase):
    @staticmethod
    def _governed_dependencies_available() -> bool:
        try:
            import core_lite.transaction_route  # noqa: F401
            import services.manifest_receipt_custody  # noqa: F401
            import stegcore.steggate  # noqa: F401
        except ImportError:
            return False
        return True

    def test_reference_mcp_crosses_real_canonical_route_and_master_records(self):
        if not self._governed_dependencies_available():
            self.skipTest("install .[governed-test] to execute the canonical integration test")
        with tempfile.TemporaryDirectory() as tmp:
            db = str(Path(tmp) / "mcp-master-records.db")
            result = run_mcp_governed_test(
                source="reference",
                descriptor_path=None,
                tool_name="inspect_state",
                arguments={},
                custody_db=db,
                host_identity="mcp-production-artifact-test",
            )
            governed = result["governed_result"]
            self.assertEqual("RECORDED", governed["master_records_custody_status"])
            self.assertTrue(governed["chain_verified"])
            self.assertTrue(governed["transaction_identity_continuous"])
            self.assertTrue(governed["route_receipt_ids"])
            self.assertTrue(result["manifest_receipt_id"].startswith("MR-"))
            self.assertEqual("MCP_TOOL_RESULT_OBSERVED", governed["execution_result"]["status"])

            from stegverse.sovereign_validation_runtime import reconstruct_sovereign, replay_sovereign
            replay = replay_sovereign(result["manifest_receipt_id"], custody_db=db)
            reconstruction = reconstruct_sovereign(result["manifest_receipt_id"], custody_db=db)
            self.assertFalse(replay["consequence_reexecuted"])
            self.assertEqual("RECORDED", replay["operation_transition_custody_status"])
            self.assertEqual("RECORDED", reconstruction["operation_transition_custody_status"])


if __name__ == "__main__":
    unittest.main()
