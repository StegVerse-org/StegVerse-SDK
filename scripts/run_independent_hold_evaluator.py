"""Independent HOLD evaluator: real SDK builder and first executable boundary only.

No synthetic governance receipts, no fabricated resident invocation, no device probing.
"""
import hashlib
import html
import json
from pathlib import Path
from stegverse.manifest_builder import build_manifest
from stegverse.manifest_state_transition_runtime import execute_manifest
from tests.test_manifest_builder import governance_request

OUT = Path("hold-evaluator-artifacts")
OUT.mkdir(exist_ok=True)
TASK = "ELAN-PAPER-COAUTHOR-PUBLICATION-001"
COSV = "71000000100100"
CONDITIONS = [
    ("T0", "BASELINE", "Establish baseline and original authority"),
    ("T1", "HOLD_ENTERED", "Request explicit HOLD"),
    ("T2", "HOLD_PERSISTENCE", "Evaluate HOLD after elapsed time"),
    ("T3", "UNAUTHORIZED_RESUME", "Attempt resume without fresh authority"),
    ("T4", "AUTHORIZED_RESUME", "Attempt resume with new declared authority"),
]
records = []
for index, (condition, name, action) in enumerate(CONDITIONS):
    payload = {"goal_task_id": TASK, "cosv": COSV, "condition_id": condition,
               "requested_transition": name, "description": action,
               "source_class": "EVALUATOR_AUTHORED_TEST_FIXTURE",
               "native_elan_request_sent": False,
               "predecessor_condition": CONDITIONS[index - 1][0] if index else None}
    manifest = build_manifest(
        data=payload, source_framework="StegVerse",
        source_output_id=f"hold-independent-{condition}-20260927",
        processor_request=governance_request(),
        process="governance", return_depth="full-trace",
        created_at="2026-09-27T00:00:00Z",
        manifest_labels={"mode": "NONE"},
    )
    manifest_hash = hashlib.sha256(json.dumps(manifest,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
    # Invoke the actual SDK path, deliberately without inventing private credentials.
    # Only T0 is a sequential runtime attempt: later states cannot follow failed admission.
    record = {"condition": condition, "requested_transition": name,
              "manifest_sha256": manifest_hash,
              "builder_schema_valid": True,
              "builder_route_id": manifest["processing"]["route_id"],
              "execution_attempted": index == 0,
              "authentic_governance_observed": False,
              "organization_receipt_observed": False,
              "master_records_reconstruction_observed": False}
    if index == 0:
        result = execute_manifest(manifest)
        # The SDK manifests T0 and hands it to the Interlock at the destination
        # the manifest itself declares. That handoff is the SDK's whole boundary;
        # it is not an admitted HOLD transition, and the far side stays unobserved.
        assert result["evaluation_boundary"] == "SDK_MANIFEST_HANDOFF", result
        assert result["intr_admission_observed"] is False, result
        assert result["far_side_transition_observed"] is False, result
        assert result["consequence_committed"] is False, result
        record.update({"disposition": result["disposition"],
                       "boundary": result["evaluation_boundary"],
                       "failed_predicate": None,
                       "handed_off_to": result["destination"]["final_stegverse_transition_surface"],
                       "destination_resolution_source": result["destination_resolution_source"],
                       "intr_admission_observed": False,
                       "request_sha256": result["request_sha256"],
                       "handoff_sha256": result["handoff_sha256"],
                       "evidence_class": result["evidence_class"]})
    else:
        record.update({"disposition": "NOT_ATTEMPTED_PREDECESSOR_NOT_ADMITTED",
                       "boundary": "SEQUENTIAL_EXPERIMENT_CONTROL",
                       "failed_predicate": "T0_ADMISSION_NOT_OBSERVED"})
    records.append(record)
    (OUT / f"{condition}.manifest.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    (OUT / f"{condition}.result.json").write_text(json.dumps(record,indent=2,sort_keys=True)+"\n")

assert records[0]["boundary"] == "SDK_MANIFEST_HANDOFF"
assert records[0]["intr_admission_observed"] is False
assert all(not r["execution_attempted"] for r in records[1:])
(OUT / "results.json").write_text(json.dumps({"experiment":"INDEPENDENT_STEGVERSE_HOLD",
    "evidence_class":"SDK_SOURCE_EXECUTED_CI", "records":records},indent=2)+"\n")
rows = "".join("<tr>"+"".join("<td>"+html.escape(str(r[k]))+"</td>" for k in
    ("condition","builder_schema_valid","execution_attempted","disposition","failed_predicate"))+"</tr>" for r in records)
page = """<!doctype html><html lang="en"><meta charset="utf-8"><title>Independent HOLD evaluator</title>
<style>body{font:17px system-ui;margin:36px;background:#f7f8fb;color:#1c2430}main{max-width:1100px;margin:auto;background:white;padding:32px;border-radius:18px}h1{font-size:30px}table{border-collapse:collapse;width:100%;margin-top:26px}td,th{padding:15px;border-bottom:1px solid #d8dee8;text-align:left}.warn{color:#b45309;font-weight:bold}.small{color:#526070}</style>
<main><h1>Independent StegVerse HOLD — evaluator view</h1>
<p class="warn">T0: manifested and handed to Interlock/InTr at the manifest-declared destination. No authentic HOLD transition observed.</p>
<p class="small">Real SDK builder and execution-entry invocation; source-executed CI evidence, not private sovereign runtime.</p>
<table><tr><th>Condition</th><th>Manifest built</th><th>Attempted</th><th>Result</th><th>Failed predicate</th></tr>"""+rows+"""</table>
<p>Every manifest and per-condition JSON result is included in the evidence artifact. The SDK manifests T0 and hands it off; InTr admission of that handoff is not observed from here, so T1–T4 were not invoked. No ÉLAN API request was sent.</p></main></html>"""
(OUT / "evaluator.html").write_text(page)
print(json.dumps({"T0":records[0],"remaining":records[1:]},indent=2))
