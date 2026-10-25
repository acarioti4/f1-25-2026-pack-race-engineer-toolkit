# F1 25 (2026 Pack) Race Engineer Toolkit

A Python telemetry toolkit for **F1 25: 2026 Season Pack UDP specification v1.2**, targeting a Windows desktop application with PySide6. The current prototype records compressed UDP captures and decodes selected player telemetry and lap data. The desktop interface is not yet implemented.

## Current status

Capture playback supports explicit raw, unversioned compressed, and identified compressed inputs. Recording uses a separate Git-ignored `live_capture.bin` destination, initializes new or empty files with a versioned header, and validates an existing header before appending.

Temporary diagnostics confirmed exact record readback, preservation of existing bytes during append, and unchanged rejection of incompatible headers. These checks used simulated reception, not live UDP or game verification. Existing-record integrity checks, bounded decompression, and permanent regression coverage remain incomplete.

Next development priorities are callable script entry points, complete resource cleanup, and shared decoding separated from presentation. See [ROADMAP.md](ROADMAP.md) and [project status](Where%20We%20Left%20Off.md).

## Features

- Play back explicitly selected raw, unversioned compressed, or identified compressed input.
- Save and read complete records through shared length-prefixed zlib functions; the two-record disk check passes, while live use and full game-capture playback remain pending.
- Record identified compressed captures with header compatibility checks and a separate ignored destination.
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

```bash
python udpreceiver.py
```

The receiver targets `127.0.0.1:20888` and appends identified version-1 compressed records to `live_capture.bin` beside the scripts. A missing or empty destination receives one header; a nonempty destination must pass marker/version validation before recording. Raw and unversioned compressed files are rejected. Stop with **Ctrl+C**. The destination is Git-ignored; keep renamed recordings ignored or outside the repository too.

Header compatibility and append/readback passed temporary simulated-receiver diagnostics. Actual UDP/game recording with this arrangement has not been verified, and valid headers do not establish record integrity. Callable entry points and complete resource cleanup remain pending; importing the receiver currently starts it.

### Run the storage check

```bash
python -B capture_io.py
```

Expected output: `Success!` followed by `Missing version correctly rejected!`. This deliberately replaces only `compression_roundtrip.bin` beside the scripts, which is ignored by Git. It tests two complete records and EOF through the shared functions. It does not start the receiver or decoder, require the game, or verify telemetry layouts. The `__name__` condition runs the check only when this module is launched directly; importing its functions does not run the check.

The checking function is permanent project code. Its generated data file is replaceable; there is no separate practice script.

### Decode a capture

```bash
python f1decoder.py
```

Before launching, select the intended file path and matching `input_format` in `f1decoder.py`:

| Input arrangement | Setting |
| --- | --- |
| Legacy timestamp-length-payload records | `raw` |
| Earlier compressed records without a file header | `unversioned_compressed` |
| New recordings with marker/version header | `identified_compressed` |

The saved defaults remain `f1_capture.bin` and `unversioned_compressed`. To replay a new receiver recording, select `live_capture.bin` and `identified_compressed`; the receiver's new destination does not automatically change playback settings. Identified input validates its header once before reading records. Selection is explicit, not automatic format detection.

The old `f1_capture.bin` is absent. Its existing ZIP archive is unchanged; neither script supports ZIP input. Paths are relative to the scripts. Playback selection passed temporary synthetic checks; full new-format game-capture playback remains pending.

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

Wheel temperatures, pressures, and contact surfaces are displayed in left rear (LR), right rear (RR), left front (LF), right front (RF) order. The application uses **core temperature**, which maps to `m_tyresInnerTemperature` in the UDP specification.

The application deliberately displays `m_drs` as **Closed/Open** (0/1), with **Unknown** for unexpected values. Protocol references retain the specification name. Raw DRS and surface IDs remain in variables but are not printed. Support for the 2025 packet format is much later; the current decoder accepts 2026 only.

15 of the 16 fields within the player Car Telemetry record are decoded. Individual rev-light bits, the three trailing packet fields, and other cars remain to be added.

## Validation and limitations

Before engine temperature was added, an October 20, 2026 capture playback processed **71,243 records** without error, including **9,695 Car Telemetry** and **9,695 Lap Data** packets. Observed values included speeds of 0–318 km/h, neutral and forward gears 1–8, a stop in neutral, and simultaneous throttle and brake input.

These results demonstrate successful playback with plausible values; exact comparisons with the game's display remain incomplete. Reverse uses signed gear decoding and is assumed working, but was not observed in that capture. Lap progression and full steering travel also remain unverified.

Engine temperature, four-wheel brake/surface/core temperatures, tyre pressures, contact surfaces, clutch, DRS, and rev-light percentage are implemented, specification-reviewed, and syntax-checked. Playback, fixture testing, and exact game comparisons for these additions remain pending. The earlier capture results do not cover these additions. Comment-only edits were checked by syntax-tree comparison and preserved executable behavior.

There is one repeatable storage self-check, but no broader automated test suite. Telemetry fixtures, malformed-input tests, other car indices, and restricted-data handling still need coverage. The two-record check does not exercise the decoder's restored-field validation. Malformed captures, unsupported formats, and unsupported versions of the implemented packet types currently stop the offline decoder with an error. Size limits, bounded decompression, and rejecting extra compressed streams/bytes are also unfinished.

## Next capture and review

Recording header compatibility and a separate destination are complete. Next, separate deliberate script startup and resource cleanup, then shared decoding and presentation. Actual live recording and full new-format game-capture playback remain unverified. Later game comparisons should include several laps and varied telemetry; no additional reverse sample is required.

## Capture format

New receiver files begin with the eight literal bytes `F1DVZCAP` and the one-byte storage version `01`. That header appears once, followed by length-prefixed compressed records. The storage version is independent of the game protocol version.

Each legacy raw capture record contains the following. This is also the byte arrangement to preserve inside future compressed blocks; the current receiver stores each such record inside its own zlib stream, preceded by a four-byte little-endian compressed size:

| Field | Size | Encoding |
| --- | --- | --- |
| Receive timestamp | 8 bytes | Unix nanoseconds, little-endian integer |
| Payload length | 4 bytes | Unsigned little-endian byte count |
| Payload | Variable | Original game UDP bytes |

The current reader recognizes normal end-of-file at the outer compressed-size prefix and checks incomplete fields and mismatched payload sizes. Captures can contain multiple recording periods because recording appends to the existing file.

## Roadmap

### Planned historical storage

As agreed October 22, 2026, build historical storage early, alongside data-pipeline separation and before broad decoding/UI expansion. The shared compressed writer and reader pass the two-record disk check. Raw reading and explicit record selection also passed the October 24 checks; playback integration and recording header compatibility are complete; broader verification remains pending. The planned block storage, rewind reconciliation, archives, and catalog remain unimplemented.

- **While driving:** save binary records in independently compressed temporary blocks using zlib/DEFLATE (initially level 6). Start by measuring approximately 1 MiB blocks, with record/session boundaries and timed flushing. Memory stays bounded and recording does not need space for an entire uncompressed session.
- **When rewinding:** keep history before the destination and replace the abandoned continuation. Remove affected blocks and rebuild the boundary block; reconcile laps, events, and statistics too. The permanent history contains detailed telemetry from kept driving, not abandoned attempts or just a final score.
- **After completion:** stream accepted temporary blocks through decompression into session entries in the corresponding track/layout ZIP. ZIP DEFLATE compresses those records as they are written; do not create nested session ZIPs or a full raw intermediate file. Include session metadata and summaries. Verify the archive and catalog update before removing temporary storage.
- **For browsing:** keep a small, rebuildable catalog outside the ZIPs. List track/session summaries quickly and load detailed telemetry only for selected comparisons. Preserve date, layout, session type, car and available conditions so comparisons have context. CSV can be an export option.

Track identity and FLBK handling will be brought forward from Session/header/Event decoding when needed. Unknown tracks stay unclassified; interrupted sessions stay explicitly incomplete and recoverable. Legacy raw-capture compatibility must remain preserved through the planned shared decoder. Compression/block sizing, recovery, rewind boundaries, and archive updates need tests before this becomes a supported feature. See milestones **2A and 2B** in [ROADMAP.md](ROADMAP.md) for the compression lifecycle, sequencing, and acceptance checks.

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
