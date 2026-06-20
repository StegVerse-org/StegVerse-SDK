# Formal Testing Route

`StegVerse-org/StegVerse-SDK` is the canonical ingestion point for all formal testing datasets in the StegVerse ecosystem.

## Required Flow

```text
Dataset / fixture / governance artifact
→ StegVerse-org/StegVerse-SDK ingestion
→ manifest binding
→ receipt binding
→ declared formal testing route
→ route-specific result receipt
```

## Routes

| Route | Repository | Purpose |
|------|------------|---------|
| Public demo validation | `StegVerse-org/stegverse-demo-suite` | Reproducible public validation and explainable demos. |
| Formal demo runner | `StegVerse-org/demo-suite-runner` | GCAT/BCAT formalism probes and deterministic runner scenarios. |
| Sandbox testing | `StegGhost/entity-sandbox-runner` | Adversarial, entity, and bounded sandbox tests. |
| Standing proof | `StegVerse-Labs/Standing-Proof-Engine` | Commit-time standing, stale-state replay, and receipt verification. |
| Boundary / GLM case | `StegVerse-Labs/Boundary-Test` | Boundary declaration and manifest composability validation. |

## Rule

```text
SDK ingests.
GLM declares boundaries.
Demo-suite demonstrates.
Demo-suite-runner probes formalism behavior.
Sandbox stresses.
SPE proves standing.
Receipts bind every transition.
```

Each downstream route must preserve the SDK intake manifest and receipt reference in its route-specific result receipt.
