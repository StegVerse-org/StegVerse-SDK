# SDK capability map reconciliation

The SDK's demo surface is the residue of its passed tests. `inspection/examples`
holds the exact fixture pairs the evaluator ran — Test 1's purpose-bound worker
request, Tests 2/3's atomic-task-worker requests, Test 4's four-case cost/lifetime
fixture, the HOLD source-observation fixture. A capability an evaluator can run
is one that has a fixture; a capability without one exists only inside the repo.

Nothing kept that surface in step with the route table, and three maps had
drifted apart:

| map | what it describes | kept how |
|---|---|---|
| `route_resolution.PUBLISHED_ROUTES` | which runtime is installed | authoritative |
| `manifest_builder.PROCESSOR_ROUTES` | which capability `--process` reaches | hand-maintained |
| `inspection/examples` | which capability a console can invoke | hand-maintained |

`capability_inventory` derives from the first and reported nine installed routes.
The builder could reach six of them. Two capabilities — `native_source_math` and
`sovereign_inference` — were published as installed while `build_manifest`
classified them `UNKNOWN_CAPABILITY`, and `stegverse.route.customer-local-governed.v1`
could not be selected at all because `--process governance` resolves to exactly
one route id. Two more, `stegbrowser` and `svg_governance_cycle`, were builder-bound
with no evaluator fixture.

## What this adds

`stegverse/capability_map.py` reconciles the three maps and states a disposition
per published route: `EVALUATOR_INVOCABLE`, `DECLARED_EXEMPTION`, or
`STOP_CAPABILITY_MAP_DRIFT`. A drifting route carries the predicate it failed,
the repair that satisfies it, a retry entrypoint and an owning goal — never a
bare unknown.

## Exemptions are granted, not self-declared

An exemption cannot be a permanent carve-out a capability awards itself. Each one
carries its failed predicate and repair, and also:

* `owning_existing_goal` — a canonical task id, checked against the registry's
  own id shape. All three current exemptions are owned by
  `SDK-GENERIC-MANIFEST-ECOSYSTEM-INVARIANT-005`, whose goal is to enforce the
  manifest-driven processing invariant across SDK processors and establish an
  architectural-claim validation gate.
* `registry_repository` and `observed_registry_generation` — the observation
  that the goal existed, and when. The SDK cannot read the canonical registry at
  test time, so it records what was observed rather than asserting a remote
  truth it cannot see.
* `granted_by` — must name the owning goal. An exemption that grants itself
  fails the gate.
* `review_by` — a date. Once it passes the gate goes red, so the carve-out has
  to be re-granted or repaired. A missing or malformed date counts as expired.

`EXEMPTION_BASELINE` names the exemptions that exist. Granting one means editing
that set in the same change, where a reviewer sees it; an exemption can never
appear as a side effect of adding a route. An exemption never reports itself
invocable.

Two fixtures were added so their capabilities became invocable rather than
exempt: `sdk-test5-stegbrowser-llm-profile.processor-request.json` and
`sdk-svg-governance-cycle.processor-request.json`. Both are the shapes the
canonical staged requests already use.

Current state: 9 published routes, 6 evaluator-invocable, 3 declared exemptions,
0 drift.

## Why it is a gate

`tests/test_capability_map_conformance.py` builds every declared example pair
through `build_manifest` and asserts the manifest lands on that route — the demo
is the test, not a file that merely exists beside one. A new route published as
installed without a builder binding and a working example turns the gate red, as
does a self-granted exemption, a non-canonical owning goal, a lapsed review date
and an exemption granted outside the declared baseline. Each of those five was
verified red before merge.

The workflow runs on every pull request rather than a path filter: a capability
can be introduced in a module no filter anticipates, and the job takes about
twelve seconds.

Inspect the map with `stegverse capability-map`; `stegverse capabilities` now
carries the same rows as `installed_routes`.

## Boundary

Source reconciliation only. It installs nothing, binds nothing, substitutes no
route, observes no runtime and grants no execution authority. A route reported
`EVALUATOR_INVOCABLE` means a manifest can be built for it — not that any
transition was admitted. For the `EXISTING_UNIVERSAL_INTR` routes the honest
console result remains a `FAIL_CLOSED` at the attachment boundary naming the
unsatisfied predicate.
