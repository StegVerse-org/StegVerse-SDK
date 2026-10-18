# Six-field disposition check

`scripts/check_six_field_dispositions.py` is a standard-library-only CI check (Python 3.10+,
no PyYAML, no jsonschema). It finds refusals that are missing the ecosystem's required
six-field actionable disposition. Every non-ALLOW result (`FAIL_CLOSED`, `DENY`, `BLOCK`,
`BLOCKED`, `REFUSED`) must carry all six of these fields:

| field | meaning |
| --- | --- |
| `failure_code` | stable machine code for the failure |
| `failed_predicate` | the predicate that did not hold |
| `required_evidence_or_repair` | what would make it hold |
| `retry_entrypoint` | where to retry (script, workflow, endpoint) |
| `owning_existing_goal` | the existing goal that owns the repair |
| `next_attempt` | the concrete next attempt |

This check replaces LLM review for this class of defect. A reviewer no longer needs to
read for "did this refusal say how to recover"; CI enforces it.

## What it checks

**JSON files (`*.json`, structural).** Each file is parsed and walked recursively. Any object
whose `disposition`, `status`, `decision` or `result` value is a string in the non-ALLOW set
(case-sensitive) must hold all six keys *on that same object*, each with a non-empty value.
Fields that appear only in a nested child, such as `actionable_disposition: {...}`, do not
count; that nesting is one of the known defects. Each finding gives a JSON pointer to the
refusal object and lists its missing fields.

Some files are skipped, and each skip is listed under `scanned.skipped`:

- JSON Schema files, meaning `*.schema.json` or a root object with `$schema`. Their enum
  lists are vocabulary, not results.
- Unparsable JSON.

**Workflows (`*.yml`, `*.yaml`, heuristic).** The script reads every `run:` value: a
single-line `run: ...`, or a block scalar `run: |` / `run: >`, which extends to the next line
indented at or below the `run` key. A line is a *refusal emission* when both of these hold:

- It produces output: `echo`, `printf`, `print(`, `cat <<` (including the heredoc body),
  `>> "$GITHUB_OUTPUT"` or `::error`.
- It contains a non-ALLOW token as a whole word.

If a block has a refusal emission, all six field names must appear somewhere in that same
block. Each finding gives the file, the 1-based line of the `run:` key and the missing fields.

**Empty scans.** If nothing was scanned, the result is `FAIL_CLOSED` with
`failure_code: NO_INPUTS_SCANNED`. An empty input set is never ALLOW. Inputs that were all
skipped also count as an empty scan.

## CLI

```
python3 scripts/check_six_field_dispositions.py [paths...] [--output report.json] [--allow-legacy-file FILE]
```

- Paths can be files or directories, and the default is `.`. Directories are walked,
  skipping `.git`, `node_modules`, `.venv`, `venv` and `__pycache__`.
- The report goes to stdout. With `--output`, it goes to that file and stdout gets a
  one-line summary.
- The exit code is `0` only when `disposition` is `ALLOW`. Otherwise it is `1`.

Report shape (keys sorted, findings sorted by path):

```json
{
  "schema": "stegverse.six-field-disposition-check.v1",
  "disposition": "ALLOW | FAIL_CLOSED",
  "scanned": {"json": 0, "workflows": 0, "skipped": [{"path": "...", "reason": "..."}]},
  "findings": [{"kind": "json", "path": "...", "pointer": "/a/0", "key": "status", "value": "DENY", "missing_fields": ["..."]},
               {"kind": "workflow", "path": "...", "line": 12, "tokens": ["FAIL_CLOSED"], "missing_fields": ["..."]}],
  "exempted": []
}
```

When the report is `FAIL_CLOSED`, it carries the six fields itself:

- `failure_code`: one of `SIX_FIELD_DISPOSITION_INCOMPLETE`, `NO_INPUTS_SCANNED` or
  `EXEMPTION_DECLARATION_INCOMPLETE`.
- `failed_predicate`: for findings, `EVERY_NON_ALLOW_RESULT_CARRIES_SIX_FIELDS`.
- `required_evidence_or_repair`
- `retry_entrypoint`: `scripts/check_six_field_dispositions.py`
- `owning_existing_goal`: `SDK-STRUCTURAL-VALIDATOR-CONSOLIDATION-001`
- `next_attempt`

## Declared exemptions

Ecosystem rule `DECLARED_EXEMPTION_REQUIRED` applies: legacy refusals that must not be edited
(for example, frozen historical receipts) are exempted explicitly and never silently.

```json
{"entries": [
  {"path": "receipts/legacy/old-receipt.json",
   "reason": "frozen historical receipt; content-addressed, cannot change",
   "owning_existing_goal": "SDK-STRUCTURAL-VALIDATOR-CONSOLIDATION-001"}
]}
```

An exemption works like this:

- An entry's `path` matches a finding's reported path in one of three ways: an exact match,
  a match on a trailing path suffix, or an `fnmatch` glob such as `receipts/legacy/*.json`.
- Exempted findings move to `exempted`, with the matching entry attached.
- Every entry needs non-empty `path`, `reason` and `owning_existing_goal` strings. If any
  entry is incomplete, or the file is unreadable, the run is `FAIL_CLOSED`
  (`EXEMPTION_DECLARATION_INCOMPLETE`).

## Adopted in this repository

`.github/workflows/six-field-disposition-check.yml` runs the check over the whole tree on every
pull request and every push to `main`, with no path filter, as job `six-field-dispositions`.
Legacy refusals whose bytes cannot change are declared in `.six-field-exemptions.json`. The job is
declared as a required check in `tasks/SDK-REPOSITORY-HARDENING-001.json`
(`required_checks_declared`). Enforcement needs a `main` ruleset, which is applied only through the
existing TVC ruleset transition; until then the declaration records `DECLARED_NOT_ENFORCED` with the
six fields.

## Adopting it in Labs, org and Site repositories

The script has no dependencies, so adopting it takes one of two forms:

1. **Copy it.** Vendor `scripts/check_six_field_dispositions.py` into the repository and
   record the SDK commit it came from in a comment or a pin file. Then run it as a step:

   ```yaml
   - run: python3 scripts/check_six_field_dispositions.py .github/workflows reports --output six-field.json
   ```

2. **Run it from a pinned SDK checkout.** Fetch the SDK at an exact commit, not a branch,
   and point it at the caller's tree:

   ```yaml
   - run: |
       set -eu
       mkdir -p /tmp/sdk
       curl -fsSL "https://github.com/StegVerse-org/StegVerse-SDK/archive/${SDK_SHA}.tar.gz" | tar -xz -C /tmp/sdk --strip-components=1
       python3 /tmp/sdk/scripts/check_six_field_dispositions.py .github/workflows reports --allow-legacy-file .six-field-exemptions.json
   ```

Choose paths that hold results and workflows. Pointing the check at a tree with nothing to
scan is deliberately a failure.

## Limitations of the workflow scan

The workflow scan is a line heuristic. It does not parse YAML.

- **Field names, not values.** It checks that the six field *names* appear somewhere in the
  `run:` block. It does not check that they are attached to the emitted refusal or that they
  have non-empty values. Plural variants such as `failure_codes:` do not count.
- **Narrow output detection.** Only `echo`, `printf`, `print(`, `cat <<`, `$GITHUB_OUTPUT`
  and `::error` count as output. A refusal written by other means, for example
  `json.dump(...)` in an inline Python heredoc or `tee`, is missed. Prefer emitting
  refusals as JSON files, which get the structural check.
- **Tokens must be on the output line.** Comparisons such as
  `assert r["disposition"] == "FAIL_CLOSED"` are correctly ignored. A refusal token held in a
  shell variable and echoed elsewhere (`echo "$D"`) is not seen.
- **Only `run:` is read.** Refusals in `with:` inputs, composite actions, or scripts the
  block calls are not checked. Scan those scripts' JSON output instead.
- **Unusual YAML is not handled.** Flow-style, anchored, or multi-line plain-scalar `run:`
  values are read only as far as their first line.
