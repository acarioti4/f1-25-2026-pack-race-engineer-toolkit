# Car Telemetry inventory

Reference map prepared on October 20, 2026; implementation coverage updated October 21, 2026. Source: [supplied UDP specification v1.2](Data%20Output%20from%20F1%2025%202026%20Season%20Pack.pdf), pages 2-3 (header and IDs), 11 (telemetry), 19-20 (restrictions), 21 (wheel order), and 30 (surface types). Implementation checked against `f1decoder.py`; capture evidence comes from `Where We Left Off.md`. The updated decoder passed Python syntax checking; no fixture or capture playback tests were run for this update.

## Packet overview

- Packet ID: 6; packet version: 1; packet format: 2026.
- Sent at the rate selected in the game menus.
- Header: 29 bytes. Car records: 24 slots, 59 bytes each. Trailing fields: 3 bytes.
- Total: 29 + (24 x 59) + 3 = **1448 bytes**, matching the specification.
- Values use little-endian encoding. Fields are packed together without padding.
- An offset is the number of bytes to skip before a field. All offsets start at zero.
- A field in car slot i starts at packet offset **29 + i x 59 + record offset**, with i from 0 to 23. Slots are not race positions. Use Participants data to establish active cars; do not assume all 24 slots are active.

## One car's record

Offsets below count from the beginning of one car's record. Count is the number of values; bytes is their combined storage size. Raw units/ranges describe the transmitted values.

Availability A applies to every row: the specification supplies these fields for cars in the race and does not list them among fields withheld by the Your Telemetry restriction. This is a specification finding, not a multiplayer test. Inactive slots and missing/stale packets must not be presented as genuine zero measurements.

| Field | Type | Count | Bytes | Record offset | Raw unit/range or meaning | Availability |
| --- | --- | ---: | ---: | ---: | --- | --- |
| m_speed | uint16 | 1 | 2 | 0 | km/h | A |
| m_throttle | float | 1 | 4 | 2 | 0.0-1.0 pedal input; current display multiplies by 100 | A |
| m_steer | float | 1 | 4 | 6 | -1.0 full left to +1.0 full right | A |
| m_brake | float | 1 | 4 | 10 | 0.0-1.0 pedal input; current display multiplies by 100 | A |
| m_clutch | uint8 | 1 | 1 | 14 | 0-100 clutch input, percent | A |
| m_gear | int8 | 1 | 1 | 15 | -1 reverse, 0 neutral, 1-8 forward | A |
| m_engineRPM | uint16 | 1 | 2 | 16 | RPM | A |
| m_drs | uint8 | 1 | 1 | 18 | 0 off, 1 on; preserve the specification's name and meaning | A |
| m_revLightsPercent | uint8 | 1 | 1 | 19 | Rev-light indicator percentage | A |
| m_revLightsBitValue | uint16 | 1 | 2 | 20 | Individual LED bits: bit 0 leftmost, bit 14 rightmost; bit 15 unspecified | A |
| m_brakesTemperature | uint16 | 4 | 8 | 22 | Celsius, one per wheel | A |
| m_tyresSurfaceTemperature | uint8 | 4 | 4 | 30 | Celsius, one per wheel | A |
| m_tyresInnerTemperature | uint8 | 4 | 4 | 34 | Celsius, one per wheel | A |
| m_engineTemperature | uint8 | 1 | 1 | 38 | Celsius; this specification uses one byte | A |
| m_tyresPressure | float | 4 | 16 | 39 | PSI, one per wheel | A |
| m_surfaceType | uint8 | 4 | 4 | 55 | Surface ID, one per wheel; lookup below | A |

The final field occupies offsets 55-58, so the next record begins 59 bytes after this one.

All wheel arrays use: **0 rear left, 1 rear right, 2 front left, 3 front right**. Each element starts at the array's offset plus its index multiplied by the size of one element.

Application terminology: **tyre core temperature** maps to the specification's `m_tyresInnerTemperature`. Core and surface are the user's chosen racing terms for display and teaching. The protocol field name remains unchanged in this inventory.

The player decoder reads brake temperatures with `struct.unpack_from("<4H", ...)` and tyre surface/core temperatures with `struct.unpack_from("<4B", ...)`. It checks the field offset plus eight or four bytes respectively, retains each four-value tuple, and indexes it directly in the labelled Celsius output.

The application deliberately displays `m_drs` as **Closed/Open** (0/1), with **Unknown** for unexpected values. Retain the specification name in protocol references and respect this display preference. Raw DRS and surface IDs remain in variables but are not printed. Support for the 2025 packet format is much later; the current decoder accepts 2026 only.

The player decoder also reads four pressures as little-endian floats at +39 (16 bytes), and four contact-surface IDs at +55 (4 bytes). Clutch at +14, DRS at +18, and rev-light percentage at +19 each use one unsigned byte with a bounds check. Clutch and rev-light percentage need no multiplication by 100. Fifteen of sixteen player record fields are implemented; individual rev-light bits remain.

## Whole-packet layout and trailing fields

These offsets count from the start of the UDP packet, excluding the capture file's timestamp and length prefix.

| Field | Type/count | Bytes | Packet offset | Meaning and availability |
| --- | --- | ---: | ---: | --- |
| m_header | PacketHeader | 29 | 0 | Shared packet metadata; individual header-field inventory remains a separate roadmap task |
| m_carTelemetryData | CarTelemetryData[24] | 1416 | 29 | Car slots; per-field details above |
| m_mfdPanelIndex | uint8 | 1 | 1445 | Player's open multifunction-display panel; 255 means closed; panel meanings depend on mode |
| m_mfdPanelIndexSecondaryPlayer | uint8 | 1 | 1446 | Same panel meanings for the secondary player; interpret only when a secondary player exists |
| m_suggestedGear | int8 | 1 | 1447 | Suggested player gear 1-8; 0 means no suggestion |

The header's m_secondaryPlayerCarIndex is 255 when there is no secondary player. Do not invent a no-player sentinel for the secondary MFD field itself.

For single-player race mode, MFD panel IDs are: 0 Car setup, 1 Pits, 2 Damage, 3 Engine, 4 Temperatures. Other modes may use different meanings. The restriction list does not name these trailing fields.

## Coverage and evidence

Reviewed means the layout and meaning were checked against the supplied PDF. It does not mean the decoder has passed tests. Player only means the current decoder selects the header's player-car slot rather than decoding every car.

| Field | Implemented | Specification reviewed | Fixture tested | Game verification |
| --- | --- | --- | --- | --- |
| m_speed | Player only | Yes | No | Capture 0-318 km/h; exact game comparison incomplete |
| m_throttle | Player only, displayed as percent | Yes | No | Capture 0-100%; exact game comparison incomplete |
| m_steer | Player only | Yes | No | Capture approximately -1.00 to +0.73; full travel and exact comparison incomplete |
| m_brake | Player only, displayed as percent | Yes | No | Capture 0-100%; exact game comparison incomplete |
| m_clutch | Player only, percent; syntax check passed | Yes | No | Playback and game comparison pending |
| m_gear | Player only, signed | Yes | No | Neutral and 1-8 observed; reverse assumed working at user request, not observed; exact comparison incomplete |
| m_engineRPM | Player only | Yes | No | Capture 3920-13204 RPM; exact game comparison incomplete |
| m_drs | Player only, Closed/Open display; syntax check passed | Yes | No | Playback and game comparison pending |
| m_revLightsPercent | Player only, percent; syntax check passed | Yes | No | Playback and game comparison pending |
| m_revLightsBitValue | No | Yes | No | Not checked |
| m_brakesTemperature | Player only, all four wheels; syntax check passed | Yes | No | Playback and game comparison pending |
| m_tyresSurfaceTemperature | Player only, all four wheels; syntax check passed | Yes | No | Playback and game comparison pending |
| m_tyresInnerTemperature | Player only, all four wheels, displayed as core temperature; syntax check passed | Yes | No | Playback and game comparison pending |
| m_engineTemperature | Player only; syntax check passed | Yes | No | Playback and game comparison pending |
| m_tyresPressure | Player only, all four wheels in PSI; syntax check passed | Yes | No | Playback and game comparison pending |
| m_surfaceType | Player only, all four wheel IDs and name lookup; syntax check passed | Yes | No | Playback and game comparison pending |
| m_mfdPanelIndex | No | Yes | No | Not checked |
| m_mfdPanelIndexSecondaryPlayer | No | Yes | No | Not checked |
| m_suggestedGear | No | Yes | No | Not checked |

Before engine temperature was added, recorded playback processed 71,243 records, including 9,695 Car Telemetry packets. This is evidence of successful playback with plausible values, not complete decoder verification; it does not cover the temperature, pressure, contact-surface, clutch, DRS, or rev-light-percentage additions. Other car slots, split-screen behavior, multiplayer availability, malformed inputs, and exact in-game comparisons remain untested or incomplete. The decoder currently checks enough bytes for selected fields, not the complete 1448-byte layout.

## Surface lookup

| ID | Surface |
| ---: | --- |
| 0 | Tarmac |
| 1 | Rumble strip |
| 2 | Concrete |
| 3 | Rock |
| 4 | Gravel |
| 5 | Mud |
| 6 | Sand |
| 7 | Grass |
| 8 | Water |
| 9 | Cobblestone |
| 10 | Metal |
| 11 | Ridged |

The surface lookup is implemented for all four player wheels. Unknown IDs display Unknown; raw IDs remain in the decoded tuple but are not printed. Unknown-value behavior has been reviewed in code, not fixture-tested.
