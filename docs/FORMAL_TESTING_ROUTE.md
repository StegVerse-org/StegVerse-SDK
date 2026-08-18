# Formal Testing Route

`StegVerse-org/StegVerse-SDK` is the generalized user/evaluator-facing testing boundary for the StegVerse ecosystem.

## Canonical generalized evaluator surface

The canonical governed evaluator path is evaluator-neutral. A tester declares the WHAT, HOW, and WHY of an experiment through the published SDK manifest contract; the SDK validates/canonicalizes the declaration and routes only published capabilities through the existing governed system.

```text
Evaluator / test harness
→ StegVerse SDK manifest ingress (0B / stegverse.ingress-manifest.v1)
→ Core-Lite manifested route carrier
→ Master Records checkpoint custody
→ StegCore manifested transaction
→ canonical StegGate + commit-coherence evaluation
→ Master Records exact-run custody
→ return ingestion/CGE
→ Master Records return custody
→ SDK return
→ Evaluator
```

This is the generalized governed testing surface. It is not specific to any evaluator, study, participant, or experiment package.

### Generalization invariant

```text
evaluator-specific test definition != evaluator-specific route
test manifest != new execution authority
configuration != augmentation
published capability selection != hot-patched semantics
unsupported requested capability -> reject before execution
new required capability -> develop/version/publish generally before use
```

An evaluator may vary experiment metadata, inputs, requested published capabilities, requested evidence, rationale, and expected observations. Those declarations do not create a private route, a private evaluator implementation, a new StegGate semantic, or a new custody path.

A named experiment such as ODA3 is therefore a test instance/package submitted through this generalized surface. It is not a canonical SDK lane and must not acquire evaluator-specific runtime machinery inside the SDK.

## Sandbox / batch-data route

The repository also documents a bounded sandbox-data loop used when a published experiment explicitly requires ephemeral sandbox/CGE batch execution:

```text
User / evaluator
→ StegVerse SDK or LLM Adapter intake
→ StegVerse-org ingestion
→ StegGhost/entity-sandbox-runner ingestion/CGE
→ ephemeral sandbox batch
→ StegGhost/entity-sandbox-runner return validation
→ StegVerse-org ingestion
→ User / evaluator
```

This is a specialized execution capability behind the generalized testing surface, not a replacement for the generalized SDK evaluator contract and not the mandatory route for every formal test.

A generalized evaluator manifest may request the sandbox capability only when that capability is published and representable in the SDK contract. The manifest may not synthesize or bypass the capability merely because a particular experiment wants it.

## Master Records receipt rule

Every governed route leg that crosses an ingestion, execution, consequence, replay, reconstruction, or return boundary must retain the receipts required by that published route. The generalized SDK route uses canonical MRR/MR/MRO custody according to the current runtime contract. The sandbox/batch route additionally requires action receipts at its own ingestion and return checkpoints.

For the sandbox/batch route, required receipt emitters are:

| Step | Ingestion point | Required Master Records action receipt |
|------|-----------------|----------------------------------------|
| 1 | `StegVerse-org/StegVerse-SDK` or LLM Adapter | user/evaluator intake receipt |
| 2 | `StegVerse-org ingestion` | org intake route receipt |
| 3 | `StegGhost/entity-sandbox-runner ingestion/CGE` | sandbox intake/CGE receipt |
| 4 | `ephemeral sandbox batch` | ephemeral execution receipt |
| 5 | `StegGhost/entity-sandbox-runner ingestion/CGE return validation` | sandbox return/CGE receipt |
| 6 | `StegVerse-org ingestion` | org return intake receipt |
| 7 | `User/evaluator return` | delivery receipt |

No route may claim a successful governed transition when a receipt required by that route is absent.

## Evaluation consumers

Public demo, formal runner, standing-proof, GLM/boundary studies, ODA3, and future evaluators consume the generalized manifest/receipt contract. They may request different published capabilities or evidence profiles, but they do not become separate SDK execution architectures.

| Evaluation consumer | Position |
|---------------------|----------|
| Public demo validation | Consumes generalized receipt-bound results for public demonstration. |
| Formal demo runner | Consumes generalized manifested formalism packets after intake. |
| Standing proof | Consumes receipt-bound standing artifacts after governed intake. |
| Boundary / GLM case | Consumes generalized boundary declarations after applicable clearance. |
| ODA3 | Supplies an experiment manifest/package through the same generalized SDK surface. |
| Future evaluator | Uses the same published manifest/capability/evidence contract. |

## Rule

```text
The SDK is the generalized testing surface.
Evaluators provide experiment definitions as data/configuration.
The published runtime provides execution semantics.
Master Records provides required custody/evidence.
Specialized capabilities may be selected when published.
No evaluator gets a custom SDK lane merely by naming a test.
```
