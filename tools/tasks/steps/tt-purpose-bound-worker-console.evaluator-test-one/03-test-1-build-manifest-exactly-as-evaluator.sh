stegverse manifest build \
  --input inspection/examples/sdk-tt-shared-source.json \
  --processor-request inspection/examples/sdk-test1-purpose-worker.processor-request.json \
  --source-framework external_evaluator \
  --source-output-id sdk-test-one-001 \
  --process purpose_bound_worker \
  --return-depth full-trace \
  --created-at 2026-09-19T19:45:00Z \
  --output /tmp/sdk-test1.manifest.json
