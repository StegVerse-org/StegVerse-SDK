# SDK source-verified developer notes (first-party review draft)

Existing owner: `ECOSYSTEM-OPEN-SOURCE-STRATEGY-001`, COSV `20010010100000`. This is **new first-party prose assembled from checked-in SDK source**, not an import of external generated DeepWiki text or diagrams. It is staged for review inside the SDK repository, **not** automatically included in the published Pages wiki. Source revision for every code anchor below (newer than the separate frozen DeepWiki comparison revision): [`9cf1d69c770ea92048a0883adf6ff0dfa09797db`](https://github.com/StegVerse-org/StegVerse-SDK/tree/9cf1d69c770ea92048a0883adf6ff0dfa09797db). Each fact is deliberately bounded by the cited implementation or test.

## Installation and manifest construction

The SDK package declares `requests>=2.28.0`, `pyyaml>=6.0` and `python-dotenv>=0.19.0` as core dependencies in [`pyproject.toml`, lines 28–32](https://github.com/StegVerse-org/StegVerse-SDK/blob/9cf1d69c770ea92048a0883adf6ff0dfa09797db/pyproject.toml#L28-L32). Other packages, including Git-pinned optional test extras, appear separately in that manifest. These declarations do not prove third-party rights clearance or availability of optional private dependencies.

The [`build_manifest` function](https://github.com/StegVerse-org/StegVerse-SDK/blob/9cf1d69c770ea92048a0883adf6ff0dfa09797db/stegverse/manifest_builder.py#L211-L220) receives source-framework identity, an original output ID, data and a processor request. [`validate_ingress_manifest`](https://github.com/StegVerse-org/StegVerse-SDK/blob/9cf1d69c770ea92048a0883adf6ff0dfa09797db/stegverse/manifest_contract.py#L165-L168) is an independent ingress-envelope validator. [`route_from_manifest`](https://github.com/StegVerse-org/StegVerse-SDK/blob/9cf1d69c770ea92048a0883adf6ff0dfa09797db/stegverse/route_resolution.py#L152-L156) rejects a missing or non-object `extensions` value. Declaring, building or resolving a route is not evidence of governed execution or custody.

## Narrow source/test boundaries

The [purpose-bound worker partition helper](https://github.com/StegVerse-org/StegVerse-SDK/blob/9cf1d69c770ea92048a0883adf6ff0dfa09797db/stegverse/purpose_bound_worker_processor.py#L62-L64) checks that concatenated partition text exactly reproduces its input, raising an error on mismatch. This is a source-level invariant, not proof of live worker execution.

[`TEST2_SCENARIO`, `TEST3_SCENARIO` and `TEST3_LEGACY_SCENARIO`](https://github.com/StegVerse-org/StegVerse-SDK/blob/9cf1d69c770ea92048a0883adf6ff0dfa09797db/stegverse/atomic_task_worker_processor.py#L23-L25) name test cases and a legacy identifier. The [atomic-worker test](https://github.com/StegVerse-org/StegVerse-SDK/blob/9cf1d69c770ea92048a0883adf6ff0dfa09797db/tests/test_evaluator_atomic_task_worker_manifest.py#L91-L93) checks that a local state graph requires a WorkerCoordinator claim fence while the adapter does not execute the lifecycle. Neither file proves an authenticated production worker claim.

The [execution-boundary test](https://github.com/StegVerse-org/StegVerse-SDK/blob/9cf1d69c770ea92048a0883adf6ff0dfa09797db/tests/test_execution_boundary.py#L112-L143) verifies fail-closed outcomes for specific fixtures, including unobserved material changes and changed authority. It must not be described as proof that *every* real-world failure mode or a live transition has been observed.

The [Governance Reference Graph authority-boundary constants](https://github.com/StegVerse-org/StegVerse-SDK/blob/9cf1d69c770ea92048a0883adf6ff0dfa09797db/stegverse/governance_reference_graph.py#L23-L29) explicitly state that representation, hierarchy, composition, unknown relations and SDK graph handling confer no independent governance authority.

The [Universal Transition Table test fixture](https://github.com/StegVerse-org/StegVerse-SDK/blob/9cf1d69c770ea92048a0883adf6ff0dfa09797db/tests/test_universal_transition_table_intake.py#L25-L27) contains `package_id`, `canonical_cells` and `receipt_requirements`. These are **example fixture fields**, not an independently established exhaustive production schema.

## Ecosystem Chat implementation scope

The [local Ecosystem Chat pipeline](https://github.com/StegVerse-org/StegVerse-SDK/blob/9cf1d69c770ea92048a0883adf6ff0dfa09797db/stegverse/ecosystem_chat_pipeline.py#L23-L36) constructs a persistence plan, binds a configured destination and passes the plan to a supplied write adapter. These source calls do not independently authenticate a production destination or prove that the downstream write, governance and Master Records transitions actually occurred.

## Evidence boundaries and provenance

The [checked-in downstream status record](https://github.com/StegVerse-org/StegVerse-SDK/blob/9cf1d69c770ea92048a0883adf6ff0dfa09797db/evidence/system-boundary-downstream-status.v0.1.json#L1-L18) records a verified source status while explicitly setting production binding, release authorization, custody transfer, execution authority and admissibility determination to false. Status-only propagation is not live runtime proof.

The retained [public DeepWiki capture](https://github.com/StegVerse-org/StegVerse-SDK/actions/runs/36175208212/artifacts/10882475515) comprises 38 generated sections and **659 originally empty citation targets**. Reconstructed paths and line anchors remain review candidates. In particular, the generated Overview governance diagram's README lines 29–30 describe Publisher and egress, not the diagram's asserted governance-intake wiring. We do not adopt that diagram here. The original exact captured content stays unmodified (SHA-256 `a729d9b0f487f785b0e8f92006f303e8520e3593b6eb6c4c5de43273daa72087`).

This draft deliberately excludes broader generated assertions, runtime-completion claims and external-generated-text republication. Approval of code/documentation reuse rights, any SDK wiki publication and any governed Master Records transition are separate decisions with their own evidence.

## Source-verified replacement for broader generated claims

[First-party SDK contract corrections](FIRST_PARTY_VERIFIED_CONTRACTS.md) independently document 15 bounded source-level contracts for manifest ingress, routing, worker partitioning, non-authorizing handlers, security posture, atomic graph derivation, Stage-1 custody limitations, Ecosystem Chat, Publisher return binding and existing developer-wiki source composition. Those assertions are pinned to SDK source revision `f5d9fdcc089bc8becdbc23a6107dab978dc15f56` and tested separately; unlike the quarantined external DeepWiki capture, the new text is not copied from generated pages. The existing Pages builder does **not** include either first-party review guide automatically. The [rights record](GENERATED_DOCS_AND_DEPENDENCY_RIGHTS.md) keeps generated-text republication and optional Git dependency redistribution independently gated.

## Manifest and route semantic successor review — 2026-09-25

[First-party exact-source manifest reference](FIRST_PARTY_MANIFEST_30_SOURCE_REFERENCE.md) independently documents 13 source-verified atomic implementation predicates and 17 narrower or unresolved assertions from 30 original, previously unsupported non-priority DeepWiki source candidates. The source-only successor [artifact 10895814581](https://github.com/StegVerse-org/StegVerse-SDK/actions/runs/36212692404/artifacts/10895814581) binds each original citation index, claim-context/source excerpt hash and prior non-ALLOW record to an exact current-code witness. These narrow facts do **not** approve entire generated paragraphs or the generated DeepWiki site; no original capture or quarantined review copy is imported into public Pages. Reuse-rights, additional open-source releases and genuine InTr/Master Records custody remain separately gated.
