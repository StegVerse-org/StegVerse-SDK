"""Build independently versioned MIR Experiment 3 source-only SDK documents."""
import argparse
import json
from pathlib import Path
from stegverse.manifest_builder import build_manifest
from stegverse.manifest_contract import validate_ingress_manifest
from stegverse.ecosystem_diagnostic_runtime import execute_manifest

HERE = Path(__file__).resolve().parents[1] / "inspection/examples/mir-sv-exp3"
NAMES = {
  "primary": "stegverse-commit-time-assessment-v1.json",
  "addendum": "mir-stegverse-ingress-egress-addendum-v1.json",
}

def build(kind):
    if kind not in NAMES:
        raise ValueError("invalid_profile")
    src = json.loads((HERE / NAMES[kind]).read_text(encoding="utf-8"))
    if src["goal_task_id"] != "MIR-SV-CAPABILITY-BOUNDARY-EXPERIMENT-003" or src["cosv"] != "50000000100000":
        raise ValueError("experiment_identity_mismatch")
    if kind == "primary" and [v["key"] for v in src["sections"]] != ["observe", "demonstrate", "retain", "reconstruct"]:
        raise ValueError("four_original_sections_required")
    checks = []
    for item in src["sections"]:
        if any(not item.get(field) for field in ("capability", "limitation", "verification")):
            raise ValueError("capability_limitation_check_required")
        if item["current_exp3_runtime"] != "NOT_OBSERVED" or item["evidence_class"] != "SOURCE_CONTRACT_DOCUMENTED":
            raise ValueError("source_assertion_cannot_be_runtime_proof")
        for suffix, observation in (
            ("source", {"state": "PASS", "evidence_refs": src.get("source_refs") or ["https://github.com/StegVerse-Labs/.github/issues/2682"]}),
            ("runtime", None),
        ):
            checks.append({
                "test_id": item["key"] + "_" + suffix,
                "component_id": "stegverse.exp3." + item["key"],
                "predicate_id": "SECTION_DOCUMENTED" if observation else "AUTHENTIC_RUNTIME_REQUIRED",
                "authority_owner": "existing source owner" if observation else "existing runtime owner",
                "observation": observation,
            })
    manifest = build_manifest(
        data=src, source_framework="StegVerse", source_output_id="mir-exp3-" + kind + "-v1",
        source_instance=src["goal_task_id"], data_class=src["schema"],
        processor_request={
            "schema": "stegverse.ecosystem-diagnostic-request.v1",
            "diagnostic_request_id": "mir-exp3-" + kind + "-v1",
            "scope": "ecosystem", "mutation_permitted": False,
            "expected_evidence_fields": ["exact_source_or_receipt_reference"],
            "tests": checks,
        }, process="ecosystem_diagnostic", return_depth="full-trace",
        initiator_class="organization", initiator_ref="StegVerse-Labs",
        publisher_required=False, created_at="2026-09-26T00:00:00Z",
    )
    validate_ingress_manifest(manifest)
    result = execute_manifest(manifest)
    states = {r["test_id"]: r["observation_state"] for r in result["results"]}
    for item in src["sections"]:
        if states[item["key"] + "_source"] != "PASS" or states[item["key"] + "_runtime"] != "NOT_OBSERVED":
            raise ValueError("diagnostic_evidence_class_drift")
    return manifest, result, src

def markdown(src, kind):
    title = "StegVerse commit-time admissibility" if kind == "primary" else "MIR-Ste​gVerse ingress/egress addendum"
    lines = ["# " + title, "", src["purpose"], "",
        "Evidence ceiling: SDK source declaration checks only; original runtime NOT_OBSERVED.", ""]
    for row in src["sections"]:
        lines.extend(["## " + row["title"], "",
            "Claim (source): " + row["capability"], "",
            "Equal-weight limit: " + row["limitation"], "",
            "Independent check: " + row["verification"], "",
            "Current original runtime: " + row["current_exp3_runtime"], ""])
    if kind == "primary":
        for row in src["questions"]:
            lines.extend(["**" + row["question"] + "** " + row["answer"], ""])
    else:
        lines.extend(["## Delivery predicates", ""])
        lines.extend("- " + x for x in src["required_runtime_evidence"])
    return "\n".join(lines) + "\n"

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output-dir", required=True, type=Path)
    out = p.parse_args().output_dir
    out.mkdir(parents=True, exist_ok=True)
    for kind in NAMES:
        manifest, result, src = build(kind)
        for suffix, content in (
            (".manifest.json", json.dumps(manifest, sort_keys=True, indent=2) + "\n"),
            (".diagnostic-result.json", json.dumps(result, sort_keys=True, indent=2) + "\n"),
            (".md", markdown(src, kind)),
        ):
            (out / (kind + suffix)).write_text(content, encoding="utf-8")
    print("SOURCE_ONLY_PRIMARY_AND_ADDENDUM_GENERATED")

if __name__ == "__main__":
    main()
