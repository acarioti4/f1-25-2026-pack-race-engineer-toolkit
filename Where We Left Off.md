# Project status

Updated October 25, 2026.

## Capture storage and playback

- `capture_io.py` provides compressed record read/write, file header read/write, legacy raw reading, and explicit raw/compressed record selection.
- Identified files begin with `F1DVZCAP` (eight bytes) followed by storage version 1 (one byte). Records contain a four-byte compressed-size prefix and one zlib stream. Restored bytes retain the original eight-byte timestamp, four-byte payload length, and UDP payload.
- Playback explicitly selects `raw`, `unversioned_compressed`, or `identified_compressed`. Identified input validates its header once before the record loop. The defaults remain `f1_capture.bin` and `unversioned_compressed`.
- Recording uses Git-ignored `live_capture.bin` in `a+b` mode. New/empty files receive one header; nonempty files must pass header validation before writes. Both paths seek to the end before reception.
- To replay a new recording, select `live_capture.bin` and `identified_compressed` in the decoder. ZIP input is not implemented. The historical standalone `f1_capture.bin` is absent; its ZIP archive remains unchanged.

## Verification evidence

### October 25: recording compatibility

Temporary terminal diagnostics executed the saved receiver using real temporary files, a simulated socket, and controlled timestamps. They confirmed:

- Missing and empty destinations initialize correctly, including stopping before any packets arrive.
- Header-only files accept a record without another header.
- Restarting preserves earlier bytes and appends a second record. Records with timestamps 1000/2000 and payloads ABC/DEFGH read back exactly, followed by EOF.
- Raw records, unversioned compressed records, partial markers, missing versions, unsupported versions, and wrong markers are rejected unchanged before reception.
- Files and simulated sockets close in the exercised success and rejection paths.

All three Python files passed syntax parsing. Comment-only additions preserved the receiver syntax tree. Git ignore checks cover recording/capture data. These diagnostics are not a permanent regression suite, actual UDP reception, telemetry fixtures, or game verification. No existing captures changed.

### October 24: readers and playback

Both record selectors returned two known records byte-for-byte and then EOF. Unknown labels and sampled raw truncations were rejected. The raw selector streamed all 358,583 records (363,003,398 bytes) from the existing ZIP entry; SHA-256 over returned records matched an independent read of the original entry. The archive was neither extracted nor modified. This establishes storage byte preservation, not telemetry decoding or application ZIP support.

Temporary in-memory playback checks processed two synthetic header-only packets and EOF in each of the three input arrangements. Unknown selection, missing/unsupported versions, and wrong markers were rejected. These checks were not full game-capture playback or permanent tests.

### Permanent storage checks

`check_round_trip` writes and reads two complete records with a versioned header, checks exact equality, and requires EOF. `check_missing_version` confirms rejection of a marker without its version byte. Both passed on October 24. Direct execution of `capture_io.py` runs them; imports do not. They replace only ignored `compression_roundtrip.bin`, leaving it with the marker-only invalid input after the second check.

### Telemetry playback

The October 20 capture playback, before engine temperature and subsequent additions, processed 71,243 records, including 9,695 Car Telemetry and 9,695 Lap Data packets. Observed speed was 0–318 km/h, gears included neutral and 1–8, RPM was 3,920–13,204, and steering ranged approximately -1.00 to +0.73. Stops in neutral and simultaneous throttle/brake input occurred. Lap time was 0–32.35 seconds, positions included P10/P11/P12/P15/P16/P17, and the lap number remained 1.

These are plausible observations, not exact game comparisons. Reverse was not observed; gear decoding is signed. Full steering travel, lap progression, and a burnout were not established. Later temperature, pressure, surface, clutch, DRS, and rev-light-percentage additions are specification-reviewed and syntax-checked, with playback/fixture/game comparisons pending. The [Car Telemetry inventory](CAR_TELEMETRY_INVENTORY.md) records field-level coverage.

## Known limitations

- Header validation does not establish that existing records are undamaged.
- Receiver and decoder execute at import time. A file-open failure after socket creation lies outside the receiver's current cleanup block.
- Size limits, bounded decompression, strict compressed-stream consumption, and multi-record blocks remain pending.
- No full new-format live UDP/game verification or broader permanent regression suite exists.
- Decoding and console presentation remain coupled. Most packet types, other car slots, and trailing Car Telemetry fields are not decoded.
- Six unused ID tables match the reviewed numeric assignments: 28 tracks, 19 session types, 18 penalties, 55 infringements, 11 modern F1 teams, and 30 selected drivers. Team/driver coverage is partial; infringement labels 16 and 27 need spelling corrections. Session track -1 requires unknown handling when integrated.
- No desktop interface, kept-history reconciliation, track archives, or catalog is implemented.

## Next development steps

1. Add callable receiver/playback entry points and direct-run conditions. Ensure imports do not start work and resources close on startup failures as well as loop exits.
2. Separate packet decoding from capture handling and console formatting. Return structured results and route live/saved payloads through the same decoder.
3. Add permanent regression coverage for storage compatibility, integrated paths, and error handling.
4. Continue defensive reads and block compression, minimum session/track/flashback fields, accepted-history reconciliation, and verified archive/catalog finalization under [roadmap milestones 2A–2B](ROADMAP.md).

Retain `127.0.0.1:20888`, the original record bytes, wheel order LR/RR/LF/RF, tyre core temperature terminology, and Closed/Open DRS display. Use the supplied UDP specification v1.2 as the layout source of truth. Individual rev-light bits remain the only undecoded field within the player Car Telemetry record; other cars and trailing packet fields remain separate work. Milestones 2, 2A, and 2B are incomplete.
