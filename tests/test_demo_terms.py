from __future__ import annotations

import copy
import unittest

from stegverse.demo_terms import accept_demo_terms, current_demo_terms_descriptor, verify_demo_terms_acceptance


class DemoTermsTests(unittest.TestCase):
    def test_affirmative_acceptance_is_required(self) -> None:
        with self.assertRaises(ValueError):
            accept_demo_terms(
                participant_id="evaluator-1",
                signer_name="Evaluator One",
                signer_capacity="self",
                accepted=False,
                electronic_signature="Evaluator One",
            )

    def test_current_terms_are_hash_bound(self) -> None:
        descriptor = current_demo_terms_descriptor()
        self.assertEqual(descriptor["terms_of_service"]["version"], "1.0.0")
        self.assertEqual(descriptor["terms_of_use"]["version"], "1.0.0")
        self.assertEqual(len(descriptor["terms_of_service"]["sha256"]), 64)
        self.assertEqual(len(descriptor["terms_of_use"]["sha256"]), 64)

    def test_valid_acceptance_verifies(self) -> None:
        receipt = accept_demo_terms(
            participant_id="org:example",
            signer_name="Authorized Signer",
            signer_capacity="authorized representative",
            accepted=True,
            electronic_signature="Authorized Signer",
            accepted_at="2026-08-11T16:00:00Z",
        )
        self.assertTrue(verify_demo_terms_acceptance(receipt))

    def test_terms_or_receipt_tamper_fails(self) -> None:
        receipt = accept_demo_terms(
            participant_id="org:example",
            signer_name="Authorized Signer",
            signer_capacity="authorized representative",
            accepted=True,
            electronic_signature="Authorized Signer",
            accepted_at="2026-08-11T16:00:00Z",
        )
        tampered = copy.deepcopy(receipt)
        tampered["terms"]["terms_of_use"]["sha256"] = "0" * 64
        self.assertFalse(verify_demo_terms_acceptance(tampered))

    def test_acceptance_does_not_replace_software_license(self) -> None:
        receipt = accept_demo_terms(
            participant_id="evaluator-1",
            signer_name="Evaluator One",
            signer_capacity="self",
            accepted=True,
            electronic_signature="Evaluator One",
            accepted_at="2026-08-11T16:00:00Z",
        )
        self.assertFalse(receipt["software_license_rights_replaced"])
        self.assertFalse(receipt["execution_authority_granted"])
        self.assertFalse(receipt["credential_authority_granted"])
        self.assertFalse(receipt["repository_access_granted"])


if __name__ == "__main__":
    unittest.main()
