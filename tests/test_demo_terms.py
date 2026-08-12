from __future__ import annotations

import copy
import unittest

from stegverse.demo_terms import accept_demo_terms, current_demo_terms_descriptor, verify_demo_terms_acceptance


class DemoTermsTests(unittest.TestCase):
    def test_acceptance_binds_exact_current_terms(self) -> None:
        receipt = accept_demo_terms(
            participant_id="evaluator:example",
            signer_name="Example Evaluator",
            signer_capacity="self",
            accepted=True,
            electronic_signature="Example Evaluator",
            accepted_at="2026-08-12T15:00:00Z",
        )
        self.assertTrue(verify_demo_terms_acceptance(receipt))
        self.assertEqual(receipt["terms"], current_demo_terms_descriptor())
        self.assertTrue(receipt["service_relationship_only"])
        self.assertFalse(receipt["software_license_rights_replaced"])
        self.assertFalse(receipt["execution_authority_granted"])
        self.assertFalse(receipt["credential_authority_granted"])
        self.assertFalse(receipt["repository_access_granted"])

    def test_nonaffirmative_or_incomplete_acceptance_fails(self) -> None:
        with self.assertRaises(ValueError):
            accept_demo_terms(participant_id="x", signer_name="x", signer_capacity="self", accepted=False, electronic_signature="x")
        with self.assertRaises(ValueError):
            accept_demo_terms(participant_id="", signer_name="x", signer_capacity="self", accepted=True, electronic_signature="x")

    def test_tampering_or_stale_terms_fail_closed(self) -> None:
        receipt = accept_demo_terms(participant_id="x", signer_name="x", signer_capacity="self", accepted=True, electronic_signature="x", accepted_at="2026-08-12T15:00:00Z")
        tampered = copy.deepcopy(receipt)
        tampered["terms"]["terms_of_use"]["sha256"] = "0" * 64
        self.assertFalse(verify_demo_terms_acceptance(tampered))
        tampered = copy.deepcopy(receipt)
        tampered["receipt_hash"] = "0" * 64
        self.assertFalse(verify_demo_terms_acceptance(tampered))


if __name__ == "__main__":
    unittest.main()
