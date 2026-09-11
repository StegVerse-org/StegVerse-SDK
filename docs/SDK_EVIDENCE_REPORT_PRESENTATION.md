# SDK Evidence Report Presentation

## Contents

- [Purpose](#purpose)
- [What gets rendered](#what-gets-rendered)
- [Evaluator flow](#evaluator-flow)
- [Evidence and completion boundary](#evidence-and-completion-boundary)
- [Output formats](#output-formats)
- [Browser roadmap](#browser-roadmap)
- [Publisher implementation](#publisher-implementation)

## Purpose

The StegVerse SDK can supply a structured evaluator evidence package to the general `GCAT-BCAT-Engine/Publisher` evidence-report function. The renderer is domain-neutral: the SDK, MIR, ELAN, or another evaluator-facing program supplies authentic evidence; Publisher validates and renders it.

This presentation path does not change SDK governance semantics and does not create execution or publication authority.

## What gets rendered

A report package can include:

- abstract and test objective;
- frozen test parameters;
- manifest and processing-path information;
- pre-registered evidence expectations;
- primary execution and result;
- replay and replay result;
- reconstruction and reconstruction result;
- evaluator-facing screenshots;
- conclusion;
- evidence ledger;
- SDK/function overview and usage instructions;
- roadmap and future-development notes.

## Evaluator flow

A strong SDK evaluation presentation should make the entire path inspectable:

1. prepare source-native data;
2. build the canonical manifest;
3. select the installed processing capability and route;
4. pre-register expected evidence fields where the test contract requires it;
5. freeze the applicable test parameters and screenshot evidence;
6. submit through the published SDK route;
7. inspect the returned result and retained references;
8. replay the retained run;
9. reconstruct from retained evidence;
10. assemble the evidence package for independent review;
11. render the same canonical package into the requested presentation formats.

## Evidence and completion boundary

Publisher may render a `DRAFT` or `IN_PROGRESS` package while clearly showing unexecuted stages.

A package marked `COMPLETE` must fail closed unless authentic primary execution, replay, and reconstruction stages are all represented as executed with retained evidence references and the required screenshot evidence is present.

Presentation screenshots do not become retroactive runtime evidence. Screenshot classes distinguish pre-run frozen evidence, runtime evidence, and presentation-only captures.

## Output formats

The general Publisher function supports a common evidence basis rendered as:

- PDF;
- HTML;
- DOCX;
- Markdown;
- JSON.

Format changes presentation, not the meaning or authority of the evidence package. Generated artifacts remain `GENERATED_VALIDATED_NOT_PUBLISHED` until a separate publication process authorizes publication.

## Browser roadmap

The package-driven design is intended to support browser-friendly access to safely exposable SDK and report functions without creating a second SDK implementation. Planned browser-facing capabilities include manifest construction, processing-path selection, evidence-field registration, frozen digest display, request/result inspection, replay, reconstruction, evidence export, and receipt inspection with semantic parity to the programmatic path.

## Publisher implementation

Canonical renderer repository:

`GCAT-BCAT-Engine/Publisher`

General evidence-report contract:

`docs/GENERAL_EVIDENCE_REPORT_PIPELINE.md`

Canonical package schema:

`stegverse.publisher.evidence-report-package/v1`

The SDK supplies project-specific evidence/input packages; Publisher owns the reusable rendering function.
