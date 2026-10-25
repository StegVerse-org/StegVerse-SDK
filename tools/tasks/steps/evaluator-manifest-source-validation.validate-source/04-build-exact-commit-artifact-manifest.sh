set -eu
cd /tmp/source
python scripts/build_evaluation_boundary_artifact_manifest.py \
  --archive-source \
  --source-commit "${SOURCE_SHA}" \
  --source-branch "${SOURCE_REF}" \
  --output /tmp/evaluation-boundary-artifacts.json
cat /tmp/evaluation-boundary-artifacts.json
