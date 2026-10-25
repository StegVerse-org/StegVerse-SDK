cd /tmp/source
python - <<'PY'
from pathlib import Path
text = '\n'.join(Path(p).read_text(encoding='utf-8') for p in (
    'stegverse/post_return_production_runner.py',
    'scripts/run_post_return_production_proof.py',
))
for name in (
    'GITHUB_TOKEN',
    'GH_TOKEN',
    'TVC_PRIVATE_SOURCE_READ_TOKEN',
    'TVC_EPHEMERAL_GITHUB_TOKEN',
):
    assert name not in text, f'credential surface introduced: {name}'
assert 'verify_release_proof_capabilities' in text
assert 'build_standing_execution_context' in text
assert 'complete_post_return_evidence' in text
assert 'organization_ledger_readback' in text
print('POST_RETURN_PRODUCTION_RUNNER_NON_AUTHORIZING_SOURCE_OK')
PY
