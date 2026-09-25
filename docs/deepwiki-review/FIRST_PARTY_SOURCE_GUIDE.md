# SDK source-verified developer notes (first-party review draft)

Existing owner: `ECOSYSTEM-OPEN-SOURCE-STRATEGY-001`, COSV `20010010100000`. This is **new first-party prose assembled from checked-in SDK source**, not an import of external generated DeepWiki text or diagrams. It is staged for review inside the SDK repository, **not** automatically included in the published Pages wiki. Source revision for every code anchor below: [`eec03e0fa3a2ee327eb4e3368b3f8458ac85e582`](https://github.com/StegVerse-org/StegVerse-SDK/tree/eec03e0fa3a2ee327eb4e3368b3f8458ac85e582). Each fact is deliberately bounded by the cited implementation or test.

## Installation and manifest construction

The SDK package declares `requests>=2.28.0`, `pyyaml>=6.0` and `python-dotenv>=0.19.0` as core dependencies in [`pyproject.toml`, lines 28–32](https://github.com/StegVerse-org/StegVerse-SDK/blob/eec03e0fa3a2ee327eb4e3368b3f8458ac85e582/pyproject.toml#L28-L32). Other packages, including Git-pinned optional test extras, appear separately in that manifest. These declarations do not prove third-party rights clearance or availability of optional private dependencies.

The [`build_manifest` function](https://github.com/StegVerse-org/StegVerse-SDK/blob/eec03e0fa3a2ee327eb4e3368b3f8458ac85e582/stegverse/manifest_builder.py#L160-L169) receives source-framework identity, an original output ID, data and a processor request. [`validate_ingress_manifest`](https://github.com/StegVerse-org/StegVerse-SDK/blob/eec03e0fa3a2ee327eb4e3368b3f8458ac85e582/stegverse/manifest_contract.py#L165-L168) is an independent ingress-envelope validator. [`route_from_manifest`](https://github.com/StegVerse-org/StegVerse-SDK/blob/eec03e0fa3a2ee327eb4e3368b3f8458ac85e582/stegverse/route_resolution.py#L152-L156) rejects a missing or non-object `extensions` value. Declaring, building or resolving a route is not evidence of governed execution or custody.

## Narrow source/test boundaries

The [purpose-bound worker partition helper](https://github.com/StegVerse-org/StegVerse-SDK/blob/eec03e0fa3a2ee327eb4e3368b3f8458ac85e582/stegverse/purpose_bound_worker_processor.py#L62-L64) checks that concatenated partition text exactly reproduces its input, raising an error on mismatch. This is a source-level invariant, not proof of live worker execution.

[`TEST2_SCENARIO`, `TEST3_SCENARIO` and `TEST3_LEGACY_SCENARIO`](https://github.com/StegVerse-org/StegVerse-SDK/blob/eec03e0fa3a2ee327eb4e3368b3f8458ac85e582/stegverse/atomic_task_worker_processor.py#L23-L25) name test cases and a legacy identifier. The [atomic-worker test](https://github.com/StegVerse-org/StegVerse-SDK/blob/eec03e0fa3a2ee327eb4e3368b3f8458ac85e582/tests/test_evaluator_atomic_task_worker_manifest.py#L91-L93) checks that a local state graph requires a WorkerCoordinator claim fence while the adapter does not execute the lifecycle. Neither file proves an authenticated production worker claim.

The [execution-boundary test](https://github.com/StegVerse-org/StegVerse-SDK/blob/eec03e0fa3a2ee327eb4e3368b3f8458ac85e582/tests/test_execution_boundary.py#L112-L143) verifies fail-closed outcomes for specific fixtures, including unobserved material changes and changed authority. It must not be described as proof that *every* real-world failure mode or a live transition has been observed.

The [Governance Reference Graph authority-boundary constants](https://github.com/StegVerse-org/StegVerse-SDK/blob/eec03e0fa3a2ee327eb4e3368b3f8458ac85e582/stegverse/governance_reference_graph.py#L23-L29) explicitly state that representation, hierarchy, composition, unknown relations and SDK graph handling confer no independent governance authority.

The [Universal Transition Table test fixture](https://github.com/StegVerse-org/StegVerse-SDK/blob/eec03e0fa3a2ee327eb4e3368b3f8458ac85e582/tests/test_universal_transition_table_intake.py#L25-L27) contains `package_id`, `canonical_cells` and `receipt_requirements`. These are **example fixture fields**, not an independently established exhaustive production schema.

## Ecosystem Chat implementation scope

The [local Ecosystem Chat pipeline](https://github.com/StegVerse-org/StegVerse-SDK/blob/eec03e0fa3a2ee327eb4e3368b3f8458ac85e582/stegverse/ecosystem_chat_pipeline.py#L23-L36) constructs a persistence plan, binds a configured destination and passes the plan to a supplied write adapter. These source calls do not independently authenticate a production destination or prove that the downstream write, governance and Master Records transitions actually occurred.

## Evidence boundaries and provenance

The [checked-in downstream status record](https://github.com/StegVerse-org/StegVerse-SDK/blob/eec03e0fa3a2ee327eb4e3368b3f8458ac85e582/evidence/system-boundary-downstream-status.v0.1.json#L1-L18) records a verified source status while explicitly setting production binding, release authorization, custody transfer, execution authority and admissibility determination to false. Status-only propagation is not live runtime proof.

The retained [public DeepWiki capture](https://github.com/StegVerse-org/StegVerse-SDK/actions/runs/36175208212/artifacts/10882475515) comprises 38 generated sections and **659 originally empty citation targets**. Reconstructed paths and line anchors remain review candidates. In particular, the generated Overview governance diagram's README lines 29–30 describe Publisher and egress, not the diagram's asserted governance-intake wiring. We do not adopt that diagram here. The original exact captured content stays unmodified (SHA-256 `a729d9b0f487f785b0e8f92006f303e8520e3593b6eb6c4c5de43273daa72087`).

This draft deliberately excludes broader generated assertions, runtime-completion claims and external-generated-text republication. Approval of code/documentation reuse rights, any SDK wiki publication and any governed Master Records transition are separate decisions with their own evidence.
