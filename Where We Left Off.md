# Project status

Reviewed November 4, 2026 against the current repository. Documentation and verification evidence were updated after incorporating remote receiver revision `483c35e`; this documentation change does not modify executable code. Performance requirements remain planned work.

## Capture storage and playback

- `capture_io.py` provides compressed record read/write, file header read/write, legacy raw reading, and explicit raw/compressed record selection.
- Identified files begin with `F1DVZCAP` (eight bytes) followed by storage version 1 (one byte). Records contain a four-byte compressed-size prefix and one zlib stream. Restored bytes retain the original eight-byte timestamp, four-byte payload length, and UDP payload.
- Playback explicitly selects `raw`, `unversioned_compressed`, or `identified_compressed`. Identified input validates its header once before the record loop. The defaults remain `f1_capture.bin` and `unversioned_compressed`.
- Current recording uses raw `f1_capture.bin` in `ab` mode relative to the working directory. It has no header or append compatibility validation. The receiver no longer imports the shared compressed helpers. Preserve incompatible files before recording.
- To replay a current recording, select `raw` in the decoder and point it at the recorded file. The decoder default path is script-relative, whereas recording is working-directory-relative. Use `identified_compressed` only for identified captures from the helpers or previous receiver. ZIP input is not implemented. Neither the historical `f1_capture.bin` nor `f1_capture.zip` is present or tracked in this checkout. Prior archive diagnostics below are historical reports using local data, not reproducible from bundled fixtures.

## Verification evidence

### November 4: repository review

Under Python 3.12.14 on Linux, both built-in storage checks passed and all three Python modules passed syntax parsing. Telemetry and Lap Data offsets were compared with the supplied v1.2 PDF.

Six temporary in-memory playback cases covered the three input arrangements at player indices 0 and 23. Assertions matched every implemented telemetry field and the three lap fields, including reverse gear, percentage/time conversions, four-wheel ordering, and unknown surface/packet IDs. The harness replaced the input-format assignment only in an in-memory syntax tree and substituted an in-memory capture through a patched file open. No repository source or user capture was modified.

These diagnostics were not committed as regression tests. They do not verify real UDP reception, Windows operation, game values, all enum branches, intermediate indices, malformed inputs, or restricted data. The historical captures and archive used below are absent from this checkout; their counts and observations are retained as prior reports, not independently reproduced results.

### October 25: recording compatibility (previous receiver)

The following historical diagnostics predate revision `483c35e` and do not describe current raw recording. Temporary terminal diagnostics executed the saved receiver using real temporary files, a simulated socket, and controlled timestamps. They confirmed:

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

`check_round_trip` writes and reads two complete records with a versioned header, checks exact equality, and requires EOF. `check_missing_version` confirms rejection of a marker without its version byte. Both were reported passing on October 24 and passed again on November 4. Direct execution of `capture_io.py` runs them; imports do not. They replace only ignored `compression_roundtrip.bin`, leaving it with the marker-only invalid input after the second check.

### Telemetry playback

The October 20 capture playback, before engine temperature and subsequent additions, processed 71,243 records, including 9,695 Car Telemetry and 9,695 Lap Data packets. Observed speed was 0–318 km/h, gears included neutral and 1–8, RPM was 3,920–13,204, and steering ranged approximately -1.00 to +0.73. Stops in neutral and simultaneous throttle/brake input occurred. Lap time was 0–32.35 seconds, positions included P10/P11/P12/P15/P16/P17, and the lap number remained 1.

These are plausible observations, not exact game comparisons. Reverse was not observed; gear decoding is signed. Full steering travel, lap progression, and a burnout were not established. Later temperature, pressure, surface, clutch, DRS, and rev-light-percentage additions are specification-reviewed and syntax-checked, with temporary synthetic playback assertions passing on November 4; real-capture playback, permanent fixtures, and game comparisons remain pending. The [Car Telemetry inventory](CAR_TELEMETRY_INVENTORY.md) records field-level coverage.

## Known limitations

- Header validation does not establish that existing records are undamaged.
- The decoder executes at import time. The receiver now has guarded `main()` and context-managed socket/file cleanup. Its three configuration parameters are unused: binding uses globals, and file opening hardcodes `"f1_capture.bin"`.
- The receive loop prints metadata/full packet hex and writes/flushes raw records synchronously before the next receive. There is no byte-bounded storage handoff or explicit overload policy yet. UDP cannot make the game slow transmission when storage falls behind.
- Size limits, bounded decompression, strict compressed-stream consumption, and multi-record blocks remain pending.
- Application-wide memory limits, independent/coalesced dashboard refresh, maintenance scheduling, and rewind work budgets are not implemented. Offline playback currently prints for every packet; logging limits and worker counts still need design and measurement.
- No numeric CPU/RAM budgets or target-PC measurements of game frame times, disk activity, and GPU use exist. A responsive interface or low average CPU would not establish acceptable driving performance.
- No full new-format live UDP/game verification or broader permanent regression suite is available in this checkout.
- Decoding and console presentation remain coupled. Most packet types, other car slots, and trailing Car Telemetry fields are not decoded.
- Six unused ID tables match the reviewed numeric assignments: 28 tracks, 19 session types, 18 penalties, 55 infringements, 11 modern F1 teams, and 30 selected drivers. Team/driver coverage is partial; infringement labels 16 and 27 need spelling corrections. Session track -1 requires unknown handling when integrated.
- No desktop interface, kept-history reconciliation, track archives, or catalog is implemented.

## Next development steps

1. Add a guarded callable playback entry point and make receiver parameters effective. Receiver guarded startup and context-managed cleanup are now implemented. Restore safe compressed recording integration before claiming the previous header/append behavior is current.
2. Separate packet decoding from capture handling and console formatting. Return structured results and route live/saved payloads through the same decoder. Keep compression, writes, and expensive history work out of reception; introduce a byte-bounded handoff and the planned overload policy below.
3. Add permanent regression coverage for storage compatibility, integrated paths, error handling, and resource limits. Enforce capture/record size and decompressed-output limits before allocation or expansion.
4. Continue block compression, minimum session/track/flashback fields, accepted-history reconciliation with a rewind work budget, and verified archive/catalog finalization under [roadmap milestones 2A–2B](ROADMAP.md).
5. As state and desktop work proceeds, bound chart/event history, caches, pending work, and loaded comparisons. Preserve incoming records independently of coalesced dashboard refresh, initially measuring 20–30 Hz and reducing refreshes when minimized.
6. Establish numeric CPU/RAM budgets on the target Windows PC and carry them through development and release checks. Measure game frame-time spikes and tail latency, CPU bursts, memory peaks, disk activity, and GPU use alongside capture correctness.

Retain `127.0.0.1:20888`, the original record bytes, wheel order LR/RR/LF/RF, tyre core temperature terminology, and Closed/Open DRS display. Use the supplied UDP specification v1.2 as the layout source of truth. Individual rev-light bits remain the only undecoded field within the player Car Telemetry record; other cars and trailing packet fields remain separate work. Milestones 2, 2A, and 2B are incomplete.

## Performance planning — October 27

These requirements remain unimplemented. Bound storage waiting data and in-progress buffers by bytes. If the budget fills or storage fails, stop recording with an explicit incomplete status, reason, and loss counters, preserve queued data where possible, and continue receiving for live state. Do not block reception waiting for storage or silently grow a backlog; lossless recording cannot be promised under UDP overload. Coalescing dashboard updates must not remove capture records or required history/events.

Schedule ZIP creation, archive rebuilding, catalog recovery, and detailed comparisons away from active driving; pause or budget them when driving resumes. Streaming bounds memory but still consumes compression CPU and disk bandwidth. Rewind reconciliation also needs bounded work so repeated rewinds cannot monopolize processing. Use rate-limited logs, avoid continuous polling, and choose a small worker count by measurement; threads do not remove CPU cost.

The initial display rate and approximately 1 MiB storage blocks are measurement starting points. CPU/RAM budgets and acceptance thresholds still need to be established and recorded on the target PC; no performance result is implied by this documentation update. See the [planned performance requirements](README.md#planned-performance-requirements) and [roadmap acceptance checks](ROADMAP.md).
