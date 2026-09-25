"""Prepare exact-byte, non-authorizing SDK reviewer evidence for existing Publisher InTr.

Input files remain on the authorized caller's source surface. This helper
materializes only a canonical existing Publisher artifact-transfer packet;
it does NOT submit InTr, mint an SDK manifest receipt, perform Master Records
custody, or assert a Publisher return.
"""
from __future__ import annotations

import argparse
import base64
import copy
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from .manifest_contract import validate_ingress_manifest
from .governance_navigation import canonical_sha256

REPORT_SCHEMA = "stegverse.publisher.evidence-report-package/v1"
TRANSFER_SCHEMA = "stegverse.publisher.artifact-transfer/v1"
SDK_ARTIFACT_NAMES = ("mir-sv-exp3.manifest.json", "mir-sv-exp3.diagnostic-result.json")
SOURCE_ONLY = "SOURCE_VALIDATED_SDK_DIAGNOSTIC_NO_AUTHENTIC_GOVERNED_EXECUTION"

class SDKReviewTransferError(ValueError):
    pass

def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def sha(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()

def source_asset(path: str, raw: bytes, *, source_class: str) -> dict[str, Any]:
    if not isinstance(raw, bytes) or not raw:
        raise SDKReviewTransferError("original asset bytes required")
    if not path.startswith("evidence/") or "/" in path[len("evidence/"):]:
        raise SDKReviewTransferError("safe evidence filename required")
    ext = path.rsplit(".", 1)[-1].lower()
    mime = {"pdf":"application/pdf","png":"image/png","jpg":"image/jpeg",
            "jpeg":"image/jpeg","json":"application/json",
            "txt":"text/plain","md":"text/markdown"}.get(ext)
    if mime is None:
        raise SDKReviewTransferError("unsupported original media class")
    if mime == "application/pdf" and not raw.startswith(b"%PDF-"):
        raise SDKReviewTransferError("original PDF signature invalid")
    if mime == "image/png" and not raw.startswith(b"\x89PNG\r\n\x1a\n"):
        raise SDKReviewTransferError("original PNG signature invalid")
    return {"path":path,"media_type":mime,"sha256":sha(raw),"bytes":len(raw),
            "content_base64":base64.b64encode(raw).decode("ascii"),
            "source_class":source_class}

def build_source_only_review_transfer(
    *,
    sdk_manifest: Mapping[str, Any],
    diagnostic_result: Mapping[str, Any],
    original_assets: Mapping[str, bytes],
    expected_original_sha256: Mapping[str, str],
    approval_ref: str,
    timestamp: str = "2026-09-24T21:33:00-05:00",
) -> dict[str, Any]:
    """Source-scoped reviewer packet. Actual InTr/MR/Publisher outcomes remain unknown."""
    manifest = copy.deepcopy(dict(sdk_manifest))
    canonical = validate_ingress_manifest(manifest)
    if manifest.get("completion",{}).get("publisher",{}).get("required") is not True:
        raise SDKReviewTransferError("review manifest must require Publisher")
    if not isinstance(approval_ref,str) or not approval_ref.strip():
        raise SDKReviewTransferError("explicit external-review instruction reference required")
    result = copy.deepcopy(dict(diagnostic_result))
    if result.get("schema") != "stegverse.ecosystem-diagnostic-result.v1":
        raise SDKReviewTransferError("source-only diagnostic result required for this fixture")
    if result.get("authority_effect") != "NONE_DIAGNOSTIC_ONLY":
        raise SDKReviewTransferError("source-only diagnostic cannot claim execution authority")
    if not isinstance(result.get("results"), list) or not result["results"]:
        raise SDKReviewTransferError("diagnostic results unavailable")
    # Recompute the actual two SDK diagnostic commitments rather than trusting
    # caller-provided JSON or a GitHub workflow name.
    first = {k:v for k,v in result.items() if k not in {
        "product_processing", "admittedcode_processing", "sdk_return_binding_hash",
        "result_binding_hash"}}
    if result.get("result_binding_hash") != canonical_sha256(first):
        raise SDKReviewTransferError("SDK diagnostic result_binding_hash mismatch")
    terminal = {k:v for k,v in result.items() if k != "sdk_return_binding_hash"}
    if result.get("sdk_return_binding_hash") != canonical_sha256(terminal):
        raise SDKReviewTransferError("SDK diagnostic sdk_return_binding_hash mismatch")
    if set(original_assets) != set(expected_original_sha256):
        raise SDKReviewTransferError("exact original file coverage mismatch")
    files = []
    for name in sorted(original_assets):
        if "/" in name or "\\" in name or name.startswith("."):
            raise SDKReviewTransferError("original filename invalid")
        raw = original_assets[name]
        if hashlib.sha256(raw).hexdigest() != expected_original_sha256[name].removeprefix("sha256:"):
            raise SDKReviewTransferError("original file SHA-256 mismatch: "+name)
        files.append(source_asset("evidence/"+name,raw,source_class=(
            "COUNTERPART_SUPPLIED_ORIGINAL" if name.endswith(".pdf") else "USER_SUPPLIED_ORIGINAL")))
    files += [
        source_asset("evidence/sdk-manifest.json",(
            json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False)+"\n"
        ).encode("utf-8"),source_class="SDK_SOURCE_VALIDATED_ARTIFACT"),
        source_asset("evidence/sdk-diagnostic-result.json",(
            json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False)+"\n"
        ).encode("utf-8"),source_class="SDK_SOURCE_VALIDATED_ARTIFACT"),
    ]
    data = manifest.get("payload")
    if not isinstance(data,dict) or set(x.get("key") for x in data.get("dimensions",[])) != {
        "observe","demonstrate","retain","reconstruct"}:
        raise SDKReviewTransferError("four capability-boundary sections required")
    sections = []
    for item in data["dimensions"]:
        for key in ("capability","limit","verification"):
            if not isinstance(item.get(key),str) or not item[key]:
                raise SDKReviewTransferError("equal-weight capability, limit and check required")
        sections.append({
            "section_id":item["key"],"heading":item["key"].title(),
            "body":"CAPABILITY\n"+item["capability"]+"\n\nLIMITATION\n"+item["limit"]+
                   "\n\nINDEPENDENT CHECK\n"+item["verification"],
            "content_class":"OWNER_AUTHORED","fidelity":"semantic_reconstruction",
            "source_subject_ids":["evidence/sdk-manifest.json"],
        })
    questions=data.get("four_questions")
    if not isinstance(questions,list) or len(questions)!=4:
        raise SDKReviewTransferError("four experiment questions required")
    sections.append({
        "section_id":"four-questions","heading":"Claimed, observed, physical work, unknown",
        "body":"\n\n".join(
            q["question"]+"\n"+q["answer"]+
            "\nEvidence class: "+q["evidence_class"]+
            "\nUnknowns: "+("; ".join(q["unknowns"])) for q in questions
        ),
        "content_class":"OWNER_AUTHORED","fidelity":"semantic_reconstruction",
        "source_subject_ids":["evidence/sdk-manifest.json","evidence/sdk-diagnostic-result.json"],
    })
    sections.append({
        "section_id":"evidence-ceiling","heading":"Source-only proof ceiling and dissent",
        "body":"No current authentic resident organization ledger, Master Records closure, external physical measurement, Publisher transport or third-party validation was obtained by this source-only packet. Richard's original document retains independent semantic custody; screenshots are user-supplied, not platform-native export authentication. Any disagreement remains separately attributable.",
        "content_class":"OWNER_AUTHORED","fidelity":"semantic_reconstruction",
        "source_subject_ids":["evidence/sdk-manifest.json","evidence/sdk-diagnostic-result.json"],
    })
    inventory = [{"path":a["path"],"sha256":a["sha256"],"bytes":a["bytes"],
                  "media_type":a["media_type"],"source_class":a["source_class"]} for a in files]
    basis = sha(canonical_bytes(inventory))
    created = datetime.fromisoformat(timestamp.replace("Z","+00:00"))
    if created.tzinfo is None:
        raise SDKReviewTransferError("timezone-aware source date required")
    export = {
        "schema_version": REPORT_SCHEMA,
        "export_id":"mir-sv-exp3-evaluator-review-source-only-"+canonical["canonical_manifest_sha256"][:12],
        "source":{"repository":"StegVerse-org/StegVerse-SDK",
                  "release":"source-validated:4c709c6e376647c75b3ff685b4829fe1f8110fc5",
                  "verification_root":basis,"event_ids":[a["path"] for a in files],
                  "vault_class":None},
        "authorization":{
            "authority_ref":approval_ref,"authority_source":"direct_instruction",
            "destination":"GCAT-BCAT-Engine/Publisher",
            "expires_at":(created+timedelta(days=14)).isoformat(),
            "purpose":"EXTERNAL_EVALUATOR_REVIEW",
            "receipt_id":approval_ref,"revocable":True,"revoked":False,
            "status":"active","scope":[a["path"] for a in files],
            "allowed_formats":["markdown","html","pdf","json"],
        },
        "created_at":created.isoformat(),
        "document":{
            "authors":[{"name":"StegVerse (source claims); Richard Whitney (independent MIR contribution)"}],
            "document_id":"mir-sv-exp3-sdk-review-source-only",
            "document_type":"EVIDENCE_REPORT",
            "sections":sections,"subtitle":"Source-validated assessment; current sovereign runtime not established",
            "template_profile":"stegverse.publisher.evidence-report-package/v1",
            "title":"MIR / StegVerse Experiment 3: capabilities and equally weighted limitations",
        },
        "evidence":[{
            "subject_id":a["path"],"path":a["path"],"content_hash":a["sha256"],
            "bytes":a["bytes"],"media_type":a["media_type"],
            "fidelity":"exact","retention_class":"full_fidelity","payload_available":True,
            "derived_index":False,"superseded":False,"restricted":False,
            "contains_credentials":False,
        } for a in files],
        "redaction":{"profile":"private-review-only","removed_paths":[],
                     "restricted_content_present":False,"review_state":"OWNER_APPROVED"},
        "requested_formats":["markdown","html","pdf","json"],
        "publication_authorized":False,"release_authorized":False,
        "execution_authorized":False,"authority_effect":"NONE",
    }
    export["export_sha256"] = sha(canonical_bytes(export))
    transfer = {
        "schema":TRANSFER_SCHEMA,
        "transfer_id":"mir-sv-exp3-review-"+canonical["canonical_manifest_sha256"][:18],
        "operation":"TRANSFER","export_bundle":export,"export_sha256":export["export_sha256"],
        "requested_formats":list(export["requested_formats"]),
        "authorization_ref":approval_ref,"evaluator_assets":files,
        "publication_authorized":False,"release_authorized":False,
        "execution_authorized":False,"authority_effect":"NONE",
    }
    return transfer


def main(argv: list[str] | None = None) -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest",type=Path,required=True)
    parser.add_argument("--result",type=Path,required=True)
    parser.add_argument("--original-dir",type=Path,required=True)
    parser.add_argument("--sha256sums",type=Path,required=True)
    parser.add_argument("--approval-ref",required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args(argv)
    checks={}
    for line in args.sha256sums.read_text().splitlines():
        if not line.strip(): continue
        key,name=line.strip().split(None,1)
        checks[name.strip()]=key
    files={name:(args.original_dir/name).read_bytes() for name in checks}
    value=build_source_only_review_transfer(
        sdk_manifest=json.loads(args.manifest.read_text()),
        diagnostic_result=json.loads(args.result.read_text()),
        original_assets=files,expected_original_sha256=checks,
        approval_ref=args.approval_ref,
    )
    args.output.write_bytes(canonical_bytes(value))
    print("SOURCE_ONLY_REVIEW_TRANSFER_PREPARED_NOT_TRANSPORTED")
    print("sha256:"+hashlib.sha256(args.output.read_bytes()).hexdigest())
    return 0

if __name__=="__main__":
    raise SystemExit(main())
