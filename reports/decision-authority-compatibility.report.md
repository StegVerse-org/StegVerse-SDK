# Decision Authority Compatibility Report

## Repository

`StegVerse-org/StegVerse-SDK`

## Canonical Source

`StegVerse-Labs/repo-standards/schemas/decision-authority.schema.json`

## Scan Observation

Repository search did not detect an obvious local decision enum for:

```text
ALLOW
DENY
DEFER
QUARANTINE
FAIL_CLOSED
ADVISORY_ONLY
decision
```

The SDK README describes validation results and non-authorizing status, but does not currently establish a local ST-004 authority enum.

## Compatibility Posture

```text
local_decision_enum_detected: false
compatibility_status: RESERVED_MAPPING_INSTALLED
```

## Reserved Mapping

| SDK/local value | ST-004 authority value |
| --- | --- |
| `ALLOW` | `allowed` |
| `DENY` | `denied` |
| `DEFER` | `requires-human-review` |
| `ADVISORY_ONLY` | `advisory-only` |
| `FAIL_CLOSED` | `fail-closed` |

## Boundary

SDK validation results are not ST-004 transition authority unless explicitly mapped to the canonical authority vocabulary and supported by policy, delegation, evidence, and validation.
