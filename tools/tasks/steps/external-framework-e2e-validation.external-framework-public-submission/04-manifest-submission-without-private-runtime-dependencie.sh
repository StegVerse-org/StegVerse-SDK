set -eu
cd /tmp/source
stegverse external-run \
  --input inspection/examples/elan-relational-state-test1.json \
  --governance-request inspection/examples/elan-governance-request.example.json \
  --evaluation-declaration inspection/examples/elan-evaluation-declaration-test1.json \
  --source-framework ELAN \
  --source-output-id elan-emotional-ambiguity-silence-test-001 \
  --data-class elan.relational-state.v1 \
  --return-depth full-trace \
  --created-at 2026-10-10T00:00:00Z \
  --attempt-id "$(cat /tmp/readiness-attempt.txt)" \
  --readiness-evidence /tmp/elan-readiness-evidence.json \
  --readiness-keys /tmp/readiness-keys.json \
  --output /tmp/elan-sdk-submission.json
