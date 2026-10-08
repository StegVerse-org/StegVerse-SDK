"""Master Records organization-record naming migration (MASTER-RECORDS-BULK-SEMANTIC-REMEDIATION-002).

Writers emit only the new names; readers accept the new names and the legacy ones.
"""
import copy
import unittest
from unittest.mock import Mock, patch

from stegverse import organization_record_names as names
from stegverse.evaluator_contract import evaluator_contract_example, evaluator_contract_summary
from stegverse.external_interlock_bootstrap import external_interlock_bootstrap_instructions
from stegverse.governance_navigation import normalize_return_projection
from stegverse.production_validation_runtime import _record_route_event, _record_status
from stegverse.public_inspection import (
    PublicInspectionRequestError,
    SUPPORTED_EVALUATION_CAPABILITIES,
    prepare_public_inspection_submission,
    validate_public_inspection_request,
)


def _request(capability):
    request = copy.deepcopy(evaluator_contract_example())
    request["evaluation_declaration"]["requested_capabilities"] = [
        "commit_time_admissibility",
        capability,
    ]
    return request


class OrganizationRecordMigrationTests(unittest.TestCase):
    def test_every_legacy_name_differs_from_its_new_name(self):
        for new, legacy in names.LEGACY_NAMES.items():
            self.assertNotEqual(new, legacy)
            self.assertEqual(names.legacy_name_for(new), legacy)

    def test_read_compatible_prefers_new_name_and_falls_back_to_legacy(self):
        field = names.ORGANIZATION_RECORD_STATUS_FIELD
        self.assertEqual("RECORDED", names.read_compatible({field: "RECORDED"}, field))
        self.assertEqual(
            "RECORDED",
            names.read_compatible({"master_records_custody_status": "RECORDED"}, field),
        )
        self.assertEqual(
            "NEW",
            names.read_compatible({field: "NEW", "master_records_custody_status": "OLD"}, field),
        )
        self.assertIsNone(names.read_compatible({}, field))

    def test_public_inspection_accepts_new_and_legacy_capability_names(self):
        self.assertIn("master_records_organization_record", SUPPORTED_EVALUATION_CAPABILITIES)
        for capability in ("master_records_organization_record", "master_records_custody"):
            normalized = validate_public_inspection_request(_request(capability))
            self.assertIn(
                capability,
                normalized["evaluation_declaration"]["requested_capabilities"],
            )
        with self.assertRaises(PublicInspectionRequestError):
            validate_public_inspection_request(_request("master_records_gate"))

    def test_public_inspection_writes_only_new_status_name(self):
        submission = prepare_public_inspection_submission(_request("master_records_organization_record"))
        self.assertEqual("NOT_CLAIMED", submission["master_records_organization_record_status"])
        self.assertNotIn("master_records_custody_status", submission)

    def test_evaluator_contract_advertises_only_new_capability_name(self):
        capabilities = evaluator_contract_summary()["capabilities"]
        self.assertIn("master_records_organization_record", capabilities)
        self.assertNotIn("master_records_custody", capabilities)
        example = evaluator_contract_example()["evaluation_declaration"]["requested_capabilities"]
        self.assertIn("master_records_organization_record", example)

    def test_record_status_reads_new_and_legacy_wire_names(self):
        self.assertEqual("RECORDED", _record_status({"record_status": "RECORDED"}))
        self.assertEqual("RECORDED", _record_status({"custody_status": "RECORDED"}))
        self.assertIsNone(_record_status({}))

    @patch("stegverse.production_validation_runtime.requests.post")
    def test_route_event_request_writes_only_record_requested(self, post):
        post.return_value = Mock(status_code=201, json=lambda: {"record_status": "RECORDED"})
        _record_route_event("https://records.example", "token", "MF-1", {"sequence": 0})
        payload = post.call_args.kwargs["json"]
        self.assertIs(payload["record_requested"], True)
        self.assertNotIn("custody_requested", payload)
        self.assertIs(payload["authority_requested"], False)

    @patch("stegverse.production_validation_runtime.requests.post")
    def test_route_event_still_accepts_legacy_status_from_deployed_service(self, post):
        post.return_value = Mock(status_code=201, json=lambda: {"custody_status": "RECORDED"})
        body = _record_route_event("https://records.example", "token", "MF-1", {"sequence": 0})
        self.assertEqual("RECORDED", body["custody_status"])

    def test_bootstrap_writes_only_new_requirement_name(self):
        text = repr(external_interlock_bootstrap_instructions())
        self.assertNotIn("master_records_custody_required", text)

    def test_return_projection_writes_only_new_suppression_flag(self):
        projection = normalize_return_projection(None)
        self.assertFalse(projection["suppresses_master_records_organization_record"])
        self.assertNotIn("suppresses_master_records_custody", projection)


if __name__ == "__main__":
    unittest.main()
