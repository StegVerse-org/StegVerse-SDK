# MHIA Reference Component Candidates v0

Status: **engineering candidate set; not a procurement freeze and not physical-validation evidence**.

This document narrows the first two-ear prototype from component classes to concrete manufacturer families that fit the current logical, electrical, and firmware contracts. Final orderable suffixes, package selections, magnet/contact geometry, acoustics, battery cell, PCB stack-up, and distributor availability remain subject to physical-envelope review.

## Candidate set

| Function | Candidate | Rationale for v0 |
|---|---|---|
| Host SoC | Nordic Semiconductor nRF5340 | Dual-core Cortex-M33 wireless SoC; BLE/LE Audio-capable family, USB/SPI/QSPI and DSP-capable application core. Suitable for host-side module discovery/control while preserving a separate governance/admission boundary. |
| Protected operating-power path | Texas Instruments TPS25947 family | Active eFuse family with adjustable current limiting, overvoltage/overcurrent protection, reverse-current blocking, thermal shutdown, enable control and fault signaling. Matches the fail-closed VBUS switching requirement. |
| Module PMIC / battery management | Nordic Semiconductor nPM1300 | Integrated single-cell charger, fuel-gauge support, buck regulators, LDO/load switches and system-management functions over I2C-compatible TWI. Useful for removable powered modules without making the PMIC an authority source. |
| Motion / head-tracking sensor | TDK InvenSense ICM-42688-P | Production 6-axis IMU with I2C/I3C/SPI interfaces and low-noise motion sensing; appropriate for the initial sensor-biased left-ear module. |
| Reference digital audio amplifier | Analog Devices MAX98357A | Production I2S/TDM digital-input Class-D amplifier with 2.5–5.5 V operation and short-circuit/thermal protection; appropriate as a bench/reference output stage rather than a final acoustic design. |

## Official source references

- Nordic nRF5340: https://www.nordicsemi.com/products/nrf5340
- TI TPS25947: https://www.ti.com/product/TPS25947
- Nordic nPM1300: https://www.nordicsemi.com/Products/nPM1300
- TDK InvenSense ICM-42688-P: https://www.invensense.tdk.com/en-us/products/6-axis/icm-42688-p
- Analog Devices MAX98357A: https://www.analog.com/en/products/max98357a.html

## Freeze criteria still required

Before this becomes a procurement BOM, the following must be resolved and retained:

1. exact orderable part suffix/package for each IC;
2. host/module PCB envelope and layer/stack constraints;
3. spring-contact manufacturer and exact 8-contact arrangement;
4. magnet material/size/polarity and retention-force target;
5. connector voltage/current/contact-resistance ratings and creepage/clearance review;
6. actual ear-driver impedance, sensitivity, acoustic volume, and amplifier match;
7. MEMS microphone selection and acoustic port geometry;
8. removable cell chemistry, capacity, protection, connector, and enclosure safety;
9. thermal model and maximum continuous/peak operating power;
10. distributor availability and prototype quantity/cost at the time of procurement.

## Authority boundary

Component selection, attachment, passive identity, successful negotiation, or availability does not grant execution, governance, credential, or consequence authority. The reference firmware remains fail-closed and operating VBUS remains contingent on validated identity, negotiated electrical envelope, and explicit admission.
