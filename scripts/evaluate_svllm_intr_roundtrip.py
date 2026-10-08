#!/usr/bin/env python3
"""Evaluator entrypoint: build an SDK manifest, invoke an authorized transport,
and verify forward/return organization receipts. No synthetic success path.

The adapter/transport implementation is injected by the existing execution
surface via --transport-module. This program never grants admission or creates
a new endpoint, credential, runtime, or ledger.
"""
import argparse
import hashlib
import importlib
import json
from pathlib import Path
from stegverse.manifest_builder import build_manifest


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def require(condition, predicate):
    if not condition:
        raise ValueError(predicate)


def verify(result, manifest):
    require(isinstance(result, dict), "TRANSPORT_RESULT_NOT_OBJECT")
    require(result.get("manifest_sha256") == digest(manifest), "CANONICAL_MANIFEST_BINDING_MISMATCH")
    require(result.get("origin") == "StegVerse-org/.github", "ORIGIN_ORGANIZATION_MISMATCH")
    require(result.get("destination") == "SV-LLM/.github", "DESTINATION_ORGANIZATION_MISMATCH")
    for name in ("forward_intr", "sv_llm_ingress", "return_intr", "stegverse_org_ingress"):
        event = result.get(name)
        require(isinstance(event, dict), f"{name.upper()}_RECEIPT_NOT_OBSERVED")
        require(event.get("disposition") == "ALLOW", f"{name.upper()}_NOT_ADMITTED")
        require(isinstance(event.get("receipt_id"), str) and bool(event["receipt_id"]), f"{name.upper()}_RECEIPT_ID_MISSING")
        require(isinstance(event.get("ledger_head"), str) and bool(event["ledger_head"]), f"{name.upper()}_LEDGER_HEAD_MISSING")
        require("predecessor" in event, f"{name.upper()}_PREDECESSOR_NOT_RETAINED")
        require(event.get("authenticated_readback") is True, f"{name.upper()}_AUTHENTIC_READBACK_MISSING")
    require(result["return_intr"].get("references_receipt_id") == result["forward_intr"]["receipt_id"],
            "RETURN_NOT_BOUND_TO_FORWARD_RECEIPT")
    require(result["stegverse_org_ingress"].get("verified_intr_receipt_ids") == [
        result["forward_intr"]["receipt_id"], result["return_intr"]["receipt_id"]
    ], "ORIGIN_DID_NOT_VERIFY_BOTH_INTR_RECEIPTS")
    require(result.get("master_records_reconstruction_verified") is True, "MASTER_RECORDS_RECONSTRUCTION_NOT_VERIFIED")
    require(result.get("evidence_source") == "AUTHENTIC_SOVEREIGN_READBACK", "AUTHENTIC_EVIDENCE_SOURCE_REQUIRED")
    require(isinstance(result.get("evidence_refs"), list) and bool(result["evidence_refs"]), "INDEPENDENT_EVIDENCE_REFERENCES_REQUIRED")
    return {"state": "ALLOW", "verified": True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="source-native JSON")
    parser.add_argument("--processor-request", required=True, help="existing installed processor request JSON")
    parser.add_argument("--process", required=True, help="existing installed processing capability")
    parser.add_argument("--transport-module", required=True, help="authorized existing transport module with submit(manifest)")
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    report = {"schema": "stegverse.evaluator.svllm-intr-roundtrip/v1", "state": "FAIL_CLOSED",
              "execution_observed": False, "failed_predicate": "NOT_ATTEMPTED"}
    try:
        data = json.loads(Path(args.input).read_text())
        request = json.loads(Path(args.processor_request).read_text())
        manifest = build_manifest(data=data, processor_request=request, process=args.process,
                                  source_framework="stegverse_org_evaluator",
                                  source_output_id="ORG-SVLLM-BIDIRECTIONAL-INTR-RECEIPT-001",
                                  return_depth="full-trace", external_review=True,
                                  destination_profile="SV-LLM/.github")
        require(manifest.get("manifest_profile") == "stegverse.ingress-manifest.v1",
                "MANIFEST_BUILDER_DID_NOT_RETURN_CANONICAL_MANIFEST")
        (out / "builder-manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        require(args.process == "stegbrowser", "STEGBROWSER_PROCESSING_REQUIRED")
        transport = importlib.import_module(args.transport_module)
        submit = getattr(transport, "submit", None)
        require(callable(submit), "AUTHORIZED_TRANSPORT_SUBMIT_NOT_EXPOSED")
        report["transport_invocation_attempted"] = True
        result = submit(manifest)
        report["execution_observed"] = True
        (out / "transport-result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        report.update(verify(result, manifest))
        report["failed_predicate"] = None
        report["receipt_ids"] = [result["forward_intr"]["receipt_id"], result["return_intr"]["receipt_id"]]
    except Exception as exc:
        report["state"] = "FAIL_CLOSED"
        report["failed_predicate"] = str(exc) if isinstance(exc, (ValueError, ImportError, AttributeError)) else "EXECUTION_EXCEPTION_" + type(exc).__name__
    (out / "evaluator-result.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, sort_keys=True))
    return 0 if report["state"] == "ALLOW" else 1


if __name__ == "__main__":
    raise SystemExit(main())
