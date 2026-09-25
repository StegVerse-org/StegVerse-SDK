"""Generate the canonical SDK diagnostic manifest for MIR/SV Experiment 3.

This invokes the SDK's *existing* manifest builder and installed read-only
processor. It does not probe resident custody or manufacture runtime receipts.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from stegverse.manifest_builder import build_manifest
from stegverse.manifest_contract import validate_ingress_manifest
from stegverse.ecosystem_diagnostic_runtime import execute_manifest as execute_local_diagnostic

HERE = Path(__file__).resolve().parents[1] / "inspection" / "examples" / "mir-sv-exp3"

def build_exp3_manifest():
    data = json.loads((HERE / "assessment-input.json").read_text(encoding="utf-8"))
    request = json.loads((HERE / "diagnostic-request.json").read_text(encoding="utf-8"))
    if data["goal_task_id"] != "MIR-SV-CAPABILITY-BOUNDARY-EXPERIMENT-003":
        raise ValueError("experiment identity changed")
    if data["cosv"] != "50000000100000":
        raise ValueError("canonical COSV mismatch")
    if set(row["key"] for row in data["dimensions"]) != {"observe", "demonstrate", "retain", "reconstruct"}:
        raise ValueError("exact four-dimension assessment required")
    if not all(row["capability"] and row["limit"] and row["verification"] for row in data["dimensions"]):
        raise ValueError("capability, limitation and check required together")
    if not all(row["unknowns"] for row in data["four_questions"]):
        raise ValueError("unknowns must be explicit")
    manifest = build_manifest(
        data=data,
        source_framework="StegVerse",
        source_output_id="mir-sv-exp3-stegverse-assessment-source-20260924",
        source_instance="MIR-SV-CAPABILITY-BOUNDARY-EXPERIMENT-003",
        data_class="stegverse.mir-sv-exp3.capability-boundary-input/v1",
        processor_request=request,
        process="ecosystem_diagnostic",
        return_depth="full-trace",
        initiator_class="organization",
        initiator_ref="StegVerse-Labs",
        for_external_review=True,  # default Publisher required for reviewer-facing use
        declared_intent="Produce the StegVerse-side four-dimension evidence assessment using the existing read-only diagnostic processor; preserve equal-weight limitations and unverified runtime states.",
        requested_consequence="Return a diagnostic evidence artifact with the declared Publisher stage and separately attributable unknowns; do not imply external egress or physical execution.",
        context_refs=[
            "StegVerse-Labs/.github:docs/MIR_SV_CAPABILITY_BOUNDARY_EXPERIMENT_003_MIRROR_HANDOFF.md",
            "MIR-original-PDF-SHA256:1e2f134ab60144bb4c5a4de135c6f76d460f22995a0e0b2df1ef071f7e8c8ffe",
        ],
        created_at="2026-09-24T00:00:00Z",
    )
    canonical = validate_ingress_manifest(manifest)
    if canonical["processing"]["capability"] != "ecosystem_diagnostic":
        raise ValueError("SDK selected unexpected processing capability")
    return manifest

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--result", type=Path)
    a=p.parse_args(argv)
    manifest=build_exp3_manifest()
    a.manifest.write_text(json.dumps(manifest,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf-8")
    if a.result is not None:
        result=execute_local_diagnostic(manifest)
        a.result.write_text(json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf-8")
    print("MIR_SV_EXP3_SDK_MANIFEST_BUILT_AND_VALIDATED; runtime evidence is NOT_OBSERVED unless separately supplied")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
