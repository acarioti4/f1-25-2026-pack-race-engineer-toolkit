# F1 25 (2026 Pack) Race Engineer Toolkit

A learning project exploring F1 telemetry with Python. The goal is a Windows desktop app built with PySide6 for viewing the data exposed by **F1 25: 2026 Season Pack UDP specification v1.2**.

The prototype contains selected player telemetry and lap decoding, plus shared compressed capture functions that pass a small, repeatable disk round-trip check. Full compressed game-capture playback remains untested. A desktop interface is planned but is not implemented yet.

## October 23 lesson status

The user extracted `write_record` and `read_record` into `capture_io.py`. The receiver imports the writer and supplies each complete timestamp-length-payload record; the decoder imports the reader and receives restored bytes, or `None` at normal EOF. File opening remains in the calling scripts. The receiver opens in binary append mode and writes a four-byte little-endian compressed-size prefix followed by one level-6 zlib stream per complete record. The restored record contains eight timestamp bytes, four original-payload-length bytes, and the original UDP payload. The shared writer checks exact decompression equality before writing.

The decoder opens in binary read mode, reads and checks the outer size prefix, reads exactly that many compressed bytes, checks the returned count, and decompresses them. It selects timestamp bytes with [0:8], original-length bytes with [8:12], and all remaining payload bytes with [12:]. It validates field lengths and compares the entire remaining payload size with the inner length. The latest payload slice is correct by source review.

The user also wrote `check_round_trip` in the shared module. It writes two different complete records through the actual writer, closes and reopens the isolated file, compares both returned records byte-for-byte, and checks that a third read returns `None`. Running `python -B capture_io.py` printed `Success!` during the lesson and again during the documentation/publication review. The originals are 15 and 17 bytes long, using timestamps 1000/2000 and payloads `ABC`/`DEFGH`. These are synthetic storage inputs, not F1 packets. All three Python files pass syntax checking.

No live recording, full compressed game-capture playback, or telemetry fixture checks ran this session. Legacy raw captures and ZIP archives are not detected or supported by the current reader. There is no storage signature/version yet; do not mix experimental compressed records with old captures sharing the same filename. One stream per record is an intermediate step, not the planned multi-record block implementation.

The user wrote all implementation and checking code. Earlier assistant comment edits preserved the pre-edit syntax trees; that historical check applies to those comments, not to the later user-written refactor. The publication review updates documentation without changing executable source.

The next lesson is storage identification/versioning, followed by restoring legacy raw compatibility. See [the handoff](Where%20We%20Left%20Off.md) for the teaching sequence and remaining validation gaps.

## Features

- Save and read complete records through shared length-prefixed zlib functions; the two-record disk check passes, while live use and full game-capture playback remain pending.
- Display selected values from experimental compressed captures; legacy raw playback worked historically but is not supported by the current reader.
- Decode speed, gear, throttle, brake, RPM, steering, and engine temperature from Car Telemetry packets, plus brake, tyre surface, and tyre core temperatures for all four player wheels.
- Decode four-wheel tyre pressures and contact-surface names, clutch input, DRS state, and rev-light percentage.
- Decode current lap time, race position, and lap number from Lap Data packets.
- Identify packet types 0–16; payload decoding currently covers selected fields in packet types 2 and 6.
- Check capture boundaries, packet headers, the 2026 format, and supported versions and player indices for the implemented packet types.

## Getting started

### Requirements

- Python 3
- F1 25 with the 2026 Season Pack for recording live telemetry

The current scripts use only the Python standard library. PySide6 is planned for the desktop interface and is not required to run the prototype.

### Configure the game

Enable UDP telemetry, select the 2026 format, and set the destination to:

| Setting | Value |
| --- | --- |
| IP address | `127.0.0.1` |
| Port | `20888` |

These defaults assume the game and receiver run on the same PC. The game's destination must match `UDP_IP` and `UDP_PORT` in `udpreceiver.py`. This project uses port `20888`, which differs from the specification's example port `20777`.

### Record telemetry

The receiver command remains the same, but its output format has changed. The isolated disk check is complete. Live recording remains deferred while storage identification and compatibility are addressed: the receiver still appends to the historical filename without checking its existing format. The command is:

```bash
python udpreceiver.py
```

The receiver prints its listening address and capture path, then records packets to `f1_capture.bin` beside the scripts. Stop recording with **Ctrl+C**.

Each recording appends to the same file. To start a separate capture, move or rename the existing file before restarting the receiver. Raw captures are excluded from Git.

### Run the storage check

```bash
python -B capture_io.py
```

Expected output: `Success!`. This deliberately replaces only `compression_roundtrip.bin` beside the scripts, which is ignored by Git. It tests two complete records and EOF through the shared functions. It does not start the receiver or decoder, require the game, or verify telemetry layouts. The `__name__` condition runs the check only when this module is launched directly; importing its functions does not run the check.

The checking function is permanent project code. Its generated data file is replaceable; there is no separate practice script.

### Decode a capture

This is the playback command. The current reader requires an experimental length-prefixed zlib capture; old raw captures and ZIPs are not compatible yet:

```bash
python f1decoder.py
```

The decoder targets `f1_capture.bin` beside the scripts. Successful legacy playback previously printed packet metadata, supported values, and the total record count. At this review the raw file is absent; `f1_capture.zip` contains an entry named `f1_capture.bin`, but ZIP input is not supported by either script. File paths are resolved relative to the scripts, regardless of the terminal's working directory.

## Decoded fields

Only the player car's selected fields are currently decoded.

| Packet | Field | Displayed unit or range |
| --- | --- | --- |
| Car Telemetry (6) | Speed | km/h |
| Car Telemetry (6) | Gear | Signed value; 0 = neutral, 1–8 = forward gears, -1 = reverse |
| Car Telemetry (6) | Throttle | % |
| Car Telemetry (6) | Brake | % |
| Car Telemetry (6) | Clutch | %, already supplied as 0-100 |
| Car Telemetry (6) | DRS | Closed/Open; Unknown for unexpected values |
| Car Telemetry (6) | Rev-light indicator | % |
| Car Telemetry (6) | Engine speed | RPM |
| Car Telemetry (6) | Steering | -1 = left, +1 = right |
| Car Telemetry (6) | Engine temperature | Degrees Celsius |
| Car Telemetry (6) | Brake temperatures | Degrees Celsius, all four wheels |
| Car Telemetry (6) | Tyre surface temperatures | Degrees Celsius, all four wheels |
| Car Telemetry (6) | Tyre core temperatures | Degrees Celsius, all four wheels |
| Car Telemetry (6) | Tyre pressures | PSI, all four wheels |
| Car Telemetry (6) | Contact surfaces | Surface names, all four wheels; Unknown for unrecognized IDs |
| Lap Data (2) | Current lap time | Seconds, converted from milliseconds |
| Lap Data (2) | Race position | Position number |
| Lap Data (2) | Current lap number | Lap number |

Wheel temperatures, pressures, and contact surfaces are displayed in left rear (LR), right rear (RR), left front (LF), right front (RF) order. The application uses **core temperature** to match the user's preferred racing terminology; this maps to `m_tyresInnerTemperature` in the UDP specification.

The application deliberately displays `m_drs` as **Closed/Open** (0/1), with **Unknown** for unexpected values. Retain the specification name in protocol references and respect this display preference. Raw DRS and surface IDs remain in variables but are not printed. Support for the 2025 packet format is much later; the current decoder accepts 2026 only.

15 of the 16 fields within the player Car Telemetry record are decoded. Individual rev-light bits, the three trailing packet fields, and other cars remain to be added.

## Validation and limitations

Before engine temperature was added, an October 20, 2026 capture playback processed **71,243 records** without error, including **9,695 Car Telemetry** and **9,695 Lap Data** packets. Observed values included speeds of 0–318 km/h, neutral and forward gears 1–8, a stop in neutral, and simultaneous throttle and brake input.

These results demonstrate successful playback with plausible values; exact comparisons with the game's display remain incomplete. Reverse uses signed gear decoding and is assumed working, but was not observed in that capture. Lap progression and full steering travel also remain unverified.

Engine temperature, four-wheel brake/surface/core temperatures, tyre pressures, contact surfaces, clutch, DRS, and rev-light percentage are implemented, specification-reviewed, and syntax-checked. Playback, fixture testing, and exact game comparisons for these additions remain pending. The earlier capture results do not cover these additions. Comment-only edits were checked by syntax-tree comparison and preserved executable behavior.

There is one repeatable storage self-check, but no broader automated test suite. Telemetry fixtures, malformed-input tests, other car indices, and restricted-data handling still need coverage. The two-record check does not exercise the decoder's restored-field validation. Malformed captures, unsupported formats, and unsupported versions of the implemented packet types currently stop the offline decoder with an error. Size limits, bounded decompression, and rejecting extra compressed streams/bytes are also unfinished.

## Next capture and review

The shared writer and reader agree on the experimental format for the two tested records. Live capture is still deferred pending storage identification, compatibility, and a clearly separated recording destination. After that is resolved, a varied session with several laps, braking and acceleration, and changes in wing state will give the next review more to inspect. If convenient, note a few in-game readings and when they occurred for comparison. No additional reverse sample is required.

The October 22 storage priority still governs the sequence. Shared compressed record I/O and the two-record disk check are complete; storage identification/versioning and legacy compatibility come next. Continue pipeline separation, then bring forward the minimum session/track and flashback fields needed for kept history and completed-session archiving; see ROADMAP.md milestones 2A-2B. Individual rev lights remain queued: `m_revLightsBitValue`, uint16 at record +20, with bits 0-14 representing the 15 lights. This is the only remaining undecoded field within the player Car Telemetry record; trailing fields and other car slots remain unimplemented. Keep storage-check evidence, capture observations, exact game comparisons, and telemetry fixture checks distinct.

Preserve the existing archive separately from compression experiments; recording still appends by default. `f1_capture.bin`, `f1_capture.zip`, and `compression_roundtrip.bin` are now explicitly ignored by Git. The raw file remains absent. The ZIP was previously inspected: its directory lists one `f1_capture.bin` entry (363,003,398 uncompressed bytes; 67,144,886 compressed bytes), and its integrity check passed. Capture framing and decoded values remain unchecked. Future storage directories and renamed captures need ignore coverage when introduced.

## Capture format

Each legacy raw capture record contains the following. This is also the byte arrangement to preserve inside future compressed blocks; the current receiver stores each such record inside its own zlib stream, preceded by a four-byte little-endian compressed size:

| Field | Size | Encoding |
| --- | --- | --- |
| Receive timestamp | 8 bytes | Unix nanoseconds, little-endian integer |
| Payload length | 4 bytes | Unsigned little-endian byte count |
| Payload | Variable | Original game UDP bytes |

The current reader recognizes normal end-of-file at the outer compressed-size prefix and checks incomplete fields and mismatched payload sizes. Captures can contain multiple recording periods because recording appends to the existing file.

## Roadmap

### Planned historical storage

As agreed October 22, 2026, build historical storage early, alongside data-pipeline separation and before broad decoding/UI expansion. The shared length-prefixed compressed writer and reader pass the two-record disk check. Broader verification and legacy detection remain pending. The planned block storage, rewind reconciliation, archives, and catalog remain unimplemented.

- **While driving:** save binary records in independently compressed temporary blocks using zlib/DEFLATE (initially level 6). Start by measuring approximately 1 MiB blocks, with record/session boundaries and timed flushing. Memory stays bounded and recording does not need space for an entire uncompressed session.
- **When rewinding:** keep history before the destination and replace the abandoned continuation. Remove affected blocks and rebuild the boundary block; reconcile laps, events, and statistics too. The permanent history contains detailed telemetry from kept driving, not abandoned attempts or just a final score.
- **After completion:** stream accepted temporary blocks through decompression into session entries in the corresponding track/layout ZIP. ZIP DEFLATE compresses those records as they are written; do not create nested session ZIPs or a full raw intermediate file. Include session metadata and summaries. Verify the archive and catalog update before removing temporary storage.
- **For browsing:** keep a small, rebuildable catalog outside the ZIPs. List track/session summaries quickly and load detailed telemetry only for selected comparisons. Preserve date, layout, session type, car and available conditions so comparisons have context. CSV can be an export option.

Track identity and FLBK handling will be brought forward from Session/header/Event decoding when needed. Unknown tracks stay unclassified; interrupted sessions stay explicitly incomplete and recoverable. Legacy raw-capture compatibility must be restored and preserved through the planned shared decoder. Compression/block sizing, recovery, rewind boundaries, and archive updates need user-written tests before this becomes a supported feature. See milestones **2A and 2B** in [ROADMAP.md](ROADMAP.md) for the compression lifecycle, sequencing, and acceptance checks.

See [ROADMAP.md](ROADMAP.md) for milestones, progress, and completion criteria.

- The [Car Telemetry inventory](CAR_TELEMETRY_INVENTORY.md) is complete. Extend the inventory to other packets and track implementation and validation coverage separately.
- Separate packet receiving, capture reading, decoding, and presentation into shared components.
- Expand decoding to all documented fields and available car slots across packet types 0–16.
- Respect multiplayer restrictions and mode-specific availability, keeping withheld data distinct from measured zero values.
- Maintain shared session and car state, including data freshness, events, and historical records.
- Build a PySide6 interface with live telemetry, capture playback, a searchable field browser, and selectable dashboards.
- Add automated fixture and state checks, complete game comparisons, and package for Windows with PyInstaller.

The initial focus is Windows and the 2026 packet format. Future directions may include support for other protocol years, cloud services, and race-strategy predictions as the project develops.

## License

Licensed under the [MIT License](LICENSE).
