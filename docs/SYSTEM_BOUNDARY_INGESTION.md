# System-Boundary Declaration Ingestion

## Purpose

`StegVerse-org/StegVerse-SDK` accepts a bounded system-boundary declaration describing model, orchestration, session, memory, environment, continuity, and authority surfaces.

The SDK validates declaration shape and non-claims. It does not determine consciousness, personhood, welfare status, admissibility, standing, or execution authority.

## Source contract

```text
StegVerse-Labs/admissibility-wiki
static/governance/system-boundary-declaration.schema.v0.1.json
```

SDK mirror:

```text
schemas/system-boundary-declaration.schema.v0.1.json
```

## SDK surfaces

```text
stegverse/system_boundary.py
tests/test_system_boundary.py
sdk.capabilities.json
```

## Manifest binding

A governed session or intake manifest may contain:

```json
{
  "system_boundary_declaration": {
    "schema_version": "0.1",
    "declaration_id": "sbd-example-001"
  }
}
```

The full declaration may be included directly or resolved through a governed evidence pointer. The manifest binding does not itself create persistence or authority.

## Receipt reference

A downstream receipt may refer to the validated declaration using:

```json
{
  "system_boundary_declaration_ref": "receipt://system-boundary/sbd-example-001"
}
```

The receipt reference must preserve the declaration identifier and evidence location. It does not convert a model output, continuity claim, or SDK validation result into execution authority.

## Required safeguards

```text
model_has_execution_authority: false
consciousness_claim: not_evaluated
personhood_claim: not_evaluated
welfare_claim: not_evaluated
```

A declaration claiming prior-state influence must identify at least one feedback path. A declaration claiming trajectory dependence must also acknowledge prior-state influence.

## Validation

```bash
pytest tests/test_system_boundary.py
```

Expected coverage:

```text
valid non-authorizing declaration: accepted
false continuity without feedback paths: rejected
model execution authority: rejected
missing commit boundary: rejected
consciousness claim: rejected
unexpected top-level fields: rejected
```

## Downstream runtime source

`StegVerse-org/LLM-adapter` is the intended runtime producer of declarations. The adapter must inventory configured surfaces and emit evidence-backed feedback paths rather than infer continuity from conversational language alone.

## Boundary

System-boundary validation is an operational architecture check. Recurrence, memory, state continuity, trajectory dependence, self-reference, or self-report do not establish consciousness, personhood, welfare standing, admissibility, or execution authority.
