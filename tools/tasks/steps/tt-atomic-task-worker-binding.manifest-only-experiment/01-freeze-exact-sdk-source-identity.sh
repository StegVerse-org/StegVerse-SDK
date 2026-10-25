git rev-parse HEAD | tee /tmp/sdk-frozen-head.txt
git status --porcelain --untracked-files=all | tee /tmp/sdk-before.status
test ! -s /tmp/sdk-before.status
git ls-files -s | LC_ALL=C sort > /tmp/sdk-source-index.txt
sha256sum /tmp/sdk-source-index.txt | tee /tmp/sdk-source-index.sha256
python - <<'PY'
import json, pathlib, subprocess
sha = pathlib.Path('/tmp/sdk-frozen-head.txt').read_text().strip()
version = json.loads(pathlib.Path('VERSION.json').read_text()) if pathlib.Path('VERSION.json').exists() else {}
pathlib.Path('/tmp/experiment-metadata.json').write_text(json.dumps({
    'schema':'stegverse.sdk.four-stage-manifest-experiment.v2',
    'sdk_commit':sha,
    'sdk_version':version,
    'per_stage_variable_execution_input':'manifest_only',
    'test3_semantics':'same installed atomic-task-worker processor; distinct manifested identity and preregistered proposition; intended invariance/person-neutrality test',
    'task4_overlap_semantics':'overlap of measured local invocation intervals after both group barriers with an explicit 10ms observation dwell; serialized invocation control must falsify overlap; this does not claim CPU-parallel instruction execution',
    'worker_route_surface':'SDK_LOCAL_SEMANTIC_DEMONSTRATION',
    'readiness_evidence':'SIGNED_FIXTURE_INVOCATION_BOUND_NOT_LIVE_OBSERVATION',
    'historical_preregistration_anchor':'StegVerse-Labs/.github@0127082e415fb220c709962ab7d0645e06105a4c',
    'historical_preregistration_sha256':'37363e0d3d8880956b0e97a90c54a140e6bebfac0aa9be73a5fb90ab2effa5d7',
    'historical_run_35547155843_attempt1_disposition':'SUCCESS'
}, sort_keys=True, indent=2) + '\n')
PY
