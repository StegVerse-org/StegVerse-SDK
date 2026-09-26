# Generic source-observation preflight — SDK 1.4 development

**Status:** Source-only capability proposed under PR #340, not a tagged/released runtime capability. **Purpose:** Any independent evaluator can submit its own source-native event sequence to an installed SDK processor without letting a client-observed no-request window masquerade as native model output. This is not an ÉLAN-only pipeline or a new governance engine.

## Public commands

```bash
python -m stegverse.source_observation \
  --input inspection/examples/source-observation-synthetic-hold.json \
  --output /tmp/source-preflight.json

stegverse manifest build \
  --input inspection/examples/source-observation-synthetic-hold.json \
  --processor-request inspection/examples/source-observation-synthetic-diagnostic-request.json \
  --source-framework synthetic_external_evaluator \
  --source-output-id synthetic-hold-demo-001 \
  --process ecosystem_diagnostic \
  --return-depth full-trace \
  --output /tmp/source-manifest.json
```

The bundled input is **synthetic, not an authentic ÉLAN or other provider trace**. A successful local preflight returns `READY_FOR_MANIFEST`, `native_source_authenticated=false`, `governed_result=false`. A malformed no-request event with a model output returns the exact input refusal `DENY: NO_INVOCATION_CANNOT_HAVE_PROVIDER_FIELDS`. This is a local source-validation disposition and not a live Interlock/InTr governance decision.

A provider-neutral `stegverse.source-observation.v1` payload has an experiment ID and ordered events. Each event declares stable ID, condition ID, predecessor if present, `source_class`, `request_sent`, outcome and client timing. Actual invoked responses require original prompt and exact returned text. `NO_INVOCATION` is client-only and cannot carry prompt, API status, provider ID or model output. An ellipsis is an exact string, an empty completed result has empty string, and a timeout is a client nonresult with no model output. Human annotation is separate. Predecessor IDs must point to earlier preserved events. The validator checks consistency of *supplied* records, not provider signature or truthfulness.

This profile is an **optional generic input format**: other native source classes still enter the same public Manifest Builder unchanged. The installed processor is selected explicitly with `processing.capability` and `processing.route_id`; this preflight creates neither a new route nor execution authority.

## Execution and custody boundaries

Only after a native original is captured and privately preserved may an evaluator submit it through its declared installed route. Any `run-manifest` call must return the **actual** existing Universal InTr transition disposition, not a synthetic success substituted by the preflight. If no authenticated runtime is available, preserve the first real `DENY`, `FAIL_CLOSED` or unavailable-origin disposition with exact correction requirements. A source-only example manifest is not proof of custody, replay/reconstruction, Publisher delivery or far-side return.

ÉLAN HOLD application: source collection may start immediately after joint protocol agreement and run **in parallel** with this SDK source work. Keep native provider output, no-request client timer and SDK-derived governance evidence as different observation sources; never rerun the historical Test 2 cross-evaluation script as corrected evidence because it embeds the superseded human-authored model-presence claim.

Canonical time-critical roadmap: `StegVerse-Labs/.github/docs/ELAN_HOLD_IMMEDIATE_EXECUTION_SDK_VERSION_ROADMAP.md`. A 1.4 development feature does not retarget the frozen 1.3.0 RC or confer release authority.
