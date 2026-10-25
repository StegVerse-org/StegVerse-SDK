set -eu
cd /tmp/source
python -m pytest -q \
  tests/test_portable_governance_verifier.py \
  tests/test_portable_governance_verifier_cli.py \
  tests/test_portable_governance_exchange.py \
  tests/test_reference_bounded_consequence.py \
  tests/test_post_return_evidence.py \
  tests/test_organization_ledger_evidence.py \
  tests/test_proof_release_gate.py
python -m unittest -v tests.test_organization_batch_manifest_task_binding
