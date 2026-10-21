# F1 25 (2026 Pack) Race Engineer Toolkit

A learning project for a Windows telemetry desktop app using Python and PySide6. The current prototype captures UDP packets and reads saved captures; no desktop interface or automated test suite exists yet. The supplied **F1 25: 2026 Season Pack UDP specification v1.2** is the source of truth. The user writes implementation and test code; the assistant explains, investigates, and reviews. See AGENTS.md for the full roadmap.

## Current behavior

- `udpreceiver.py` listens on `127.0.0.1:20888`, prints its address and capture path at startup, and appends packets to `f1_capture.bin` beside the script. It flushes each record and stops with Ctrl+C. It does not print individual packets. Restarting appends to the same file.
- `f1decoder.py` reads every capture record, checks capture boundaries, the 29-byte header, and the 2026 format, and labels packet IDs. For IDs 6 and 2 it checks version 1 and player indices 0-23 before decoding the implemented fields. It prints decoded values, packet metadata, and a final record count. Malformed input or unsupported formats/implemented packet versions terminate the offline reader with an error.
- Car Telemetry fields: player speed (km/h), signed gear, throttle (%), brake (%), RPM, and steering (-1 left to +1 right).
- Lap Data fields: player current lap time (milliseconds converted to seconds), race position, and lap number.
- Both Python files include explanatory comments. Other packet types are named but their payload fields are not yet decoded.

The October 20 capture review, comments, and existing local implementation changes were published to `main` in commit `6fa735a`, followed by merge commit `d5675db` to incorporate the existing GitHub history. Captures remain excluded from version control.

## Run the prototype

Use Python 3; the scripts require only the standard library. In the game enable UDP output, select the 2026 format, and set destination `127.0.0.1:20888` when running on the same PC. The destination must match the receiver settings. The specification's example port 20777 differs from this project's default 20888.

Start recording:

```bash
python udpreceiver.py
```

Stop with Ctrl+C, then inspect the saved capture:

```bash
python f1decoder.py
```

The capture path is relative to the scripts, regardless of the terminal's working directory. Captures may contain multiple recording periods because the receiver appends. Raw captures are local data excluded from Git.

## Capture format

| Field | Size | Encoding |
| --- | --- | --- |
| Receive timestamp | 8 bytes | Unix nanoseconds from time.time_ns(), little-endian |
| Payload length | 4 bytes | Unsigned little-endian byte count |
| Payload | Variable | Original game UDP bytes |

The reader distinguishes normal EOF from truncated timestamps, lengths, and payloads. Game structures are packed and use little-endian values. Player records begin after the 29-byte header: Car Telemetry uses 59-byte records; Lap Data uses 57-byte records.

## Capture validation: October 20, 2026

The existing decoder processed **71,243 complete records**, including **9,695 Car Telemetry** and **9,695 Lap Data** packets, with exit code 0. This was a game-capture playback check, not an automated fixture suite or a simultaneous comparison with the game's display.

| Field or action | Observed result |
| --- | --- |
| Speed | 0-318 km/h |
| Gear | Neutral (0) and forward gears 1-8 |
| Throttle and brake | Each ranged from 0-100% |
| RPM | 3,920-13,204 |
| Steering | Approximately -1.00 to +0.73 |
| Complete stop in neutral | 5,796 telemetry samples at 0 km/h and gear 0 |
| Simultaneous throttle and brake | 617 samples with both positive |
| Example overlap | 0 km/h, neutral, 30.25% throttle, 98.46% brake, 10,584 RPM |
| Current lap time | 0-32.35 seconds |
| Position | P10, P11, P12, P15, P16, P17 |
| Lap number | 1 throughout |

The six telemetry fields produced plausible game-capture values, including the reported stop and pedal overlap. Reverse is **assumed working at the user's request**, based on the signed gear decoding; no reverse sample occurred in this capture. The burnout remains unconfirmed from these six fields alone; wheel-speed or slip data would provide stronger evidence. Lap Data offsets, types, and units were reviewed against the supplied specification, but the decoded lap values still need comparison with the game. Lap progression and full steering travel were not covered.

No synthetic fixtures or malformed-input tests were run. Capture success does not establish every validation branch, other car indices, restricted-data handling, or all documented data coverage. Comment additions were checked to preserve both scripts' Python syntax trees.

## One next learning task

Begin the coverage inventory with a Car Telemetry table: list every documented record field and packet trailing field, type, offset, unit, and availability rule. Track implementation, specification review, fixture testing, and game verification separately. Completion means the whole packet is accounted for against the supplied PDF and the six implemented fields are accurately marked. No new decoder code is needed for this task.

## Roadmap

1. Inventory packet types 0-16, header fields, event variants, and lookup tables; extend decoding one field at a time.
2. Separate receiving, capture reading, decoding, and presentation. Return structured results and preserve the capture format.
3. Decode all documented fields and car slots, respecting active counts, availability, mode differences, and multiplayer restrictions. Withheld data must not appear as genuine zero measurements.
4. Maintain shared session/car state, freshness, events, and historical data independently of widgets.
5. Build the PySide6 Windows interface with reception outside the UI thread, capture/playback, searchable field access, and selectable dashboards.
6. Add user-written fixture and state checks, document game-verification gaps, and package with PyInstaller. Verify on Windows without a development Python installation.

See [Where We Left Off.md](Where%20We%20Left%20Off.md) for the session handoff and [AGENTS.md](AGENTS.md) for collaboration rules and planned acceptance checks. The user continues to write implementation and tests; source comments may be added by the assistant when explicitly requested. Cloud services, other protocol years, and derived race-strategy predictions are outside the current roadmap.
