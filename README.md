# F1 25 (2026 Pack) Race Engineer Toolkit

A Python telemetry toolkit for **F1 25: 2026 Season Pack UDP specification v1.2**, targeting a Windows desktop application with PySide6. The current prototype records raw UDP captures and decodes selected player telemetry and lap data. The desktop interface is not yet implemented.

## Current status

Reviewed against this checkout on November 4, 2026.

Capture playback supports explicit raw, unversioned compressed, and identified compressed inputs. The current receiver appends raw records to Git-ignored `f1_capture.bin` in the working directory. It does not use the shared compressed writer or validate existing file contents before appending.

The two built-in storage checks pass. Temporary synthetic playback checks also pass for all three input arrangements, player slots 0 and 23, all implemented telemetry/lap fields, reverse gear, and unknown surface/packet IDs. Earlier simulated-receiver diagnostics reported compatible append behavior. Live game verification, existing-record integrity checks, bounded decompression, and broader permanent regression coverage remain incomplete.

The receiver now has a guarded `main()` and context-managed socket/file cleanup. Next priorities are a guarded playback entry point, effective receiver configuration, and shared decoding separated from presentation. The planned pipeline must also keep reception quick, bound application memory, and meet measured performance budgets while the game runs. These are requirements, not verified prototype behavior. See [ROADMAP.md](ROADMAP.md) and [project status](Where%20We%20Left%20Off.md).

## Features

- Play back explicitly selected raw, unversioned compressed, or identified compressed input.
- Save and read complete records through shared length-prefixed zlib functions; the two-record disk check passes, while live use and full game-capture playback remain pending.
- Record raw timestamp-length-payload captures; compressed storage helpers remain available separately.
- Decode speed, gear, throttle, brake, RPM, steering, and engine temperature from Car Telemetry packets, plus brake, tyre surface, and tyre core temperatures for all four player wheels.
- Decode four-wheel tyre pressures and contact-surface names, clutch input, DRS state, and rev-light percentage.
- Decode current lap time, race position, and lap number from Lap Data packets.
- Identify packet types 0–16; payload decoding currently covers selected fields in packet types 2 and 6.
- Check capture boundaries, packet headers, the 2026 format, and supported versions and player indices for the implemented packet types.

## Getting started

### Requirements

- Python 3.8 or later for the APIs currently used (`bytes.hex(" ")` requires 3.8); this review used Python 3.12.14 on Linux. Windows runtime verification remains pending.
- F1 25 with the 2026 Season Pack for recording live telemetry

The current scripts use only the Python standard library. PySide6 is planned for the desktop interface and is not required to run the prototype.

Run commands from the repository directory; on Windows, `py` can replace `python` if that is your Python launcher. No dependency installation or build step is needed. Captures and archives are not included in this checkout.

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

The receiver binds `127.0.0.1:20888` and appends raw records to `f1_capture.bin` in the current working directory. Stop with **Ctrl+C**. There is no file header or compatibility check: use a new file or an existing raw capture, and move incompatible compressed data aside before recording. The filename is Git-ignored; keep renamed recordings ignored or outside the repository too.

Importing the receiver no longer starts recording; direct execution calls `main()`. Socket and file context managers cover startup failures and loop exits. The `capture_path`, `udp_ip`, and `udp_port` parameters currently have no effect: binding uses `UDP_IP`/`UDP_PORT`, and file opening hardcodes `"f1_capture.bin"`. Edit the effective values in the code to change them. Earlier header/append diagnostics describe the previous compressed receiver, not the current implementation. Actual UDP/game recording with this revision remains unverified.

### Run the storage check

```bash
python -B capture_io.py
```

Expected output: `Success!` followed by `Missing version correctly rejected!`. This deliberately replaces only `compression_roundtrip.bin` beside the scripts, which is ignored by Git. It tests two complete records and EOF through the shared functions. It does not start the receiver or decoder, require the game, or verify telemetry layouts. The `__name__` condition runs the check only when this module is launched directly; importing its functions does not run the check.

These two checking functions are permanent project code. The second check overwrites the round-trip data, so the generated file ends with only `F1DVZCAP` and is intentionally invalid as a capture. There is no separate practice script.

### Decode a capture

```bash
python f1decoder.py
```

Before launching, edit both settings in `f1decoder.py`; there are no command-line options. For a new receiver recording, use:

```python
input_format = "raw"
# In the existing with open(...) statement:
with open(Path(__file__).resolve().parent / "f1_capture.bin", "rb") as capture:
    ...  # Keep the existing decoding body here.
```

Keep the existing indented body of that `with` statement. Choose the format that matches the file:

| Input arrangement | Setting |
| --- | --- |
| Legacy timestamp-length-payload records | `raw` |
| Earlier compressed records without a file header | `unversioned_compressed` |
| Identified captures with marker/version header | `identified_compressed` |

The saved defaults remain `f1_capture.bin` and `unversioned_compressed`. To replay a current receiver recording, select `raw` and the recorded file. Run the receiver from the repository directory to match the decoder's script-relative `f1_capture.bin` path, or edit the decoder path explicitly. Identified input validates its header once before reading records. Selection is explicit, not automatic format detection.

Neither `f1_capture.bin` nor `f1_capture.zip` is tracked or present in this checkout. Earlier notes describe a local archive used in prior diagnostics; it is not a bundled sample. Extract a capture from your own ZIP before playback; neither script accepts ZIP input. The decoder resolves its default capture path beside the script; the receiver writes relative to the working directory. Importing `f1decoder.py` also starts playback. Full new-format game-capture playback remains pending.

## Repository files

| File | Purpose |
| --- | --- |
| `udpreceiver.py` | Receives and records raw UDP via guarded `main()`; safe to import |
| `f1decoder.py` | Reads a manually selected capture and prints decoded values; starts on import or direct execution |
| `capture_io.py` | Shared storage functions; direct execution runs two storage checks |
| [UDP specification v1.2](Data%20Output%20from%20F1%2025%202026%20Season%20Pack.pdf) | Protocol reference |
| [Car Telemetry inventory](CAR_TELEMETRY_INVENTORY.md) | Field layouts and implementation/verification coverage |
| [Project status](Where%20We%20Left%20Off.md) | Evidence, limitations, and next steps |
| [Roadmap](ROADMAP.md) | Planned features and acceptance criteria |

## Troubleshooting

- **Missing capture:** provide a capture and edit the decoder path and format before running. A fresh checkout has no sample data.
- **Invalid header/format:** match the input format to the actual file. The current receiver appends raw bytes without checking the destination; preserve incompatible data before starting it.
- **Address already in use:** stop another receiver using port `20888`, or edit the receiver port and game destination together.
- **No packets:** check that game UDP output is enabled and matches the receiver address/port. The receiver waits for data and cannot decode live values.

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

These results demonstrate successful playback with plausible values; exact comparisons with the game's display remain incomplete. Reverse uses signed gear decoding and passes the temporary synthetic check, but was not observed in that capture. Lap progression and full steering travel also remain unverified.

On November 4, 2026, both built-in storage checks and syntax parsing of all three modules passed under Python 3.12.14. Temporary in-memory playback diagnostics exercised raw, unversioned compressed, and identified compressed input with player slots 0 and 23. All 15 implemented telemetry fields and three lap fields matched synthetic values, including wheel ordering, unit conversions, reverse gear, an unknown surface ID, and an unknown packet ID. The harness changed only the input-format assignment in an in-memory syntax tree and substituted an in-memory capture; repository source and user captures were not changed.

These six synthetic cases are not a committed regression suite or real game-capture evidence. Historical capture results above do not cover the later temperature, pressure, surface, clutch, DRS, or rev-light additions. Real-capture playback and exact game comparisons for these additions remain pending.

There are two repeatable storage self-checks, but no broader automated test suite. Permanent telemetry fixtures, malformed-input tests, intermediate car indices, split-screen behavior, and restricted-data handling still need coverage. The built-in storage checks do not exercise the decoder's restored-field validation. Malformed captures, unsupported formats, and unsupported versions of the implemented packet types currently stop the offline decoder with an error. Size limits, bounded decompression, and rejecting extra compressed streams/bytes are also unfinished.

The receiver currently prints packet metadata and a full hex dump, writes raw fields, and flushes the file before the next receive; there is no storage worker or byte-bounded handoff yet. The offline decoder prints for every packet. No target-PC CPU/RAM budgets, game frame-time measurements, or desktop refresh controls have been established.

## Next capture and review

Receiver startup and context-managed cleanup are implemented. Compressed recording integration and header-safe append behavior from the previous receiver are no longer present. Next, guard playback startup, make receiver parameters effective, and separate shared decoding and presentation. Actual live recording and full new-format game-capture playback remain unverified. Later game comparisons should include several laps and varied telemetry; no additional reverse sample is required.

## Capture format

Current receiver files contain raw records without a header. Identified compressed captures produced by the shared helpers or previous receiver begin with the eight literal bytes `F1DVZCAP` and the one-byte storage version `01`, followed by length-prefixed compressed records. The storage version is independent of the game protocol version.

Each current or legacy raw capture record contains the following. The shared compressed writer stores this same arrangement inside a zlib stream, preceded by a four-byte little-endian compressed size:

| Field | Size | Encoding |
| --- | --- | --- |
| Receive timestamp | 8 bytes | Unix nanoseconds, little-endian integer |
| Payload length | 4 bytes | Unsigned little-endian byte count |
| Payload | Variable | Original game UDP bytes |

The compressed reader checks the outer size prefix and compressed-byte count, then decompresses the stream; the decoder separately checks the restored timestamp, payload length, and selected game fields. The raw reader checks its timestamp, length, and payload reads. Normal EOF is an empty read at the next record boundary. Neither reader enforces size limits, and the compressed reader does not reject trailing compressed streams/bytes. The decoder checks enough bytes for selected fields rather than requiring a full documented packet layout. Captures can contain multiple recording periods because recording appends to the existing file.

## Roadmap

### Planned performance requirements

The following requirements apply across reception, storage, state, and the future desktop interface. Implementation and performance verification remain pending; the corresponding work and acceptance checks are in [ROADMAP.md](ROADMAP.md).

- **Keep reception quick:** limit the receive path to receiving, timestamping, and a bounded handoff. Move compression, disk writes, and expensive history work to scheduled workers. Bound waiting data by bytes, including work in progress. UDP cannot slow the game's sender: if storage fails or its byte budget fills, stop recording with an explicit incomplete status, reason, and loss counters; preserve queued data where possible and keep receiving for live state. Do not wait for storage or grow an unlimited backlog.
- **Refresh independently:** preserve incoming telemetry at its received rate within storage capacity, while refreshing dashboard values at an initial 20–30 Hz target to validate by measurement. Coalesce intermediate display updates into the latest snapshot so pending UI work stays bounded; reduce refreshes when minimized. Display coalescing must not discard capture records or required history/events.
- **Bound all memory:** cap chart history, event lists, caches, pending work, and loaded comparisons as well as compression blocks. Define retention/eviction behavior and enforce capture/record size and decompressed-output limits before allocating from file-supplied sizes or expanding compressed data.
- **Control maintenance:** defer ZIP creation, archive rebuilding, catalog recovery, and detailed comparisons until active driving ends, or explicitly pause/budget them when driving resumes. Give rewind processing a bounded work budget. Streaming limits memory, but compression and disk access still consume resources.
- **Keep background activity modest:** rate-limit logs, avoid continuous polling, and use a small worker count chosen through measurement. A worker thread can keep the interface responsive while still competing with the game for CPU and disk time.
- **Make performance a release requirement:** establish numeric CPU and RAM budgets on the target Windows PC and verify them with the game running. Measure frame-time spikes and tail latency alongside CPU bursts, memory peaks, disk activity, and GPU use; low average CPU alone is insufficient. Record the hardware, workload, budgets, and results before release.

### Planned historical storage

As agreed October 22, 2026, build historical storage early, alongside data-pipeline separation and before broad decoding/UI expansion. The shared compressed writer and reader pass the two-record disk check. Raw reading and explicit record selection also passed the October 24 checks; playback integration is complete, while recording header compatibility belongs to the previous receiver and must be restored for compressed recording; broader verification remains pending. The planned block storage, rewind reconciliation, archives, and catalog remain unimplemented.

- **While driving:** save binary records in independently compressed temporary blocks using zlib/DEFLATE (initially level 6) outside the receive path. Start by measuring approximately 1 MiB blocks, with record/session boundaries and timed flushing. Bound blocks and the full storage handoff by bytes, using the overload policy above; recording does not need space for an entire uncompressed session.
- **When rewinding:** keep history before the destination and replace the abandoned continuation. Remove affected blocks and rebuild the boundary block; reconcile laps, events, and statistics too, within the rewind work budget. The permanent history contains detailed telemetry from kept driving, not abandoned attempts or just a final score.
- **After completion:** schedule finalization away from active driving, streaming accepted temporary blocks through decompression into session entries in the corresponding track/layout ZIP. ZIP DEFLATE compresses those records as they are written; do not create nested session ZIPs or a full raw intermediate file. Include session metadata and summaries. Verify the archive and catalog update before removing temporary storage.
- **For browsing:** keep a small, rebuildable catalog outside the ZIPs. List track/session summaries quickly and load detailed telemetry only for selected comparisons within explicit memory limits. Schedule catalog recovery and detailed comparisons under the maintenance budget. Preserve date, layout, session type, car and available conditions so comparisons have context. CSV can be an export option.

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
