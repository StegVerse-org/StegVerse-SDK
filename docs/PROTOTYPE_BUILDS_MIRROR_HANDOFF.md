# Prototype Builds Mirror Handoff

## Source of truth

```text
organization: StegVerse-org
repository: StegVerse-SDK
canonical_branch: main
parent_handoff: SDK_MIRROR_HANDOFF.md
scope: StegVerse prototype-build concepts and prototype architecture candidates
credential_authority: TV/TVC
GitHub token runtime authority: NONE
```

This file is the scoped continuation record for prototype-build concepts documented under `docs/prototype-builds/`. It is subordinate to `SDK_MIRROR_HANDOFF.md` and does not grant runtime, activation, credential, publication, or transition authority.

## Modular Human Interface Architecture (MHIA)

Canonical synopsis:

```text
docs/prototype-builds/MODULAR_HUMAN_INTERFACE_ARCHITECTURE.md
```

Implemented artifacts:

```text
schemas/prototype-builds/mhia-module-manifest.v1.schema.json
schemas/prototype-builds/mhia-mechanical-attachment-profile.v1.schema.json
schemas/prototype-builds/mhia-electrical-data-interface.v1.schema.json
examples/prototype-builds/mhia-left-ear-sensor-module.v1.json
examples/prototype-builds/mhia-right-ear-power-audio-module.v1.json
examples/prototype-builds/mhia-ear-mechanical-profile.v1.json
examples/prototype-builds/mhia-ear-electrical-data-interface.v1.json
stegverse/mhia_capability_graph.py
stegverse/mhia_reference_firmware.py
stegverse/mhia_reference_hal.py
tests/test_mhia_module_manifest_schema.py
tests/test_mhia_capability_graph.py
tests/test_mhia_reference_firmware.py
tests/test_mhia_reference_hal.py
docs/prototype-builds/MHIA_REFERENCE_CONNECTOR_PINOUT_V0.md
docs/prototype-builds/MHIA_TWO_EAR_REFERENCE_BOM_V0.md
docs/prototype-builds/MHIA_PHYSICAL_VALIDATION_PLAN_V0.md
docs/prototype-builds/MHIA_REFERENCE_COMPONENT_CANDIDATES_V0.md
.github/workflows/mhia-schema-validation.yml
```

Validation evidence:

```text
initial logical-manifest validation: run 33907042094 -> SUCCESS
mechanical + electrical/data extension validation: run 33907170937 -> SUCCESS
capability-graph extension validation: run 33907371645 -> SUCCESS
reference firmware + connector/BOM source validation: run 33911367741 -> SUCCESS
physical-validation-plan documentation-triggered validation: run 33911399546 -> SUCCESS
handoff-state validation: run 33911441943 -> SUCCESS
hardware-abstraction boundary validation: run 33918491094 -> SUCCESS
component-candidate documentation-triggered validation: run 33918515418 -> SUCCESS
hosted validation authority: NONE
```

Current source commits:

```text
capability graph: 335d32e1f84023b394563bb03867f1f5beae3b0c
asymmetric right-ear fixture: 204d8f201c1774157404ef773f0b9c9a8e2bf5a7
capability graph tests: 48085656b86baa6f1e9dbe20787d9ca593b0bce9
reference connector/pinout: 27c9c7a8a80319179a254849fad414cc51c51fa1
reference firmware state machine: 75481290f00bbf1e26745017f116adb54656a8a7
reference firmware tests: ebaae38195bf8af16bb9ec2cc88164aa5a6680a8
two-ear reference BOM: 8c3308d1015308e597ed224b83296e19a486078b
physical validation plan: cb3d3db9feb69f9a569dd19dbdf3366a591f5d76
hardware abstraction: 0c3df9fca46eea6efdf33f5ce9f3cafc964e5c26
hardware abstraction tests: 8f4569efb59212d3e29fee6c66bb512db0a6dde7
HAL validation-workflow extension: 75a38d42d1b092c3fb3dbec7a98d5ba90a7fda84
concrete component candidate set: 424f9d938a811675a857b6f5d73ab93deb35ea7c
handoff advance through HAL/component candidates: 605c60184f9580d5748fcf9424a8d473a4d786db
```

Status:

```text
concept captured: COMPLETE
implementation-neutral module/capability manifest schema: COMPLETE_SOURCE_VALIDATED
module identity + provenance fields: COMPLETE_SOURCE_VALIDATED
logical interface declaration: COMPLETE_SOURCE_VALIDATED
power declaration: COMPLETE_SOURCE_VALIDATED
authority-boundary declaration: COMPLETE_SOURCE_VALIDATED
mechanical attachment logical profile: COMPLETE_SOURCE_VALIDATED
electrical/power/data negotiation logical profile: COMPLETE_SOURCE_VALIDATED
host deterministic capability-discovery graph: COMPLETE_SOURCE_VALIDATED
asymmetric left/right composition fixture: COMPLETE_SOURCE_VALIDATED
conflicting capability quarantine: COMPLETE_SOURCE_VALIDATED
no-authority-inheritance composition invariant: COMPLETE_SOURCE_VALIDATED
reference connector/pinout candidate: SOURCE_COMPLETE_VALIDATED_AS_ENGINEERING_CANDIDATE
reference firmware discovery/negotiation state machine: COMPLETE_SOURCE_VALIDATED
reference firmware safety tests: COMPLETE_SOURCE_VALIDATED
hardware-abstraction fail-closed projection: COMPLETE_SOURCE_VALIDATED
hardware-abstraction overcurrent/fault enforcement: COMPLETE_SOURCE_VALIDATED
two-ear reference BOM component classes: SOURCE_COMPLETE
physical validation plan: SOURCE_COMPLETE
manufacturer-family candidate set: COMPLETE_SOURCE_VALIDATED_AS_ENGINEERING_CANDIDATE
manufacturer orderable part-number freeze: NOT_STARTED
mechanical CAD/fit validation: NOT_STARTED
assembled reference hardware: NOT_STARTED
compatibility implementation on physical hardware: NOT_STARTED
physical validation execution: NOT_STARTED
release/tag: NONE
runtime activation claim: NONE
```

The capability graph sorts module/capability discovery deterministically, supports asymmetric left/right modules, preserves compatible multiple providers, quarantines incompatible declarations instead of exposing them as usable capabilities, rejects duplicate module identity, and rejects any module declaration that attempts to derive authority from discovery or attachment. Composition itself grants no authority.

The reference firmware enforces the sequence DETACHED -> SAFE_OFF -> VSAFE_DISCOVERY -> MANIFEST_VALIDATED -> NEGOTIATED -> ADMITTED -> VBUS_ACTIVE. Invalid manifests, negotiation failures, admission denial, detach, or fault cannot produce operating VBUS. Fault transitions isolate the port and clear the negotiated envelope. This is executable reference logic, not evidence of flashed physical firmware.

The hardware-abstraction layer projects that governed state onto independent VSAFE/VBUS controls. It always drives VBUS off before non-active transitions, forces both rails off on a hardware fault, and independently drops VBUS when observed current exceeds the negotiated envelope. The HAL does not create admission or credentials.

The `MHIA-EAR-8P-MAG-v0` connector remains an engineering candidate using keyed magnetic retention and eight spring contacts with separate GND, ground-sense, passive detect/ID, differential data, wake/interrupt, current-limited discovery power, and separately switched operating power. Physical geometry, contact rating, signal integrity, moisture/corrosion, arcing, magnetic safety and cycle life remain unvalidated.

The concrete component-family candidate set identifies Nordic nRF5340, TI TPS25947, Nordic nPM1300, TDK InvenSense ICM-42688-P and Analog Devices MAX98357A for the first host/power/module-management/motion/audio reference path. These are engineering candidates only; exact orderable suffixes/packages and procurement quantities are not yet frozen.

## Next machine-execution sequence

1. Resolve exact orderable suffix/package candidates, connector/contact manufacturer, microphone, driver and battery cell only after cost/availability/physical-envelope review.
2. Freeze a procurement-candidate BOM only when dimensions, ratings and availability are verified together.
3. Produce first mechanical CAD/dimensional drawing against the frozen package/contact/component envelopes.
4. Implement device-specific HAL adapters for selected MCU/power switches/telemetry devices.
5. Assemble hardware and execute `MHIA_PHYSICAL_VALIDATION_PLAN_V0.md`; do not claim physical validation before retained measurements exist.
6. Only after successful physical validation evaluate a prototype release/tag and downstream propagation tasks for StegVerse-Labs/Site, GCAT-BCAT-Engine/Publisher, admissibility-wiki and stegguardian-wiki.

## Continuation rule

Prototype concepts may be documented before implementation, but documentation MUST distinguish concept, scaffold, implementation, validation, release, deployment, and authentic runtime evidence. No prototype-build document may infer working physical hardware or runtime activation from source/design evidence alone.
