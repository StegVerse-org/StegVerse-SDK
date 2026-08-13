# Production Validation Route — 2026-08-13

State: CODE_COMPLETE_PENDING_HOSTED_DEPLOY_AND_INTEGRATED_RUN

Installed route:

SDK -> Core-Lite manifested route carrier -> Master Records route custody -> deployed StegCore manifested validation -> canonical StegGate -> exact-run Master Records custody -> Core-Lite return -> SDK return.

Merged dependencies:

StegCore manifested validation endpoint: 083557adec1bdbace09ebd10fb0765eb8e9a9d08
Core-Lite manifested route carrier: 72bdb0f110031ccc2cd98b8ebb7c22b1ab7326f8
Master Records route and operation custody: d0828441f2e92de736df1123bad5668f67e935fc

StegCore PR #90 passed all five required repository workflows before merge.

Hosted deployment status:

The existing Render steggate-core service attempted to deploy the merged StegCore commit, but Render canceled the build before execution because the workspace had exhausted build-pipeline minutes for the billing period.

Therefore the new live manifested-validation endpoint is not yet active, the cross-repository hosted run has not yet executed, and no new evaluator receipt IDs have been issued from that route.

Earlier local or ephemeral receipt IDs must not be substituted for the hosted production-validation run.
