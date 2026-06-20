# Testing Data Loop Handoff

## Status

```text
handoff_status: ready_for_external_workflow_observation
implementation_posture: operationally_wired
remaining_gap: live workflow-run metadata input
```

## Built Route

```text
User
→ StegVerse-org/StegVerse-SDK or LLM Adapter
→ StegVerse-org ingestion
→ StegGhost/entity-sandbox-runner ingestion/CGE
→ ephemeral sandbox batch
→ StegGhost/entity-sandbox-runner ingestion/CGE return validation
→ StegVerse-org ingestion
→ User / downstream evaluation route
```

## Implemented Artifacts

```text
docs/TESTING_DATA_LOOP_CONTRACT.md
docs/TESTING_DATA_LOOP_STATUS.md
docs/TESTING_DATA_LOOP_STATUS_INGESTION.md
schemas/testing-data-loop.schema.json
schemas/testing-data-loop-handoff.schema.json
schemas/testing-data-loop-status.schema.json
examples/testing_data_loop.json
examples/testing_data_loop_handoff.json
examples/testing_data_loop_status.json
examples/testing_data_loop_workflow_observations.json
scripts/validate_formal_testing_route.py
scripts/ingest_testing_data_loop_status.py
```

## Execution Companions

```text
StegVerse-org/demo_ingest_engine/scripts/run_org_ingestion_step.py
StegVerse-org/demo_ingest_engine/scripts/run_testing_data_loop_demo.py
StegVerse-org/demo_ingest_engine/scripts/validate_testing_data_loop_chain.py
StegGhost/entity-sandbox-runner/scripts/run_sandbox_step.py
```

## Downstream Contract Coverage

```text
StegVerse-org/stegverse-demo-suite/docs/TESTING_DATA_LOOP_CONTRACT.md
StegVerse-org/demo-suite-runner/docs/TESTING_DATA_LOOP_CONTRACT.md
StegVerse-Labs/Standing-Proof-Engine/docs/testing_data_loop_contract.md
StegVerse-Labs/Boundary-Test/docs/testing_data_loop_contract.md
```

## Next Valid Action

Export real workflow-run observations into:

```text
examples/testing_data_loop_workflow_observations.json
```

Then run:

```bash
python scripts/ingest_testing_data_loop_status.py \
  --status examples/testing_data_loop_status.json \
  --observations examples/testing_data_loop_workflow_observations.json \
  --output /tmp/testing_data_loop_status.json

python scripts/validate_formal_testing_route.py --kind status /tmp/testing_data_loop_status.json
```

## Completion Criterion

The route may be marked externally confirmed when workflow metadata is visible for the relevant repositories and the observed workflow conclusions support the installed route checks.
