# Optional Transparency Surfaces — 000 / 00

## Purpose

Options `000` and `00` are optional transparency and configuration surfaces. They exist so a human can explicitly inspect what StegVerse is using, what it is not using, what transitions and receipts mean, what may be returned to the caller, and what remains in canonical Master Records custody.

They are **not prerequisites for machine-to-machine governance** and they grant no additional authority.

## Operating principle

```text
machine use should be minimal;
human observability should be maximal without changing machine semantics.
```

An external LLM/framework that already knows the accepted `stegverse.ingress-manifest.v1` contract may construct a conforming manifest and submit it directly through the ordinary governed ingress path. It does not need to invoke `000` or `00` first.

However, an LLM or agent **may** invoke or use the semantics of `000` and `00` when helping a user understand or configure StegVerse. In that case, the LLM receives the same transparency surfaces available to the human; there is no privileged AI-only explanation path.

## Option 000 — explain by worked example

`000` is the complete worked demonstration. It is intended to answer questions such as:

- What data was submitted?
- What manifest shape did StegVerse use?
- What governance outcomes exist?
- Which state-transition classes and receipt classes exist?
- Which fields are editable input vs generated observation?
- Which evidence is returned to the caller?
- Which state transitions remain in Master Records regardless of caller projection?
- Which objects are locators or observations rather than authority?

A human may read the returned package directly. An LLM may use the same package to explain the process to its user in natural language.

The LLM must not treat demo outcomes, generated receipts, or explanatory labels as authority for a future run.

## Option 00 — explain/configure user intent

`00` is the explicit user-parameter surface. It is intended to help a human choose permitted caller-return behavior, including:

```text
return_projection
  -> which user-disclosable transition evidence is returned

manifest_labels
  -> how returned sections are labeled/explained
```

An LLM may use `00` on behalf of a user to explain available choices and construct the corresponding ordinary manifest fields. Example user interaction:

```text
User: Only return governance and execution receipts, but explain each returned section.

LLM assistance:
  return_projection.mode = SELECTED
  return_projection.transition_classes = [governance, consequence]
  manifest_labels.mode = ALL
```

The resulting request is still an ordinary `stegverse.ingress-manifest.v1` manifest and must pass the normal profile, hash, provenance, governance, and consequence-boundary checks.

## Direct machine path

```text
External LLM/framework
  -> construct stegverse.ingress-manifest.v1
  -> ordinary manifest validation/canonicalization
  -> canonical StegVerse governance
  -> consequence boundary if applicable
  -> return ingestion
  -> governed result + manifest_receipt_id
```

`000` and `00` are not required in this path.

## Assisted-user path

```text
User <-> LLM/agent
      |
      +-> optional 000 for complete worked explanation
      +-> optional 00 for explicit parameter explanation/configuration
      |
      -> construct ordinary stegverse.ingress-manifest.v1
      -> canonical governed path
```

## Direct-human path

```text
User -> SDK 000 / 00 / 0 / 1 / 2
```

The human and the assisting LLM observe the same vocabulary and boundaries.

## Authority invariants

```text
000 grants authority: false
00 grants authority: false
manifest labels grant authority: false
schema discovery grants authority: false
manifest structural validity grants authority: false
manifest_receipt_id grants authority: false
Master Records custody is independent of caller-return projection
```

Invoking `000` or `00` must never create a stronger governance path than submitting the same canonical manifest directly.

## Product rule

There must be no hidden dependency on the educational surfaces. If an external LLM can construct a valid canonical manifest directly, StegVerse must govern it through the same canonical path used after human-assisted configuration.

Conversely, when a user asks what StegVerse is doing, an LLM may use the optional transparency surfaces to explain the exact same machine semantics rather than inventing a separate simplified story.
