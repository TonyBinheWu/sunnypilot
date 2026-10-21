# Kia ccNC factory cluster integration: implementation and verification matrix

This document describes **the ccNC Port variant only**. It is not a claim that all Hyundai/Kia/Genesis ccNC instrument clusters use an identical UI protocol. The instrument ECU, ADAS hardware, exact fingerprint, firmware and factory data must be checked independently.

## What exists

- `opendbc/car/hyundai/carstate.py` currently reads factory camera CAN-FD cluster messages `CCNC_0x161` and `CCNC_0x162` via the camera parser, along with `FR_CMR_03_50ms`. On eligible CCNC non-LKA-steering platforms the decoded values and CANParser COUNTER timestamps are copied.
- `opendbc/car/hyundai/carcontroller.py` already emits these same two IDs on `CanBus(CP).ECAN` at the existing 20 Hz schedule when the OEM decoded source is available.
- `opendbc/car/hyundai/hyundaicanfd.py` now repacks source values without removing original FCA/ADAS/HDP faults, warning sounds, traffic signs, nearby targets, and navigation indicators. The input mappings remain untouched.
- Existing Panda CCNC safety allowlisting permits `0x161` and `0x162` only in its explicitly selected CCNC configuration at E-CAN bus 0 and 32 bytes. No new TX authorization was introduced.
- All five device/SunnyLink settings default **off**, are changeable only offroad, and are not enabled for any platform until synchronized CAN/rlog plus physical cluster validation establishes the exact protocol. `CCNC_VERIFIED_CLUSTER_PLATFORMS` is intentionally empty. A DBC match alone is not certification.

### Signals, provenance, confidence, and status

| Feature | Relevant signal(s) | Current source | Software state | Vehicle verification |
| --- | --- | --- | --- | --- |
| LFA | `0x161 LFA_ICON` | car control lateral-active state | Conditional overlay implemented behind verified-only gate; factory value otherwise passed through | Pending |
| HDA, HDP | `0x161 HDA_ICON` and related status | OEM camera | Pass-through only; no synthetic highway status | Pending |
| LKA, LCA state | `0x161 LKA_ICON, LCA_LEFT_ICON, LCA_RIGHT_ICON` | OEM camera | Pass-through only, do not infer LCA from turn signals | Pending |
| Lane-change arrows | `0x161 LCA_LEFT_ARROW, LCA_RIGHT_ARROW` | OEM camera | Pass-through only | Pending |
| Left/right lanes, curvature, centre | `0x161 LANELINE_*, CENTERLINE` | OEM camera | Pass-through only; model confidence and geometry mapping not validated | Pending |
| Cruise speed, following distance | `0x161 SETSPEED_SPEED, DISTANCE` | active sunnypilot controller | Restricted real-value overlay behind verified-only gate | Pending |
| Ahead, adjacent, rear vehicles | `0x162 LEAD*, LEAD_ALT*, LEAD_*_REAR_*` | OEM camera | Pass-through only; no fictional classification/distance | Pending |
| FCA/BCA/HBA/DAW and faults | `0x161 FCA_ICON, FCA_ALT_ICON` and `0x162 FAULT_*` | OEM camera | Pass-through, never clear genuine warning/faults | Pending |
| Navigation | `0x161 NAV_ICON` | OEM camera | Pass-through only; not a turn-guidance/map protocol | Pending |
| Speed limit/road signs | `0x162 SPEEDLIMIT_*, SIGNS, SPEEDLIMIT_WEATHER` | OEM camera | Pass-through only; no unverified mapping from generic sign classifiers | Pending |

The current DBC exposes LEAD/LEAD_LEFT/LEAD_RIGHT shape codes 0–14, including box, car, truck, pedestrian, cycle, motorbike and cone. **LEAD_ALT uses different codes (0–4)**; rear target codes and placement must be evaluated independently. Existence of a code in a DBC is not confirmation the cluster contains or renders the icon asset.

## Compatibility and gating

- Candidate: `KIA_SORENTO_2024` (documented non-HDA II 2024–2025 CAN-FD ccNC); requires actual fingerprint/firmware/CAN and instrument verification.
- Other ccNC platforms: no default permission. Matching `CCNC` flags or a CAN message ID is insufficient.
- `HyundaiFlags.CCNC` and non-LKA-steering bus layout are prerequisites for the existing path, not proof of display behavior.
- Unsupported/unknown protocol: preserve factory payload and forbid newly synthesized graphics.
- The five `CcncCluster*` settings are persistent off-by-default flags with the same independent availability gate on device and SunnyLink.

## Message transport and rollback

| ID | Source | Destination | Payload | Frequency | Policy |
| --- | --- | --- | --- | --- | --- |
| `0x161` | factory camera via camera bus (typically 2) | E-CAN through existing controller, CCNC-specific bus 0 | 32 bytes | existing 20 Hz | Preserve OEM signals; no new IDs |
| `0x162` | factory camera via camera bus (typically 2) | E-CAN through existing controller, CCNC-specific bus 0 | 32 bytes | existing 20 Hz | Preserve OEM faults, targets and warnings |

No Panda safety or ECU-disable change is introduced. CANPacker is responsible for the existing DBC checksum/counter machinery; exact counter and checksum correspondence must be assessed using real OEM frames. Repacking a decoded payload is **not** bit-identical OEM forwarding by itself.

**Disable:** switch the CCNC master off while parked and restart the car/session. The extra overlay no longer writes any signals. The present controller still retransmits the decoded OEM 0x161/0x162 values because Panda forwarding may suppress the originals. Full restoration of physical factory routing (rather than OEM-equivalent repacking) has **not** been verified. For complete rollback, reinstall the known working CCNC Port revision and confirm OEM behavior.

## Safety and outstanding validation

1. Capture synchronized camera/cluster video, bus captures, exact vehicle fingerprint and firmware, while factory symbols are naturally visible at supported speeds.
2. Compare original CAN counter/checksum, payload and transmission timing against repacked 0x161/0x162. The current parser timestamps and a 300 ms freshness gate for both 0x161 and 0x162 prevent retransmission of obviously stale values. Test camera loss, counters, scheduler stalls, mismatched clock domains and recovery; this remains **not a full end-to-end fail-safe** until verified on hardware.
3. Confirm mode transitions for LFA standby/engaged, factory HDA and LCA, lane geometry confidence, arrows, blind-spot warnings, FCA/AEB status and emergency alerts.
4. Verify track classification, front/rear coordinate conventions and expiry. Never fabricate distances from blindspot Boolean values or categories from plain radar range.
5. Verify sign/mapping enums, regional cluster firmware and visibility. Check no error or warning is hidden.
6. Run CI, process replay and Panda Safety regressions before driving; only on-road instrument evidence proves the graphic appeared.

Currently no extra synthetic surrounding target, LCA, HDA/HDP, navigation, or traffic sign overlays are enabled on any real car. The work is a safe staged integration, **not a confirmed full cluster retrofit**.
