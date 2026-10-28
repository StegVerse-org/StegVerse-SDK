stegverse manifest build \
  --input inspection/examples/sdk-tt-shared-source.json \
  --processor-request inspection/examples/sdk-test1-purpose-worker.processor-request.json \
  --source-framework external_evaluator --source-output-id test-1 \
  --process purpose_bound_worker --return-depth full-trace \
  --created-at 2026-09-20T21:45:00Z --output /tmp/test1.manifest.json

stegverse manifest build \
  --input inspection/examples/sdk-tt-shared-source.json \
  --processor-request inspection/examples/sdk-test2-atomic-task-worker.processor-request.json \
  --source-framework external_evaluator --source-output-id test-2 \
  --process atomic_task_worker --return-depth full-trace \
  --created-at 2026-09-20T21:46:00Z --output /tmp/test2.manifest.json

stegverse manifest build \
  --input inspection/examples/sdk-tt-shared-source.json \
  --processor-request inspection/examples/sdk-test3-invariance-seam.processor-request.json \
  --source-framework external_evaluator --source-output-id test-3 \
  --process atomic_task_worker --return-depth full-trace \
  --created-at 2026-09-20T21:47:00Z --output /tmp/test3.manifest.json

stegverse manifest build \
  --input inspection/examples/sdk-tt-shared-source.json \
  --processor-request /tmp/sdk-task4-group.processor-request.json \
  --source-framework external_evaluator --source-output-id task-4 \
  --process purpose_bound_worker --return-depth full-trace \
  --created-at 2026-09-20T21:48:00Z --output /tmp/task4.manifest.json
