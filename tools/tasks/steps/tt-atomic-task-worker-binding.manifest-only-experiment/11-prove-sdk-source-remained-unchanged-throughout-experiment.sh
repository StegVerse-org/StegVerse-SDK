git rev-parse HEAD | tee /tmp/sdk-after-head.txt
diff -u /tmp/sdk-frozen-head.txt /tmp/sdk-after-head.txt
git status --porcelain --untracked-files=all | tee /tmp/sdk-after.status
test ! -s /tmp/sdk-after.status
git ls-files -s | LC_ALL=C sort > /tmp/sdk-source-index.after.txt
diff -u /tmp/sdk-source-index.txt /tmp/sdk-source-index.after.txt
sha256sum /tmp/test1.manifest.json /tmp/test2.manifest.json /tmp/test3.manifest.json /tmp/task4.manifest.json \
  /tmp/test1.result.json /tmp/test2.result.json /tmp/test3.result.json /tmp/task4.result.json \
  /tmp/test1.readiness-evidence.json /tmp/test2.readiness-evidence.json \
  /tmp/test3.readiness-evidence.json /tmp/task4.readiness-evidence.json \
  /tmp/sdk-source-index.txt /tmp/experiment-metadata.json /tmp/sdk-task4-group.processor-request.json \
  /tmp/pip-freeze.txt /tmp/experiment-stage-results.log \
  | tee /tmp/experiment-sha256.txt
