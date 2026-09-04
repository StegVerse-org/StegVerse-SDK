# MHIA Reference Connector / Pinout v0

Status: engineering reference candidate; not a manufacturing release and not physically validated.

## Purpose

This document converts the validated MHIA logical attachment and electrical/data contracts into a first concrete ear-module interconnect candidate suitable for reference-firmware and bench-prototype work.

The connector is intentionally separable from the logical MHIA capability manifest. A future mechanical or electrical connector may replace this reference without changing capability identity or authority semantics.

## Reference connector

Reference designation: `MHIA-EAR-8P-MAG-v0`

Candidate physical form: keyed magnetic retention plus eight spring contacts (pogo or equivalent) on a recessed, touch-safe interface. Final geometry, magnet arrangement, plating, ingress protection, creepage/clearance and contact-current rating require hardware engineering validation.

The host/chassis side is the protected power-source side. A detached or unidentified module must not receive main bus power.

## Pin allocation

| Pin | Signal | Direction at host | Safe default | Purpose |
|---|---|---|---|---|
| 1 | GND | — | bonded | primary return / reference |
| 2 | GND_SENSE | input | high impedance | return/contact integrity sense |
| 3 | DETECT_ID | input | pull-up, current limited | passive presence + identification bootstrap |
| 4 | DATA_P | bidirectional | high impedance | differential data positive |
| 5 | DATA_N | bidirectional | high impedance | differential data negative |
| 6 | WAKE_INT | bidirectional | high impedance | negotiated wake/interrupt line |
| 7 | VSAFE | output | current limited | discovery-only low-power rail |
| 8 | VBUS | output | OFF | negotiated operating-power rail |

## Power sequencing

1. Mechanical attachment does not energize VBUS.
2. Host detects passive `DETECT_ID` presence.
3. Host may enable current-limited VSAFE only.
4. Module identity/manifest is read over the discovery path.
5. Manifest, electrical profile and host policy are validated.
6. Required limits are negotiated: voltage, current, thermal envelope and power role.
7. Only after successful admission may VBUS transition from OFF to the negotiated envelope.
8. Any fault, detach, invalid identity, timeout, over-current, over-voltage, thermal trip or negotiation mismatch returns VBUS to OFF and the interface to SAFE_OFF.

## Data bootstrap

The v0 reference uses `DATA_P/DATA_N` as a transport-neutral differential pair. The logical contract does not require USB semantics. A reference implementation may use USB 2.0-compatible electrical signaling, CAN-like signaling, or another qualified half/full-duplex PHY provided the negotiated profile names the concrete transport and remains within the declared electrical envelope.

No host-specific authentication secret is assigned to a connector pin. Endpoint authentication belongs to an authenticated module/secure-element capability and remains distinct from physical attachment.

## Discovery identity

`DETECT_ID` is deliberately low-bandwidth. It may encode only enough information to identify the discovery class and bootstrap a signed/validated module manifest. It is not trusted as authority and cannot independently enable VBUS or consequential capability use.

## Fault posture

Required behavior:

```text
unknown module          -> SAFE_OFF
invalid manifest        -> SAFE_OFF
unsupported power role  -> SAFE_OFF
negotiation timeout     -> SAFE_OFF
over-current            -> ISOLATE -> SAFE_OFF
over-voltage            -> ISOLATE -> SAFE_OFF
thermal trip            -> ISOLATE -> SAFE_OFF
detach                  -> VBUS_OFF immediately
```

## Authority boundary

```text
physical attachment != identity
identity != capability admission
capability discovery != authority
power negotiation != governance authority
connector presence != execution authority
```

TV/TVC remains the protected credential authority where protected credential semantics apply. GitHub has no runtime authority.

## Validation still required

- connector/contact vendor selection;
- maximum continuous and transient current characterization;
- contact resistance and heating;
- ESD/EFT protection;
- reverse-polarity and short-circuit behavior;
- insertion/removal arcing;
- magnet safety and retention force;
- sweat/moisture/corrosion resistance;
- touch safety;
- mechanical cycle life;
- signal integrity for selected PHY;
- EMC/EMI;
- human-factor fit and serviceability.
