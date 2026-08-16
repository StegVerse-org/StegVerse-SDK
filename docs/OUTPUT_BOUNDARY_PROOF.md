# Credentialless Output-Boundary Proof

`stegverse-output-proof` lets a user test an externally generated model response through the StegVerse SDK without transferring the provider API key to StegVerse.

## Purpose

The proof surface is designed for the production-artifact test path that supports the seven-lane StegVerse cost analysis and the portable S/NS adoption model.

The provider relationship remains outside StegVerse:

```text
user/application -> provider -> candidate output -> StegVerse SDK proof boundary
```

StegVerse receives the candidate, not the provider credential.

## Input

```json
{
  "deployment_class": "S",
  "provider": "openai",
  "model": "your-model-name",
  "prompt": "the prompt used with the provider",
  "output": "the provider output",
  "declared_intent": "research_note",
  "consequence_level": "medium",
  "provider_api_key_transferred_to_stegverse": false
}
```

`deployment_class` must be `S` or `NS`.

`NS` selects the Node Sovereign profile for the proof context. It does not grant Node Sovereign membership.

## Run

```bash
stegverse-output-proof --input candidate.json
```

The generic SDK surface registry also exposes `output-boundary-proof` for discovery.

## Evidence returned

The result binds:

- provider/model identity;
- prompt and output hashes;
- a stable candidate hash;
- StegVerse admissibility decision projection;
- an admissibility receipt reference;
- preserved-packet replay proof;
- semantic reconstruction proof;
- explicit provider-credential non-possession;
- S/NS selection;
- explicit `node_sovereign_membership_granted: false`.

## Replay meaning

The local proof re-evaluates the exact preserved tester packet through the existing SDK admissibility evaluator and compares the stable decision projection. Timestamps are not used as the replay equality condition.

This local proof is distinct from canonical Master Records replay by `manifest_receipt_id`. Canonical replay remains available through the sovereign governance path.

## Reconstruction meaning

The proof independently rebuilds the LLM tester packet from the candidate evidence and checks the stable object identity, provider/model identity, prompt/output hashes, and decision projection.

This semantic reconstruction is intentionally distinguished from canonical sovereign state reconstruction through Master Records custody.

## Authority boundary

```text
output-boundary proof != provider authority
output-boundary proof != execution authority
output-boundary proof != publication authority
S proof != ecosystem node membership
NS proof/profile != Node Sovereign membership
provider API key possession by StegVerse == false
```

## Seven-lane relationship

The canonical Generation-2 seven-lane cost experiment is owned by:

```text
GCAT-BCAT-Engine/workflows
experiments/sv-cost-program/seven-lane-results/
```

That experiment uses the same architecture: one externally generated provider candidate is compared as a raw observation and as the same candidate passed through StegVerse governance, while StegVerse never consumes the provider API key.
