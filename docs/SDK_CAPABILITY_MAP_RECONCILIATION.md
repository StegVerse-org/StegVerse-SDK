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

An exemption is explicit. It names why the route is outside the standard, what
would bring it in and who owns that, and it can never report itself invocable.

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
installed without a builder binding and a working example turns the gate red.

Inspect the map with `stegverse capability-map`; `stegverse capabilities` now
carries the same rows as `installed_routes`.

## Boundary

Source reconciliation only. It installs nothing, binds nothing, substitutes no
route, observes no runtime and grants no execution authority. A route reported
`EVALUATOR_INVOCABLE` means a manifest can be built for it — not that any
transition was admitted. For the `EXISTING_UNIVERSAL_INTR` routes the honest
console result remains a `FAIL_CLOSED` at the attachment boundary naming the
unsatisfied predicate.
