"""Reviewer default and generic Publisher exact-return boundary regression."""
import base64
import copy
import json
import unittest

from stegverse.manifest_builder import build_manifest
from stegverse.review_publisher_transfer import (
    ReviewPublisherBoundaryError, prepare_review_transfer,
    bind_exact_review_return, canonical_json, digest, digest_bytes,
)
from tests.test_manifest_builder import governance_request
from tests.test_publisher_return_binding import publisher_return_value


def review_manifest(*, external_review=True, publisher_required=None):
    return build_manifest(
        data={"source": "independent-assessment", "limitations": ["live runtime not observed"]},
        source_framework="StegVerse",
        source_output_id="mir-sv-exp3-test-source-fixture",
        processor_request=governance_request(),
        created_at="2026-09-24T00:00:00Z",
        external_review=external_review,
        publisher_required=publisher_required,
    )


def originals():
    pdf=b"%PDF-1.4\nOriginal counterpart PDF test fixture\n"
    png=b"\x89PNG\r\n\x1a\noriginal screenshot test fixture"
    return [
        {"path":"evidence/IMG_3282.png","media_type":"image/png",
         "sha256":digest_bytes(png),"bytes":len(png),
         "content_base64":base64.b64encode(png).decode(),"source_class":"USER_SUPPLIED_ORIGINAL"},
        {"path":"evidence/experiment-one-mir-side.pdf","media_type":"application/pdf",
         "sha256":digest_bytes(pdf),"bytes":len(pdf),
         "content_base64":base64.b64encode(pdf).decode(),"source_class":"COUNTERPART_SUPPLIED_ORIGINAL"},
    ]


def source_bundle():
    files=originals()
    b={
        "schema_version":"stegverse.publisher.evidence-report-package/v1",
        "export_id":"exp3-review-source-fixture",
        "created_at":"2026-09-24T00:00:00Z",
        "authorization":{
            "authority_ref":"owner-review-fixture-only","receipt_id":"owner-review-fixture-only",
            "status":"active","revoked":False,"destination":"GCAT-BCAT-Engine/Publisher",
            "purpose":"EXTERNAL_EVALUATOR_REVIEW","scope":[f["path"] for f in files],
            "allowed_formats":["pdf","json"],"expires_at":"2099-12-31T23:59:59Z",
        },
        "requested_formats":["pdf","json"],
        "source":{"repository":"StegVerse-org/StegVerse-SDK","release":"source-test",
                  "verification_root":digest(review_manifest()),"event_ids":[],
                  "vault_class":"SOURCE_REPORT"},
        "evidence":[
            {"subject_id":f["path"],"path":f["path"],"content_hash":f["sha256"],
             "bytes":f["bytes"],"media_type":f["media_type"],"fidelity":"exact",
             "retention_class":"full_fidelity","payload_available":True,"derived_index":False,
             "restricted":False,"superseded":False,"contains_credentials":False,
             "artifact_refs":[]}
            for f in files
        ],
        "document":{"document_id":"mir-sv-exp3-review-fixture","document_type":"REPORT",
                    "title":"MIR/SV Exp3 source-only evaluator fixture",
                    "authors":[{"name":"StegVerse","affiliation":"StegVerse"}],
                    "sections":[{"section_id":d,"heading":d.title(),
                                 "body":"Source capability and limitation; authentic runtime not observed.",
                                 "content_class":"OWNER_AUTHORED","fidelity":"semantic_reconstruction",
                                 "source_subject_ids":[files[0]["path"]]}
                                for d in ("observe","demonstrate","retain","reconstruct")]},
        "redaction":{"profile":"owner-reviewed-export-v1","removed_paths":[],
                     "restricted_content_present":False,"review_state":"OWNER_APPROVED"},
        "publication_authorized":False,"release_authorized":False,
        "execution_authorized":False,"authority_effect":"NONE",
    }
    b["export_sha256"]=digest(b)
    return b


class ReviewerPublisherTests(unittest.TestCase):
    def test_default_for_explicit_review_but_not_ordinary_sdk(self):
        self.assertTrue(review_manifest()["completion"]["publisher"]["required"])
        self.assertFalse(review_manifest(external_review=False)["completion"]["publisher"]["required"])
        self.assertTrue(review_manifest()["extensions"]["manifest_builder"]["external_review_requested"])

    def test_explicit_review_opt_out_remains_optional(self):
        self.assertFalse(review_manifest(publisher_required=False)["completion"]["publisher"]["required"])
        self.assertFalse(review_manifest(publisher_required=False)["extensions"]["manifest_builder"]["publisher_required_by_review_default"])
        self.assertTrue(review_manifest(external_review=False,publisher_required=True)["completion"]["publisher"]["required"])

    def test_exact_publisher_transfer_uses_existing_schema_without_claiming_delivery(self):
        p=prepare_review_transfer(manifest=review_manifest(),authorized_export_bundle=source_bundle(),
                                  original_assets=originals(),transfer_id="exp3-review-fixture-001")
        self.assertEqual(p["state"],"PREPARED_NOT_TRANSPORTED")
        self.assertEqual(p["transfer_sha256"],digest_bytes(p["transfer_bytes"]))
        self.assertEqual(p["transfer"]["schema"],"stegverse.publisher.artifact-transfer/v1")
        self.assertEqual(len(p["expected_original_paths"]),2)
        self.assertEqual(p["authority_effect"],"NONE")
        self.assertEqual(json.loads(p["transfer_bytes"]),p["transfer"])

    def test_undeclared_or_tampered_original_fails_closed(self):
        bad=originals()[:-1]
        with self.assertRaisesRegex(ReviewPublisherBoundaryError,"every declared original"):
            prepare_review_transfer(manifest=review_manifest(),authorized_export_bundle=source_bundle(),
                                    original_assets=bad,transfer_id="exp3-review-fixture-001")
        bad=originals()
        bad[0]["content_base64"]=base64.b64encode(b"modified").decode()
        with self.assertRaisesRegex(ReviewPublisherBoundaryError,"hash mismatch"):
            prepare_review_transfer(manifest=review_manifest(),authorized_export_bundle=source_bundle(),
                                    original_assets=bad,transfer_id="exp3-review-fixture-001")

    def test_no_publisher_non_review_cannot_prepare_transfer(self):
        with self.assertRaisesRegex(ReviewPublisherBoundaryError,"requires Publisher"):
            prepare_review_transfer(manifest=review_manifest(external_review=False),
                                    authorized_export_bundle=source_bundle(),
                                    original_assets=originals(),transfer_id="exp3-review-fixture-001")

    def test_source_export_wrong_manifest_root_fails_closed(self):
        b=source_bundle()
        b["source"]["verification_root"]="sha256:"+"0"*64
        b.pop("export_sha256")
        b["export_sha256"]=digest(b)
        with self.assertRaisesRegex(ReviewPublisherBoundaryError,"exact original SDK manifest hash"):
            prepare_review_transfer(manifest=review_manifest(),authorized_export_bundle=b,
                                    original_assets=originals(),transfer_id="exp3-review-fixture-001")

    def test_return_exact_lineage_and_negative_mismatch(self):
        m=review_manifest()
        p=prepare_review_transfer(manifest=m,authorized_export_bundle=source_bundle(),
                                  original_assets=originals(),transfer_id="exp3-review-fixture-001")
        returned=publisher_return_value()
        returned["transfer_id"]=p["transfer_id"]
        returned["source_export_sha256"]=p["export_sha256"]
        returned["artifacts"]+= [
            {"format":"source-original","path":x["path"],"sha256":x["sha256"],"bytes":x["bytes"],
             "content_base64":x["content_base64"],"media_type":x["media_type"],"source_class":x["source_class"]}
            for x in originals()
        ]
        returned["manifest"]["artifacts"]+= [
            {"format":"source-original","path":x["path"],"sha256":x["sha256"],"bytes":x["bytes"],
             "media_type":x["media_type"],"source_class":x["source_class"]}
            for x in originals()
        ]
        returned["manifest"]["manifest_sha256"]=digest({k:v for k,v in returned["manifest"].items() if k!="manifest_sha256"})
        returned["rendering_receipt"]["manifest_sha256"]=returned["manifest"]["manifest_sha256"]
        returned["rendering_receipt"]["receipt_sha256"]=digest({k:v for k,v in returned["rendering_receipt"].items() if k!="receipt_sha256"})
        raw=canonical_json(returned).encode()
        bound=bind_exact_review_return(prepared=p,manifest=m,manifest_receipt_id="MR-0123456789ABCDEF",
                                       publisher_return_bytes=raw)
        self.assertFalse(bound["publisher_transition_observed"]) # no authentic transport receipt
        self.assertTrue(bound["sdk_return_binding_observed"])
        self.assertFalse(bound["communication_complete"])
        bad_manifest=copy.deepcopy(returned)
        bad_manifest["manifest"]["generation_id"]="tampered"
        with self.assertRaisesRegex(ReviewPublisherBoundaryError,"manifest exact digest invalid"):
            bind_exact_review_return(prepared=p,manifest=m,manifest_receipt_id="MR-0123456789ABCDEF",
                                     publisher_return_bytes=canonical_json(bad_manifest).encode())
        bad_receipt=copy.deepcopy(returned)
        bad_receipt["rendering_receipt"]["generation_id"]="tampered"
        with self.assertRaisesRegex(ReviewPublisherBoundaryError,"receipt exact digest invalid"):
            bind_exact_review_return(prepared=p,manifest=m,manifest_receipt_id="MR-0123456789ABCDEF",
                                     publisher_return_bytes=canonical_json(bad_receipt).encode())
        returned["transfer_id"]="different-transfer"
        with self.assertRaisesRegex(ReviewPublisherBoundaryError,"transfer ID mismatch"):
            bind_exact_review_return(prepared=p,manifest=m,manifest_receipt_id="MR-0123456789ABCDEF",
                                     publisher_return_bytes=canonical_json(returned).encode())


if __name__=="__main__":
    unittest.main()
