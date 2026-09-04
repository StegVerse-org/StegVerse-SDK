# MHIA Two-Ear Reference Hardware BOM v0

Status: reference engineering BOM; component classes are selected, manufacturer part numbers are intentionally not frozen until electrical, mechanical, availability, and cost review.

## Prototype objective

Build one two-ear MHIA bench/reference unit demonstrating:

- independent left/right module identity;
- asymmetric capability composition;
- safe discovery before main power;
- replaceable acoustic, sensor, compute/radio, and power modules;
- host-side deterministic capability graph construction;
- fault isolation and immediate VBUS removal;
- no authority inheritance from physical attachment or discovery.

## Host / headband chassis

| Qty | Item | Minimum reference requirement |
|---:|---|---|
| 1 | adjustable headband/chassis | removable left/right interface carriers; no permanently bonded electronics required for ear modules |
| 2 | MHIA-EAR-8P-MAG-v0 host interfaces | keyed 8-contact spring interface with separate magnetic/mechanical retention |
| 1 | host controller MCU | USB-capable MCU with >=2 independent module discovery channels, hardware watchdog, ADC and interrupt inputs |
| 1 | protected VSAFE regulator | current-limited discovery rail with per-port enable/measurement |
| 2 | protected VBUS load switches | independent per-ear current limit, reverse-current protection and fast disconnect |
| 2 | current/voltage monitors | per-ear rail telemetry |
| 2 | temperature sensing channels | interface/module thermal monitoring |
| 1 | debug/programming interface | isolated or protected bench programming connection |
| 1 | host power input | USB-C or protected bench DC input; implementation separate from ear-module connector |

## Left-ear reference module

Role: sensor/audio-biased module.

| Qty | Item | Minimum reference requirement |
|---:|---|---|
| 1 | MHIA-EAR-8P-MAG-v0 module interface | keyed mate |
| 1 | low-power module MCU | manifest service + discovery protocol |
| 1 | audio DAC/amplifier | replaceable acoustic driver path |
| 1 | acoustic driver cartridge | independently replaceable from module electronics where practical |
| 1 | microphone array | >=2 microphones for reference sensing |
| 1 | 6-axis IMU | motion/head-tracking reference sensor |
| 1 | module temperature sensor | local thermal evidence |
| 1 | local nonvolatile identity store | module identity + calibration/provenance fixture |
| 1 | optional secure element footprint | unpopulated acceptable for first electrical prototype; does not grant authority by presence |

## Right-ear reference module

Role: power/audio-biased asymmetric module.

| Qty | Item | Minimum reference requirement |
|---:|---|---|
| 1 | MHIA-EAR-8P-MAG-v0 module interface | keyed mate |
| 1 | low-power module MCU | manifest service + discovery protocol |
| 1 | audio DAC/amplifier | independent right acoustic path |
| 1 | acoustic driver cartridge | independently replaceable |
| 1 | removable battery carrier | protected single-cell rechargeable reference pack or equivalent safe bench substitute |
| 1 | battery protection/measurement | independent protection plus state telemetry |
| 1 | module temperature sensor | local thermal evidence |
| 1 | local nonvolatile identity store | module identity + calibration/provenance fixture |

## Interchangeable module candidates for first physical test

At least two swaps should be tested without replacing the entire headset:

1. left-ear sensor cartridge: `IMU + microphones` replaced by a reduced-sensor cartridge;
2. right-ear power cartridge: lower-capacity/lightweight pack exchanged for higher-capacity pack;
3. optional acoustic cartridge swap with different driver/impedance declaration.

## Bench/support equipment

- current-limited programmable or protected bench supply;
- multimeter;
- oscilloscope;
- USB protocol/debug interface as applicable;
- electronic load for power-envelope testing;
- thermal measurement (thermocouple or IR instrumentation);
- ESD-safe work surface;
- fixture for repeated attach/detach cycles;
- contact-resistance measurement method.

## BOM freeze gates

Manufacturer part numbers SHALL NOT be called frozen until:

1. VSAFE and VBUS voltage/current envelopes are confirmed;
2. contact current and resistance targets are confirmed;
3. selected data PHY is confirmed;
4. MCU I/O/ADC/interrupt requirements are confirmed;
5. battery chemistry and charging architecture are selected;
6. physical envelope/CAD is compatible;
7. thermal and user-contact constraints are reviewed;
8. replacement availability and lifecycle risk are assessed.

## Evidence posture

This BOM is sufficient to structure procurement and detailed engineering. It is not evidence of assembled hardware, physical validation, certification, or runtime activation.
