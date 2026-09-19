from __future__ import annotations

import unittest

from stegverse.product_processing import (
    ADMITTEDCODE_PROCESSING_SCHEMA,
    PRODUCT_PROCESSING_SCHEMA,
    build_product_processing,
    canonical_sha256,
)


def request_with_llm_adapter_origin():
    return {
        "input": {
            "ingress_manifest_identity": {
                "source_framework": "StegVerse-org/LLM-adapter",
                "source_output_id": "adapter-output-7",
                "canonical_manifest_sha256": "sha256:" + "a" * 64,
            }
        }
    }


def runtime_result():
    return {
        "submitted_manifest_hash": "sha256:" + "b" * 64,
        "governance_request_hash": "sha256:" + "c" * 64,
        "state_binding_hash": "d" * 64,
        "declared_route_id": "stegverse.route.canonical-governed.v1",
        "route_declaration_hash": "e" * 64,
        "transaction_id": "txn-1",
        "route_manifest_id": "route-1",
        "route_receipt_ids": ["RR-1", "RR-2"],
        "route_receipt_chain_head": "f" * 64,
        "manifest_receipt_id": "MR-" + "1" * 64,
        "governance_state": "ALLOW",
        "chain_verified": True,
        "master_records_custody_status": "RECORDED",
    }


class ProductProcessingTests(unittest.TestCase):
    def test_composes_product_attribution_without_authority_collapse(self):
        envelope, admitted = build_product_processing(
            normalized_request=request_with_llm_adapter_origin(),
            runtime_result=runtime_result(),
            evaluation={"disposition": "ALLOW", "reason_codes": ["ok"], "reason": "ok"},
        )
        self.assertEqual(PRODUCT_PROCESSING_SCHEMA, envelope["schema"])
        self.assertEqual("NONE", envelope["composition_authority_effect"])
        by_product = {c["product_id"]: c for c in envelope["contributions"]}

        self.assertEqual(
            "DECLARED_UPSTREAM_PROVENANCE",
            by_product["StegVerse-org/LLM-adapter"]["processing_status"],
        )
        self.assertFalse(
            by_product["StegVerse-org/LLM-adapter"]["details"]["independently_verified_by_sdk"]
        )

        self.assertEqual("PROCESSED", by_product["AdmittedCode"]["processing_status"])
        self.assertEqual("ALLOW", by_product["AdmittedCode"]["output_bindings"]["disposition"])
        self.assertEqual(["ok"], by_product["AdmittedCode"]["output_bindings"]["reason_codes"])
        self.assertEqual(
            "ADMISSION_DECISION_ONLY", by_product["AdmittedCode"]["authority_effect"]
        )
        self.assertFalse(by_product["AdmittedCode"]["details"]["admission_is_execution"])

        self.assertEqual("PROCESSED", by_product["StegCore"]["processing_status"])
        self.assertEqual("PROCESSED", by_product["Core-Lite"]["processing_status"])
        self.assertEqual("PROCESSED", by_product["Master Records"]["processing_status"])
        self.assertEqual("CUSTODY_ONLY", by_product["Master Records"]["authority_effect"])

        self.assertEqual("NOT_OBSERVED", by_product["Interlock/InTr"]["processing_status"])
        self.assertEqual("NONE", by_product["Interlock/InTr"]["authority_effect"])
        self.assertEqual("NOT_OBSERVED", by_product["StegAgents/runtime"]["processing_status"])

        self.assertEqual(ADMITTEDCODE_PROCESSING_SCHEMA, admitted["schema"])
        self.assertEqual("admittedcode:canonical-admission", admitted["generic_contribution_ref"])
        self.assertEqual(
            by_product["AdmittedCode"]["contribution_sha256"],
            admitted["contribution_sha256"],
        )

    def test_does_not_invent_upstream_product_without_manifest_identity(self):
        envelope, _ = build_product_processing(
            normalized_request={"input": {}},
            runtime_result=runtime_result(),
            evaluation={"disposition": "ALLOW"},
        )
        products = {c["product_id"] for c in envelope["contributions"]}
        self.assertNotIn("StegVerse-org/LLM-adapter", products)
        self.assertIn("AdmittedCode", products)

    def test_hashes_are_deterministic(self):
        args = dict(
            normalized_request=request_with_llm_adapter_origin(),
            runtime_result=runtime_result(),
            evaluation={"disposition": "ALLOW", "reason_codes": ["ok"]},
        )
        one, admitted_one = build_product_processing(**args)
        two, admitted_two = build_product_processing(**args)
        self.assertEqual(one["product_processing_sha256"], two["product_processing_sha256"])
        self.assertEqual(admitted_one["projection_sha256"], admitted_two["projection_sha256"])
        self.assertEqual(canonical_sha256(one), canonical_sha256(two))


if __name__ == "__main__":
    unittest.main()
