# F1 25 (2026 Pack) Race Engineer Toolkit

## October 24 update — raw reading and explicit reader selection

This is the current status and supersedes older next-task and compatibility notes below. Older dated sections are retained as historical evidence.

The user completed `read_raw_record(capture)` and `read_capture_record(capture, capture_format)` in `capture_io.py`. The raw reader reads eight timestamp bytes, four payload-length bytes, and exactly the decoded payload length; it rejects incomplete fields and returns the original timestamp + length + payload bytes. An empty timestamp read returns `None` at normal EOF. The selector uses `==` to choose `"raw"` or `"compressed"`, calls `read_raw_record` or `read_record`, and returns that reader's result unchanged. Other labels raise `ValueError`. These strings are explicit caller-supplied choices, not automatic file detection.

Verification performed October 24:

- Existing `check_round_trip` and `check_missing_version` both passed again.
- Both selector branches returned the two known records (timestamps 1000/2000, payloads ABC/DEFGH) byte-for-byte, then returned `None` at EOF.
- An unknown format label raised `ValueError`.
- Raw records truncated to 1, 7, 8, 11, 12, and 14 bytes were rejected, covering incomplete timestamps, length fields, and payloads.
- The raw selector read all **358,583 records**, totalling **363,003,398 bytes**, from `f1_capture.bin` inside the existing `f1_capture.zip`, then reached normal EOF. Each returned record's payload size matched its stored length. SHA-256 over all returned record bytes matched a separate streaming read of the original ZIP entry.

The ZIP entry was streamed directly for this diagnostic; no extraction, source edit, or old-capture modification was needed. The existing checks replaced only ignored `compression_roundtrip.bin`, leaving it with the marker-only missing-version input. The additional checks were run from the terminal and are not a saved regression suite. The user wrote the new implementation; the assistant executed the requested verification.

This verifies storage reading and byte preservation, not F1 field decoding or exact game values. The 358,583-record storage read is distinct from the earlier 71,243-record decoder playback. No decoder playback, live UDP recording, telemetry fixture checks, or new game comparisons ran. The diagnostic use of Python's ZIP reader does not add ZIP input support to the application.

**Next lesson:** connect the completed readers to playback with explicit input-format selection and one-time header handling. Distinguish legacy raw input, unversioned compressed input, and identified version-1 compressed input. For an identified file, read/validate the file header once before using the compressed record reader; do not read the header for every record. Missing identification does not prove a file is raw. Then teach safe append checks and a separate ignored recording destination before resuming live recording.

October 24 publication preparation: explanatory comments were added to the raw reader and format selector at the user's request. Syntax-tree comparison against the pre-comment source confirmed unchanged executable behavior, and all three Python files passed syntax parsing. Captures, generated check data, and private instructions remain Git-ignored.

The receiver and decoder still need this integration. Safe append handling, defensive size/decompression limits, multi-record blocks, kept-history reconciliation, archives, and the catalog remain unfinished. Milestones 2, 2A, and 2B remain incomplete.

## October 23 end-of-session update: file headers

The user implemented `write_file_header(capture)` and `read_file_header(capture)` in `capture_io.py`. The identified layout starts with the eight literal bytes `F1DVZCAP`, followed by storage version 1 encoded in one byte, then the existing length-prefixed compressed records. This storage version is independent of the game's protocol version. The reader validates the marker and version and returns the decoded integer version, leaving the file at the first record. File opening and closing remain with the caller.

The existing two-record disk check now uses these header functions and checks the returned version, both exact-byte record comparisons, and EOF. At the user's explicit request, the assistant implemented `check_missing_version`: it writes only the marker and confirms that reading the incomplete header raises `ValueError`. `python -B capture_io.py` printed both `Success!` and `Missing version correctly rejected!`. The second check replaces the same ignored `compression_roundtrip.bin`, so that generated file ends with only the marker. No real capture or archive was modified.

Publication checks: both storage checks passed again, all three Python files passed syntax parsing, and the syntax tree of `capture_io.py` matched its pre-comment snapshot exactly. The explanatory comments preserve executable behavior. Captures and private instructions remain Git-ignored.

Only the shared module and its checks use the new header so far. The receiver and decoder still use the unversioned compressed arrangement; they do not call the header functions. Legacy raw reading, explicit format selection, safe append checks, and a separate live-recording destination remain unfinished. Live recording stays deferred. Unsupported-version, wrong-marker, and partial-marker rejection are present by source review but have not received dedicated checks. No live UDP, game-capture playback, telemetry fixtures, or new game comparisons ran. Milestones 2, 2A, and 2B remain incomplete.

**Resume with one task:** teach and guide `read_raw_record(capture)` in the shared module. Read eight timestamp bytes (empty means EOF; partial means error), four payload-length bytes, then exactly the decoded payload length. Return the original timestamp bytes + length bytes + payload, preserving the same complete-record result as `read_record`. Keep encoded length bytes separate from the decoded integer count. This was explained but has not been implemented. Then add explicit legacy/raw and unversioned-compressed selection, integrate identified headers, and prevent incompatible appends before continuing pipeline separation. ZIP input remains later work. Do not reassign the completed header or missing-version checks.

The user paused because they were tired and found repeated tiny corrections/checks repetitive. Teach the operation and its values before assigning edits; use connected, manageable chunks and review saved attempts. The user's exception authorized the assistant to write the missing-version check only, not future implementation or tests. The user separately authorized explanatory comments, all documentation updates, and Git publication. Default learning rules still apply; private `AGENTS.md` stays local and ignored.

A learning project exploring F1 telemetry with Python. The goal is a Windows desktop app built with PySide6 for viewing the data exposed by **F1 25: 2026 Season Pack UDP specification v1.2**.

The prototype contains selected player telemetry and lap decoding, plus shared compressed capture functions that pass a small, repeatable disk round-trip check. Full compressed game-capture playback remains untested. A desktop interface is planned but is not implemented yet.

## Earlier October 23 lesson status (before file headers)

The user extracted `write_record` and `read_record` into `capture_io.py`. The receiver imports the writer and supplies each complete timestamp-length-payload record; the decoder imports the reader and receives restored bytes, or `None` at normal EOF. File opening remains in the calling scripts. The receiver opens in binary append mode and writes a four-byte little-endian compressed-size prefix followed by one level-6 zlib stream per complete record. The restored record contains eight timestamp bytes, four original-payload-length bytes, and the original UDP payload. The shared writer checks exact decompression equality before writing.

The decoder opens in binary read mode, reads and checks the outer size prefix, reads exactly that many compressed bytes, checks the returned count, and decompresses them. It selects timestamp bytes with [0:8], original-length bytes with [8:12], and all remaining payload bytes with [12:]. It validates field lengths and compares the entire remaining payload size with the inner length. The latest payload slice is correct by source review.

The user also wrote `check_round_trip` in the shared module. It writes two different complete records through the actual writer, closes and reopens the isolated file, compares both returned records byte-for-byte, and checks that a third read returns `None`. Running `python -B capture_io.py` printed `Success!` during the lesson and again during the documentation/publication review. The originals are 15 and 17 bytes long, using timestamps 1000/2000 and payloads `ABC`/`DEFGH`. These are synthetic storage inputs, not F1 packets. All three Python files pass syntax checking.

No live recording, full compressed game-capture playback, or telemetry fixture checks ran this session. At that earlier checkpoint, legacy raw captures and ZIP archives were not supported. The October 24 shared raw reader is now checked; application integration remains pending. The receiver and decoder do not yet use the new shared storage signature/version; do not mix experimental compressed records with old captures sharing the same filename. One stream per record is an intermediate step, not the planned multi-record block implementation.

The user wrote the implementation and round-trip check; the assistant wrote the missing-version check under a specific user exception. Earlier assistant comment edits preserved the pre-edit syntax trees; that historical check applies to those comments, not to the later user-written refactor. The publication review updates documentation without changing executable source.

The next lesson is playback integration of explicit format selection and one-time header handling, followed by safe append checks; shared header functions, raw reading, and record selection are complete. See [the handoff](Where%20We%20Left%20Off.md) for the teaching sequence and remaining validation gaps.

## Features

- Read legacy raw records through the shared raw reader and choose raw/compressed record reading explicitly; playback-script integration remains pending.
- Save and read complete records through shared length-prefixed zlib functions; the two-record disk check passes, while live use and full game-capture playback remain pending.
- Display selected values from experimental compressed captures; legacy raw playback worked historically, and the new shared raw reader still needs connecting to the playback script.
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

Expected output: `Success!` followed by `Missing version correctly rejected!`. This deliberately replaces only `compression_roundtrip.bin` beside the scripts, which is ignored by Git. It tests two complete records and EOF through the shared functions. It does not start the receiver or decoder, require the game, or verify telemetry layouts. The `__name__` condition runs the check only when this module is launched directly; importing its functions does not run the check.

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

The October 22 storage priority still governs the sequence. Shared compressed I/O, header functions, raw reading, and explicit record selection are complete, with the October 24 storage evidence recorded above. Playback integration, one-time header handling, and safe append checks come next. Continue pipeline separation, then bring forward the minimum session/track and flashback fields needed for kept history and completed-session archiving; see ROADMAP.md milestones 2A-2B. Individual rev lights remain queued: `m_revLightsBitValue`, uint16 at record +20, with bits 0-14 representing the 15 lights. This is the only remaining undecoded field within the player Car Telemetry record; trailing fields and other car slots remain unimplemented. Keep storage-check evidence, capture observations, exact game comparisons, and telemetry fixture checks distinct.

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

As agreed October 22, 2026, build historical storage early, alongside data-pipeline separation and before broad decoding/UI expansion. The shared compressed writer and reader pass the two-record disk check. Raw reading and explicit record selection also passed the October 24 checks; application integration and broader verification remain pending. The planned block storage, rewind reconciliation, archives, and catalog remain unimplemented.

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
