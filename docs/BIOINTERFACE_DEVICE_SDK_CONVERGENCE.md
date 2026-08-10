# StegVerse Biointerface Device SDK Convergence

Status: architectural handoff candidate
Date: 2026-08-09
Origin: StegHealth / StegNeuro hardware convergence discussion

## Purpose

StegHealth physiological nodes and StegNeuro neural READ/WRITE nodes should not independently reinvent the same MCU, clock, local storage, BLE/USB transport, device identity, configuration, discovery, packet framing, firmware lifecycle, and developer tooling.

The shared lower layer is a non-authorizing **StegVerse Biointerface Device SDK**. Domain repositories own the meaning of signals and the authority boundaries above the shared transport/device substrate.

## Shared physical-node substrate

A conforming physical node may provide:

- secure/stable device identity;
- MCU/runtime identity;
- monotonic clock and optional UTC synchronization evidence;
- local append-only capture/storage;
- BLE, USB, serial, or other bounded transports;
- device discovery and capability declaration;
- configuration hashing/versioning;
- sequence/framing and packet-loss evidence;
- battery/device-health state;
- firmware/runtime version evidence;
- raw/native byte preservation where available;
- host SDK discovery, capture, replay, and provenance surfaces.

The shared substrate does **not** decide what a physiological or neural signal means and does not grant authority merely because a capability exists.

## Domain profiles

### StegHealth

Canonical owner: `StegVerse-Labs/StegHealth`.

Example READ profiles:

- PPG red/IR/green raw;
- ECG observation;
- temperature;
- accelerometer/motion;
- CO2 waveform;
- airway pressure/flow;
- other physiological/environmental observations.

StegHealth owns physiological acquisition semantics, raw evidence, synchronization, derived-observation provenance, multisite correlation, and research-device profiles.

### StegNeuro

Canonical owner: `StegVerse-Labs/StegNeuro`.

Neuro is **not brain-limited**. The nervous-system scope may include CNS, spinal, cranial, peripheral somatic, autonomic sympathetic, autonomic parasympathetic, enteric, neuromuscular, and sensory-afferent pathways when a justified neural interface profile exists.

Neural interactions must separately declare:

- `READ_RAW`;
- `READ_DERIVED`;
- `WRITE_STIMULATE`;
- `WRITE_MODULATE`.

READ and WRITE may share electrodes, transports, clocks, or physical nodes but MUST NOT share implied authority. A declaration that hardware can stimulate does not authorize stimulation.

## Capability versus authority

A device profile can truthfully state physical capability without creating permission:

```text
capability declaration != execution authority
sensor visibility != semantic truth
transport success != admissibility
WRITE support != WRITE authorization
receiver identity != consent
model output != actuation authority
```

StegCore remains the admissibility/consequence authority for governed effects. The SDK remains a compatibility/intake boundary.

## Host-side SDK model

The common host SDK should expose at least:

```text
discover()
identify()
capabilities()
configure()
start_capture()
stop_capture()
stream_native()
stream_normalized()
clock_status()
device_health()
firmware_identity()
receipt()
```

A device adapter transforms device-native packets into the appropriate domain record while retaining an immutable/native reference when available.

```text
device-native bytes
  -> preserve native evidence
  -> transport/device adapter
  -> common device envelope
  -> StegHealth or StegNeuro profile
  -> domain processing
```

## Why the separation matters

The same electronics can support different semantics. A biopotential AFE could carry ECG, EMG, EEG, or other electrical observations depending on site/profile. The reusable device substrate should therefore be classified by transport/capture capabilities while Health/Neuro classify meaning and governance.

## Cross-repository acceptance boundary

This document transfers the shared-device architectural requirement into the SDK repository. It does not claim the implementation exists yet.

Required next implementation work belongs to a dedicated SDK task/issue and should include:

1. common device/capability schema;
2. transport-neutral packet/envelope contract compatible with StegHealth raw preservation;
3. reference Python host client;
4. device adapter interface;
5. READ/WRITE capability separation and authority-neutrality tests;
6. StegHealth reference profile fixture;
7. StegNeuro reference profile fixture covering whole-nervous-system anatomical/pathway classification without implying semantic decoding;
8. conformance tests and SDK workflow integration.

## Relationship to continuity/reconstruction

The shared SDK must preserve enough timing, sequence, configuration, provenance, and source identity for downstream HB/DeltaHB and Master Records reconstruction. Master Records, not the SDK, owns inference-window/reconstruction qualification.
