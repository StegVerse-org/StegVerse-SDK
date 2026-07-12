# Governed vs Recursive LLM Comparison

## Purpose

This SDK contract prepares one normalized request for matched execution through:

1. a StegVerse governed route; and
2. an external recursive LLM route.

The comparison is intended for the future Ecosystem Chat proving surface. It allows both result quality and operational behavior to be compared without treating SDK intake as execution authority.

## Initial comparison dimensions

```text
DeltaCost       total route cost difference
DeltaLatency    end-to-end latency difference
DeltaCalls      model-call difference
DeltaTokens     input and output token difference
DeltaTools      tool-call difference
DeltaRetries    retry/correction-loop difference
DeltaNodes      node or transition-cell activation difference
DeltaReceipts   receipt/evidence-artifact difference
DeltaStanding   supported-claim and admissibility posture difference
```

## Required fairness invariants

Each route must receive the same:

- normalized user intent;
- task identity;
- evidence package;
- output requirements;
- measurement boundary;
- completion condition.

Provider-specific formatting may differ, but it may not silently change the requested task.

## Evidence classes

Every metric must be classified as one of:

```text
MEASURED      emitted by an actual route trace
CONFIGURED    supplied as a scenario or test parameter
DERIVED       calculated from other classified values
UNAVAILABLE   not present or not admissible for comparison
```

Configured or scenario-derived consequence values may not be displayed as measured inference savings.

## SDK example

```python
from stegverse.llm_route_comparison import (
    ComparisonRequest,
    ComparisonRoute,
    build_comparison_package,
    required_default_metrics,
)

metrics = required_default_metrics()
request = ComparisonRequest(
    comparison_id="cmp-001",
    normalized_input={"prompt": "Assess whether this transition may execute."},
    task_identity="transition-admissibility-assessment",
    output_requirements={"format": "json", "decision_required": True},
    routes=[
        ComparisonRoute(
            route_id="stegverse-governed",
            route_kind="STEGVERSE_GOVERNED",
            provider="stegverse",
            model="ecosystem-llm",
            execution_target="core-node-runtime-demo",
            governance_profile="transition-table-native",
            recursion_enabled=False,
            telemetry_required=metrics,
        ),
        ComparisonRoute(
            route_id="external-recursive",
            route_kind="EXTERNAL_RECURSIVE",
            provider="external",
            model="provider-selected",
            execution_target="llm-adapter",
            governance_profile="comparison-observed",
            recursion_enabled=True,
            telemetry_required=metrics,
        ),
    ],
    metrics_requested=metrics,
)

package = build_comparison_package(request)
```

## Current boundary

This increment creates the SDK-side comparison package and metric discipline. It does not yet:

- call an external provider;
- execute the core-node runtime;
- duplicate a live Ecosystem Chat request;
- calculate live deltas;
- issue a master-record receipt;
- prove that either route is cheaper, faster, or more accurate.

## Next integration path

```text
Ecosystem Chat
-> StegVerse-SDK comparison package
-> governed route + recursive route
-> common telemetry envelope
-> returned comparison result
-> delta calculation
-> comparison receipt
-> browser visualization
```

The runtime and provider adapter must return actual traces in a shared result schema before public comparative claims are activated.
