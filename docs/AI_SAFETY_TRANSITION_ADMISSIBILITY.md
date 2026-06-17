# AI Safety to Transition Admissibility

**Status:** SDK positioning cross-reference  
**Generated:** 2026-06-17  
**Canonical public copy:** `StegVerse-Labs/Site/docs/public-positioning/ai-safety-to-transition-admissibility.md`

---

## Purpose

This note records how the public AI-safety positioning artifact relates to `StegVerse-org/StegVerse-SDK`.

The SDK exposes developer-facing primitives for submitting action intent, evaluating admissibility, attaching receipt references, and verifying governed admissibility bundles.

The canonical public essay lives in the Site repository. This SDK note explains how developers should interpret the same concept when using SDK helpers.

---

## SDK Relationship

The public positioning claim is:

> Prior evaluation is not commit-time standing.

For SDK users, that means:

- do not treat a model output as executable merely because it appears safe;
- do not treat prior review as current authority;
- submit action intent into the admissibility path before execution;
- attach or verify receipt references when a transition becomes consequential;
- preserve explicit non-claims in generated bundles and receipts.

---

## Developer Rule

A governed SDK integration should follow this pattern:

```text
proposed action
→ structured intent or admissibility packet
→ local or remote admissibility evaluation
→ allow | deny | defer
→ execution only after allow
→ receipt or receipt reference retained for replay
```

The SDK must not collapse proposal, evaluation, execution, and proof into a single implicit step.

---

## Associated Components

| Component | Role |
|---|---|
| SDK | Developer-facing integration surface |
| StegCore | Commit-time decision and admissibility posture |
| Admissibility Receipt | Portable proof envelope and verifier |
| GLM | Machine-readable boundary declaration |
| EVIDE | Post-event reconstructability |
| Site | Public mirror and canonical publication surface |

---

## Use in Future Work

Future SDK examples should cite the canonical Site document when explaining why developer integrations need commit-time admissibility rather than post-hoc audit alone.
