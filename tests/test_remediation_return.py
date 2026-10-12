import unittest
from stegverse.remediation_return import validate_remediation_return


def fixture():
    binding = {"transition_id": "remediation-002", "canonical_manifest_sha256": "a" * 64,
               "route_id": "manifest-route", "processing_capability": "governance",
               "authority_effect": "NONE_BINDING_ONLY"}
    proposal = {"schema": "stegverse.remediation.manifest-transition-proposal/v1",
                "manifest_transition": binding, "approval_result": "NOT_EVALUATED"}
    request = {"canonical_manifest_sha256": "a" * 64, "route_id": "manifest-route",
               "processing_capability": "governance"}
    result = {**request, "disposition": "DENY", "originating_evaluator_request_id": "eval-001",
              "authoritative_receipt_chain": [
                  {"receipt_sha256": "b" * 64},
                  {"receipt_sha256": "c" * 64, "predecessor_receipt_sha256": "b" * 64}],
              "independent_organization_ledger_readback_verified": True,
              "originating_evaluator_return_acknowledged": True}
    return proposal, request, result, {"request_id": "eval-001"}


class RemediationReturnTests(unittest.TestCase):
    def test_self_asserted_readback_is_insufficient(self):
        with self.assertRaisesRegex(ValueError, "INDEPENDENT_ORGANIZATION_LEDGER_READBACK_REQUIRED"):
            validate_remediation_return(*fixture())

    def test_reject_broken_receipt_predecessor(self):
        p, q, r, e = fixture()
        r["authoritative_receipt_chain"][1]["predecessor_receipt_sha256"] = "wrong"
        with self.assertRaisesRegex(ValueError, "AUTHORITATIVE_RECEIPT_PREDECESSOR_MISMATCH"):
            validate_remediation_return(p, q, r, e)

    def test_reject_missing_independent_readback(self):
        p, q, r, e = fixture()
        r["independent_organization_ledger_readback_verified"] = False
        with self.assertRaisesRegex(ValueError, "INDEPENDENT_ORGANIZATION_LEDGER_READBACK_REQUIRED"):
            validate_remediation_return(p, q, r, e)

    def test_reject_evaluator_mismatch(self):
        p, q, r, e = fixture()
        e["request_id"] = "different"
        with self.assertRaisesRegex(ValueError, "ORIGINATING_EVALUATOR_RETURN_BINDING_MISMATCH"):
            validate_remediation_return(p, q, r, e)


if __name__ == "__main__":
    unittest.main()
