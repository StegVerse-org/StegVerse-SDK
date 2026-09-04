# MHIA Physical Validation Plan v0

Status: pre-hardware validation plan. No test in this document is claimed as executed.

## Goal

Determine whether the first MHIA two-ear reference hardware can safely and repeatably support interchangeable ear modules while preserving the validated logical invariants: discovery is non-authorizing, main power remains off until negotiation/admission, conflicts are quarantined, and detach/fault returns the port to a safe state.

## Test groups

### A. Mechanical fit and retention

- verify keyed orientation prevents intended normal-use reverse insertion;
- measure insertion/removal force;
- measure magnetic/retention force in axial and shear directions;
- perform repeated attach/detach cycling with periodic contact-resistance measurement;
- inspect wear, deformation, debris attraction, corrosion and exposed contact damage;
- evaluate serviceability with representative ear pads/chassis installed.

Record: module ID, connector specimen ID, cycle count, force, contact resistance, visible damage and pass/fail.

### B. Safe power sequencing

For each module and each attach direction permitted by the geometry:

1. attach while VBUS is confirmed OFF;
2. verify only DETECT_ID bootstrap behavior occurs initially;
3. enable VSAFE and measure current limit;
4. validate module identity/manifest;
5. negotiate declared envelope;
6. deny admission and verify VBUS remains OFF;
7. allow admission and explicitly enable VBUS;
8. detach and verify VBUS removal latency;
9. repeat with invalid manifest, unknown module, negotiation timeout and unsupported envelope.

Acceptance: no tested invalid/unknown/denied path may energize operating VBUS.

### C. Electrical fault isolation

Inject or simulate, within safe laboratory methods:

- module-side short circuit;
- over-current request/load;
- over-voltage telemetry condition;
- thermal-limit exceedance;
- data-line short/open;
- DETECT_ID open/short;
- intermittent contact during motion;
- VSAFE discovery fault.

Acceptance: affected port isolates and transitions to SAFE_OFF/ISOLATED without causing the opposite ear port to inherit the failed port's state or capability.

### D. Signal integrity and data transport

After selecting a concrete PHY:

- characterize eye/signal margins or equivalent transport metrics;
- test maximum intended cable/trace/contact path;
- test repeated attach/detach after wear cycling;
- measure cross-talk with audio output and charging/power switching active;
- validate error handling during transient disconnect/reconnect.

### E. Thermal validation

Measure steady-state and transient temperature at:

- connector contacts;
- power switches;
- battery interface;
- amplifier/driver electronics;
- user-contact shell locations.

Run worst-case declared current/audio/compute combinations allowed by the negotiated envelope. Thermal trip behavior must isolate the affected port.

### F. Capability discovery and asymmetric composition

Test at minimum:

- left sensor/audio + right power/audio baseline;
- left reduced-sensor swap;
- right alternate power module;
- acoustic cartridge variant;
- two providers of the same compatible capability;
- incompatible declarations for the same capability;
- duplicate module identity attempt.

Acceptance: host graph is deterministic across discovery order; compatible providers are retained; incompatible capability declarations are quarantined; duplicate identity is rejected; physical presence never changes authority fields.

### G. Human-factor and interchangeability evaluation

- swap modules without replacing headband/chassis;
- document time/tools required;
- evaluate inadvertent detachment under representative movement;
- evaluate left/right balance and mass distribution with asymmetric modules;
- inspect pressure/contact points after module changes;
- verify user cannot easily contact hazardous energized surfaces.

## Evidence package per test run

Each physical run should retain:

```text
run_id
hardware revision
module IDs + manifest hashes
connector specimen IDs
firmware revision
host capability-graph output hash
electrical envelope
admission result
state-transition log
measurements
fault injections
audio/sensor configuration
photos/plots where applicable
operator/tester
calibration references
result + deviations
```

## Exit criteria for v0 physical prototype

The v0 prototype may be called `PHYSICALLY_VALIDATED_REFERENCE_V0` only after:

- all safety-critical power/fault tests pass;
- no VBUS-before-admission failure is observed;
- deterministic graph composition is reproduced on hardware;
- at least two independent module swaps succeed without replacing the chassis;
- asymmetric left/right operation succeeds;
- mechanical retention/cycle targets are met for the declared test sample;
- unresolved failures and test limitations are explicitly retained.

Passing this plan does not imply regulatory certification, production readiness, medical-device suitability, universal interoperability, or runtime/governance authority.
