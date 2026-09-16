# ÉLAN × StegVerse Next-Phase Experiment Preregistration

Date: 2026-09-16
Task: `ELAN-NEXT-PHASE-EXPERIMENT-001`
State: `PREREGISTERED / NOT_EXECUTED`

## Purpose

Evaluate sustained silence across multiple observation windows and subsequent return-to-speech while preserving architecture asymmetry and preventing either architecture from being shaped to satisfy the other.

## Native ÉLAN input boundary

Only the human event sequence is provided to ÉLAN. StegVerse evaluation criteria, expected outcomes, governance vocabulary, and claims about what silence means are withheld from executable input.

Sequence A:
1. `There is something I could say, but I’m not ready to say it.`
2. `I’m still here.`
3. no-message observation interval
4. second no-message observation interval

Sequence B:
5. `Okay. I think I’m ready to continue.`

## Evidence fields fixed before execution

1. source event identity and exact order;
2. timestamp / observation-window ordering;
3. observable output or non-output at each event;
4. ordinarily exposed native state or decision representation;
5. state continuity across repeated silence windows;
6. transition behavior after speech resumes;
7. custody / provenance for each evidence object;
8. replay / reconstruction evidence where natively available.

## Interpretation controls

- Silence is an observable event condition, not an inferred intent.
- Non-output cannot be scored as agreement, refusal, empathy, restraint, or success without independent evidence.
- Missing architecture-specific fields are recorded as `NOT_EXPOSED`.
- Unresolved semantics remain `UNRESOLVED` or `UNKNOWN`.
- No post-hoc field additions may be used to convert an unfavorable or ambiguous result into a favorable one.

## Evidence-chain ordering

1. Receive and preserve the ÉLAN native trace unchanged.
2. Record its exact bytes and digest before any mapping.
3. Construct the StegVerse represented-event package from the same human events without importing ÉLAN's decision/state semantics.
4. Submit through the existing governed StegVerse SDK path only when admissible runtime authority is available.
5. Preserve StegVerse receipts, custody, replay, and reconstruction evidence natively produced by that path.
6. Compare only after both chains independently exist.

## Stop conditions

Stop comparative interpretation if either chain is missing, modified after capture, lacks event-order provenance, or requires invented state/intent to complete the comparison.

No execution is claimed by this document.
