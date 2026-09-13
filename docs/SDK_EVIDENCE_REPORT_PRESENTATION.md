# SDK Evidence Report Presentation

## Purpose

Publisher is the canonical presentation/evidence-assembly stage of a **complete communication manifest** whenever the initiating request requires a presentation, report, or evaluator-facing evidence package.

Publisher is not out-of-band post-processing. It consumes authentic evidence retained by the governed run and renders only what the complete manifest declares. Publisher does not become governance authority, processing-selection authority, transport authority, or evidence-creation authority.

Canonical southbound lifecycle:

```text
manifested processing
-> required governed transitions / counterparty round trips
-> canonical custody + replay/reconstruction when declared
-> Publisher presentation/evidence stage when declared
-> Publisher output returned to SDK
-> SDK binds output to original request + initiating entity
-> applicable final StegVerse-side egress transition
-> Interlock/InTr egress
-> far-side Interlock/InTr transition
-> initiating entity receives the manifested result/evidence projection
```

For an external-framework path using LLM Adapter, the last StegVerse-side sequence is:

```text
Publisher -> SDK return assembly -> LLM Adapter -> Interlock/InTr -> far-side transition
```

LLM Adapter is the final **StegVerse-side** transition surface in that path; it is not the terminal communication transition. Terminal communication state requires the far-side Interlock/InTr transition.

## Complete-manifest declaration

New builder-generated `stegverse.ingress-manifest.v1` objects carry a `completion` block that binds:

- `direction = SOUTH`;
- original initiator class/ref;
- Publisher stage declaration and package profile;
- final StegVerse-side egress transition surface;
- `transport = INTERLOCK_INTR`;
- `far_side_transition_required = true`.

Legacy v1 manifests may omit `completion` for backward compatibility, but omission means they are not classified as complete communication manifests.

When `completion.publisher.required=true`, the governed lifecycle is not presentation-complete until Publisher has assembled the declared package from authentic retained evidence and returned its package identity/reference to SDK.

## What gets rendered

A manifest-declared report package can include:

- abstract and test objective;
- frozen test parameters;
- manifest and processing-path information;
- pre-registered evidence expectations;
- primary execution and result;
- counterparty/evaluator round-trip evidence;
- replay and replay result;
- reconstruction and reconstruction result;
- evaluator-facing screenshots;
- conclusion;
- evidence ledger;
- SDK/function overview and usage instructions;
- roadmap and future-development notes.

Publisher may not invent missing evidence merely because the manifest requests a report field.

## Evaluator flow

A complete evaluator-facing flow is:

1. prepare source-native data;
2. build the complete canonical manifest;
3. select the installed processing capability and route;
4. declare initiator, Publisher requirements, and egress completion contract;
5. pre-register expected evidence fields where required;
6. freeze applicable test parameters/evidence expectations;
7. submit through the published SDK route;
8. execute the manifest-selected governed processing and required InTr round trips;
9. retain canonical evidence, replay, and reconstruction where declared;
10. Publisher consumes the authentic retained evidence basis;
11. Publisher assembles the declared presentation/evaluator package;
12. Publisher output returns to SDK;
13. SDK binds it to the original request and initiating entity;
14. the applicable final StegVerse-side egress transition occurs;
15. Interlock/InTr egress occurs;
16. the far-side Interlock/InTr transition completes the communication;
17. the initiating entity receives the requested projection.

## Evidence and completion boundary

Publisher may render `DRAFT` or `IN_PROGRESS` packages when the manifest and package contract permit those states, but such rendering does not imply missing governed stages occurred.

A Publisher package marked `COMPLETE` must fail closed unless the evidence stages required by its manifest/package profile are represented by authentic retained references.

`PUBLISHER_STAGE_COMPLETE` is not `COMMUNICATION_COMPLETE`. SDK return assembly, the applicable final StegVerse-side transition, Interlock/InTr egress, and the required far-side transition remain distinct later states.

Presentation screenshots do not become retroactive runtime evidence.

## SDK return boundary

Publisher output returns to SDK as the presentation/evidence product of the **same manifest lifecycle**. SDK binds the Publisher output to:

- original manifest/request identity;
- original initiating entity identity/correlation;
- package identity/digest or retained reference;
- requested return projection;
- evidence/custody references;
- manifest-declared egress surface.

Publisher output is not automatically a new processing request. A new processing cycle exists only when a new admitted manifest explicitly requests additional processing.

## Output formats

Publisher may render the common evidence basis as PDF, HTML, DOCX, Markdown, JSON, or another explicitly supported package representation. Format changes presentation, not evidence meaning or authority.

Generated artifacts remain subject to their applicable publication policy; presentation assembly is distinct from public publication authority.

## Publisher implementation

Canonical renderer repository:

`GCAT-BCAT-Engine/Publisher`

Canonical package schema:

`stegverse.publisher.evidence-report-package/v1`

Global lifecycle contract:

`StegVerse-Labs/.github/docs/CANONICAL_SOUTHBOUND_COMMUNICATION_LIFECYCLE.md`
