# SDK Core-Node Unified Comparison Result

Request: `sdk-core-node-fanout-sample-001`  
Package: `sample-package-001`  
Baseline: `PATH-1`  
Runtime: `StegVerse-org/core-node-runtime-demo`

## Path comparison

| Path | Status | Elapsed ms | Memory MB | Cost USD | Receipts | Warning state | Summary |
|---|---:|---:|---:|---:|---:|---|---|
| PATH-1 | PASS | 18.9 | 24.0 | 0.0001 | 3 | none | Cross-org ingestion baseline completed successfully. |
| PATH-2 | PASS | 11.4 | 18.0 | 0.00008 | 6 | none | Fixed-capacity core-node path completed successfully. |
| PATH-3 | PASS | 9.7 | 14.5 | 0.00007 | 7 | none | Minimal delegated micro-node path completed successfully. |
| PATH-4 | PASS | 10.8 | 16.0 | 0.00009 | 8 | none | Return-path memory micro-node path completed successfully. |
| PATH-5 | PASS | 10.1 | 15.2 | 0.00007 | 7 | none | Adaptive transition-cell assembly path completed successfully. |

## Witness references

- `master-records-package-observed-sample-001`
- `master-records-fanout-observed-sample-001`
- `master-records-comparison-observed-sample-001`
- `master-records-return-observed-sample-001`

## Human result shape

```text
path_id
result_status
elapsed_time_ms
memory_peak_mb
estimated_cost_usd
receipt_count
failure_or_warning_state
human_readable_summary
```
