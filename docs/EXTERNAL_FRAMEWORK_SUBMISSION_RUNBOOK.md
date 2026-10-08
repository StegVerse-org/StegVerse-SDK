# External framework submission — run this first

Any evaluator can produce a validated, digest-bound StegVerse submission from the
public SDK with no credentials and no StegVerse-side setup. This is the path to
run before asking for anything else.

## What you need

Three JSON files. Neutral examples are in `inspection/examples/`, and each field
says what to replace it with:

| file | what it is |
| --- | --- |
| `external-framework-submission-source.example.json` | what your framework observed, in your own shape |
| `external-framework-governance-request.example.json` | the governance facts you represent |
| `external-framework-evaluation-declaration.example.json` | what you are asking to establish |

Your framework's identity is **not** in any of them. It is a command-line
argument, because `source_framework` is a field of the manifest, not a property
of the fixture. The same three files work for every evaluator.

## Run it

```bash
pip install stegverse-sdk        # or: pip install -e . from a checkout

stegverse external-run --prepare-only \
  --input            your-source.json \
  --governance-request your-governance-request.json \
  --evaluation-declaration your-evaluation-declaration.json \
  --source-framework   YOUR_FRAMEWORK \
  --source-output-id   your-submission-001 \
  --data-class         your.source-class.v1 \
  --return-depth       full-trace \
  --output             submission.json
```

## What you get

```text
schema:              stegverse.sdk.external-framework-submission.v1
status:              SUBMISSION_READY
execution_performed: false
manifest_receipt_id: null
```

Plus a canonical `stegverse.ingress-manifest.v1` carrying your payload and
candidate digests, the resolved processing capability and route, your declared
data class, and your evaluation declaration held separately from the governance
request.

## What this does and does not establish

It establishes that your submission is structurally admissible: the manifest
validates, the capability resolves to an installed route, and the digests bind
your bytes.

It establishes nothing about execution. `execution_performed: false` and
`manifest_receipt_id: null` are load-bearing, not placeholders. Canonical
governed execution, Master Records organization record, replay and reconstruction are a
separate step through the StegVerse runtime, and this command deliberately
cannot claim them.

## Why the examples are not named after a framework

An artifact named after the first framework that exercised it reads as that
framework's demo, and the next evaluator has to reverse-engineer a neutral shape
out of someone else's name. Identity belongs in `source_framework`, which is a
required manifest field. See `CAPABILITY_NAMED_ARTIFACTS.md`; the naming guard
enforces it.

## Notes

`declared_context` inside the governance request is descriptive only — nothing
in the SDK reads it. The binding identity is the `--source-framework` argument.

Leave unknown internal state `null` rather than inferring it. A null is
preserved as an explicit unknown; an invented value is indistinguishable from an
observation, which is the one thing a submission must never blur.
