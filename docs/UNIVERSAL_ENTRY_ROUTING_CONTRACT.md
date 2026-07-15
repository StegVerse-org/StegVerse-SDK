# Universal Entry Routing Contract

## Purpose

Every StegVerse entry point MUST normalize accepted input into `stegverse.universal_entry_envelope.v0.1` before capability routing. The Ecosystem Chat window is one adapter into this path; it is not the owner of routing semantics.

## Required path

```text
entry adapter
-> universal entry envelope
-> continuity and prior-receipt binding
-> capability and policy classification
-> one or more selected lanes
-> governed return path
-> applicable routing, usage, retrieval, decision, execution, custody, or reconstruction receipts
```

## Supported lanes

```text
conversation
 ecosystem_query
 external_llm
 research
 solver
 governed_task
 execution
```

`selected_lanes` MUST be a subset of both node capability and policy-authorized `allowed_lanes`. A mixed request MAY select multiple lanes. External LLM output MUST return through the governed response path and MUST NOT bypass ecosystem policy, provenance, usage, or receipt handling.

## Entry-point parity

The following entry classes MUST use materially equivalent envelope and routing semantics:

```text
site_chat
sdk
api
portable_node
stegtalk
agent
repository_ingest
external_actor_gateway
partner_adapter
```

Adapters MAY differ in transport, authentication, and presentation. They MUST NOT invent incompatible route vocabularies, receipt rules, authority meanings, or continuity identities.

## Manifest-directed routing

The envelope declares origin, requested capabilities, allowed lanes, authority posture, expected receipt classes, and continuity identity. The router determines selected lanes. Entry adapters MUST NOT silently elevate their own capability or authority.

## Receipt-directed continuation

Prior receipts are inputs to the next routing decision when they establish continuity, usage, retrieval, decision, execution, custody, or reconstruction state. A receipt is not automatically authority. A routing or provider receipt MUST NOT be interpreted as execution permission.

## Portable-node release gate

A node MUST NOT be distributed as a functional public portable node when declared capabilities are fixture-only, preview-only, or unavailable at runtime.

A reduced-capability node MAY be distributed only when:

1. its capability registry accurately marks each capability `operational`, `degraded`, `unavailable`, or `disabled`;
2. every `operational` capability completes through the universal route;
3. unavailable capabilities fail closed and are not presented as performed;
4. conversation, ecosystem query, and external LLM claims match installed engines;
5. mixed routing, return-path, and receipt behavior are tested for every declared combination;
6. consequential operations are reconstructable from manifests and receipts.

## Minimum functional portable node

A full Ecosystem Chat portable node is ready only when it can:

- conduct multi-turn conversation;
- query authoritative ecosystem sources;
- invoke an external LLM through a server-side or locally authorized interface;
- return external output through governed synthesis;
- combine ecosystem and external lanes;
- preserve route changes within one session;
- emit applicable event and receipt records;
- fail closed on unavailable or unauthorized capabilities;
- reconstruct consequential interactions.

## Non-authority boundary

Universal entry validation is intake correctness, not execution authority. `execution_authority_granted` remains false in the entry envelope. Execution requires a later governed authority determination and an execution receipt obligation.

## Installed artifacts

```text
schemas/universal-entry-envelope.schema.v0.1.json
examples/universal_entry/site_chat_good_morning.json
scripts/verify_universal_entry_envelope.py
```

## Verification

```bash
python scripts/verify_universal_entry_envelope.py
```
