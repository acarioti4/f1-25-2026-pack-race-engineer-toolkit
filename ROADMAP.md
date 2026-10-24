# Roadmap

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

The goal is a Windows desktop application built with Python and PySide6 that exposes every field available through **F1 25: 2026 Season Pack UDP specification v1.2**, across all available cars and packet types 0–16.

This is a hobby learning project. Milestones describe the intended development order, with no fixed release dates. See the [README](README.md) for setup instructions and current features.

## Earlier progress baseline (see latest update above)

October 23 completed lesson: the user moved length-prefixed zlib writing and reading into `capture_io.py`, imported those functions into the receiver and decoder, and wrote a permanent `check_round_trip` using them. Direct execution printed `Success!`, confirming exact-byte recovery of two different complete records and normal EOF; the publication review repeated the same check successfully. All three Python files pass syntax checking. The module's direct-run condition prevents imports from running the check. Full compressed game-capture playback, legacy detection, storage versioning, multi-record blocks, and archives remain unfinished. Earlier assistant comment-only syntax-tree checks are historical and do not cover the later user-written refactor.

Roadmap review: this is partial progress on milestone 2 and the first storage verification in 2A. The overall Windows/PySide6 and full 2026 packet coverage goal remains unchanged. The sequence remains storage identification and compatibility, defensive reads and blocks, minimum session/track/flashback decoding, kept history and archives/catalog, wider decoding, shared application state, UI, and packaging. Full pipeline separation and milestones 2A-2B are not complete.

Six ID dictionaries were added and specification-reviewed. Tracks (28), session types (19), penalties (18), and infringements (55) cover their appendix lists; teams (11 modern 2026 F1 teams) and drivers (30) are partial. Numeric assignments match; infringement labels 16 and 27 need spelling corrections. These tables are not connected to packet decoding, so Session, Participants, and Event coverage is unchanged.

Teaching must explain concepts before assigning edits, remain concise at the user's requested moderate pace, and continue directly in project files. Give connected steps as one manageable lesson rather than requiring a turn for each tiny change. Keep reusable implementation and checks; temporary generated test data is appropriate, disposable practice code is not. The roadmap is planning context, not an engineering assignment for the learner.

- [x] Record raw UDP packets with receive timestamps.
- [x] Read saved captures and identify packet types 0–16.
- [x] Decode player speed, signed gear, throttle, brake, RPM, and steering.
- [x] Decode player current lap time, race position, and lap number.
- [x] Exercise the original six telemetry fields and three lap fields through saved game-capture playback.
- [x] Add player engine temperature; specification review and syntax check passed.
- [x] Add brake, tyre surface, and tyre core temperatures for all four player wheels; layout review and syntax check passed.
- [x] Add four-wheel tyre pressures and contact-surface names; reviewed and syntax-checked.
- [x] Add clutch, DRS Closed/Open state, and rev-light percentage; reviewed and syntax-checked.
- [x] Extract shared compressed record reading/writing into `capture_io.py`.
- [x] Pass the user-written two-record disk round-trip check with exact-byte comparisons and EOF.
- [ ] Exercise all additions since the original six telemetry fields through saved-capture playback.
- [ ] Add individual rev-light bits, the remaining field within the player Car Telemetry record.
- [ ] Complete exact comparisons with the game's display.
- [ ] Add broader automated telemetry, malformed-input, and state tests beyond the storage self-check.
- [ ] Build the desktop interface.

Before engine temperature was added, the October 20, 2026 playback processed 71,243 records without error, including 9,695 Car Telemetry and 9,695 Lap Data packets. This establishes successful playback with plausible values, not complete decoder verification, and does not cover the temperature, pressure, contact-surface, clutch, DRS, or rev-light-percentage additions. Reverse is assumed working through signed decoding but was not observed in that capture. Lap progression and full steering travel remain unverified.

The application calls the specification's `m_tyresInnerTemperature` **tyre core temperature**, following the user's preferred racing terminology.

The application deliberately displays `m_drs` as **Closed/Open** (0/1), with **Unknown** for unexpected values. Retain the specification name in protocol references and respect this display preference. Raw DRS and surface IDs remain in variables but are not printed. Support for the 2025 packet format is much later; the current decoder accepts 2026 only.

## 1. Catalogue the specification

- [x] Complete the [Car Telemetry inventory](CAR_TELEMETRY_INVENTORY.md), including every per-car record field and packet trailing field.
- [x] Record Car Telemetry specification names, types, offsets, units, array ordering, and availability rules.
- [x] Track Car Telemetry implementation, specification review, fixture testing, and game verification as separate statuses.
- [ ] Extend the inventory to every packet type, header field, event variant, and lookup table.

**Completion criteria:** Every documented field has an inventory entry, and the existing decoder's coverage and verification gaps are accurately represented.

## 2. Separate the data pipeline

- [x] Extract record compression and disk reading/writing into shared functions used by the scripts and storage check.
- [x] Implement shared file marker/version functions and pass the existing header-aware storage checks.
- [x] Implement raw record reading and explicit raw/compressed record selection.
- [x] Exercise both selector branches, EOF, unknown labels, and sampled raw truncations in terminal diagnostics.
- [x] Read the full archived raw capture through the selector and verify returned-byte preservation (358,583 records; no telemetry decoding).
- [ ] Integrate explicit playback input selection and one-time identified-header validation.
- [ ] Prevent incompatible appends and use a separate ignored recording destination.
- [ ] Preserve new reader coverage in permanent user-written regression checks.
- [ ] Separate UDP reception, capture reading, decoding, and presentation.
- [ ] Use the same decoder for live packets and saved captures.
- [ ] Return structured header and payload results rather than printing within parsing logic.
- [ ] Report malformed and unsupported packets without terminating live reception.
- [ ] Preserve the existing timestamp–length–payload capture format.

**Completion criteria:** Decoding works independently of networking and PySide6, and live reception and playback can feed the same downstream data path.

## 2A. Build compressed recording and kept session history early

**Planning decision: October 22, 2026. Foundation started; block storage and kept history are not implemented.** Build this foundation alongside the pipeline separation, before broad packet expansion and desktop work. Historical storage must support comparing the user's kept laps and sessions by track. "Kept results" includes detailed telemetry from the accepted driving timeline, not just finishing position or summary statistics. Abandoned rewind attempts are excluded from permanent session history.

Current intermediate format compresses one complete record at level 6, prefixes its compressed size with four little-endian bytes, and flushes the file after each write. The two-record check passes, but this is not the planned multi-record, timed-flush design below. Original timestamp-length-payload bytes remain unchanged inside compression. Restoring legacy input support is still required.

Introduce this in manageable lessons:

1. Separate capture input/output from decoding and presentation. Retain legacy uncompressed capture reading and the existing timestamp-length-payload records. Live, legacy, compressed, and archived playback must ultimately feed the same decoder.
2. Add lossless compression during recording, before waiting for track decoding. Use bounded, independently compressed binary blocks in temporary session storage. The initial design uses zlib/DEFLATE at level 6, with approximately 1 MiB of uncompressed records per block as a starting measurement, not a fixed performance promise. Close blocks on record boundaries and session boundaries; also use a timed flush so sparse traffic does not remain unsaved indefinitely. Benchmark block size, flush interval, and CPU cost with the game running. Do not flush the compressor for every packet or accumulate a whole session in memory.
3. Bring forward just the shared-header, Session, and Event fields needed for identity and rewind handling: session UID, session time, ordinary and overall frame counters, track/layout and session type, and session-start/end and FLBK events. Consult the supplied specification for exact layouts and availability. Full Session and Event decoding can continue later. Until track identity is known, retain an unclassified temporary session rather than guessing a track.
4. Build the accepted timeline and minimal shared state before permanent archiving. Then add finalization, track ZIPs, and the catalog described below. Resume individual rev lights and wider packet coverage in manageable lessons; storage must not wait for complete decoding or the UI.

Each temporary block needs a versioned wrapper with its sequence, record count, sizes, checksum, and session/time/frame range. A small index locates blocks without decompressing the entire session. Compression must recover the exact original record bytes; do not round values, downsample, or discard undecoded packet types to save space. Keep packet protocol version and storage format version distinct. Preserve raw availability information and distinguish missing or restricted data from measured zero.

On a confirmed rewind, keep accepted history before the destination and replace the abandoned continuation. Use FLBK's target time/frame within the same session, together with receipt order and the overall frame counter to distinguish repeated attempts. Ordinary frame numbers and session times can repeat. Reject stale or duplicate packets; a lone backwards packet must not trigger destructive trimming. If FLBK is missing, reconcile corroborating evidence and mark uncertainty rather than silently accepting or deleting ambiguous history.

Discard temporary blocks wholly in the abandoned continuation; decompress the boundary block, retain the accepted records, and recompress that portion. Reconcile samples at the destination per packet/data group as resumed packets arrive, avoiding duplicate boundary samples. Repeated or longer rewinds can reach older blocks; do not assume a fixed 15-second history buffer. Rebuild current state, completed laps, events, best laps, and derived summaries so abandoned results cannot survive. Retain only a small rewind/provenance marker if needed, not the abandoned telemetry. Packet bytes themselves remain unchanged; branch metadata governs playback. Validate the precise boundary behavior using real captures and user-written fixtures before enabling removal.

- [ ] Legacy and compressed playback recover identical retained records and decoded values.
- [x] Two synthetic complete records pass shared-function disk readback and EOF checks.
- [ ] Compression/decompression checks pass byte-for-byte, including undecoded payloads.
- [ ] Live recording has bounded memory/queues and measured throughput; report overload or dropped packets.
- [ ] Test rewinds within/across blocks, across lap boundaries, repeated destinations, duplicate/delayed/missing FLBK, and session changes.
- [ ] Test interrupted writes, corrupt blocks, recovery, and low disk space. Show space usage and stop cleanly before exhaustion.

**Completion criteria:** Compressed temporary recording and accepted-history playback work without changing legacy capture semantics. Rewinds remove abandoned measurements and results from the accepted history. Implementation, fixture evidence, and game observations remain separately recorded.

## 2B. Finalize completed sessions into track archives

After the session is completed and rewind reconciliation has settled, finalize its kept history. Session end, user stopping capture, a disconnect, and a crash are distinct: an interrupted recording must remain recoverable and explicitly incomplete, not be silently presented as a completed session. Define a bounded end-of-session settling policy for late result packets and mode-specific absence of final classification.

The permanent layout is one ZIP per track/layout containing uniquely named session entries, for example a session directory with a binary capture, metadata, and summary. Include date, session type, and a unique recording identity so repeated sessions never overwrite one another. Use stable track/layout identity for grouping and readable names for display. Unknown track IDs remain explicitly unclassified. Separate incompatible protocol/game formats in metadata and comparisons.

**Compression lifecycle:**

1. During recording, write the independently compressed temporary blocks described in milestone 2A. Rewind edits operate on these blocks, not on the permanent track ZIP.
2. After completion, stream the accepted blocks through decompression into a new session capture entry in the track ZIP. Use ZIP DEFLATE compression, initially level 6. The ZIP writer recompresses the original binary records as they stream through it. No full uncompressed session file is needed on disk or in memory.
3. Store metadata and summaries as additional ZIP entries. Do not wrap sessions in nested ZIPs or put already-compressed temporary blocks through a second compression layer; the permanent ZIP supplies the compression.
4. Close and verify the archive's new entries, record counts, checksums, and readback before marking the session archived. Retain temporary data until the archive and catalog update are confirmed; cleanup follows successful finalization.

Archive writes must be recoverable and must preserve existing sessions. Decide and test the ZIP append/recovery strategy before implementation; replacement or deletion of existing entries can require rebuilding a large track archive. Budget free space for temporary data plus archive growth and any rebuild. Streamed compression avoids a full raw copy but does not remove that space requirement. If finalization fails, leave the temporary session recoverable and do not publish a successful catalog entry. Retry must not duplicate a session.

Maintain a small catalog outside the ZIPs for quick browsing: stable session identity, track/layout, date, session type, completion status, archive entry location, format versions, summary statistics, and available comparison context such as car, weather, tyres, and assists. Keep corresponding metadata inside the ZIP so the catalog can be rebuilt. Catalog technology is an implementation choice, not yet selected. Load detailed telemetry on demand through the shared playback path; derive summaries only from kept history and preserve missing-data indicators. CSV is an optional export format, not the primary recording format.

- [ ] Archive only kept history; verify no abandoned telemetry, lap completion, event, or best-lap result remains.
- [ ] Archive playback matches the finalized temporary session, including packets not yet decoded.
- [ ] Test two sessions at the same track, multiple layouts, unknown tracks, and repeated session names.
- [ ] Test archive failure, retry, catalog reconstruction, and recovery without damaging older sessions.
- [ ] Browse summaries without decompressing every track archive; load selected laps/sessions for comparison.

**Completion criteria:** Completed sessions are compressed into their track archives, remain replayable, and are discoverable through a rebuildable catalog. No permanent archive feature is considered complete until failure recovery and legacy playback checks pass.

## 3. Complete documented decoding

- [ ] Expand Car Telemetry and Lap Data to every documented field and available car slot.
- [ ] Complete Session and Participants; the minimum header/Session/Event fields needed by milestones 2A-2B come first.
- [ ] Add Car Status, Car Damage, Car Setups, and Car Telemetry 2.
- [ ] Add Motion and Motion Ex.
- [ ] Add Events and every documented event payload variant.
- [ ] Add Session History, Tyre Sets, and Lap Positions.
- [ ] Add Final Classification, Lobby Info, and Time Trial.
- [ ] Handle active counts, player and split-screen indices, and multipart lap-position history.
- [ ] Preserve unknown enum values and distinguish withheld or unavailable data from genuine zero measurements.

**Completion criteria:** Every field in the specification is accessible through structured results, with mode-specific availability and multiplayer restrictions respected. Implementation coverage remains separate from verification coverage.

## 4. Maintain shared application state

- [ ] Track session identity, car identity, latest values, events, and supplied historical records independently of widgets.
- [ ] Preserve raw values alongside units and readable labels.
- [ ] Track receive time, freshness, and availability by data group.
- [ ] Handle session changes, flashbacks, missing packets, and stale data.
- [ ] Assemble multipart history without mixing incompatible session data.
- [ ] Extend the minimal session/rewind state from milestone 2A rather than creating a separate historical state path.

**Completion criteria:** Live reception and playback update the same state model, with clear distinctions between current, stale, missing, and restricted data.

## 5. Build the Windows desktop interface

- [ ] Add configurable connection settings, initially using `127.0.0.1:20888`.
- [ ] Add start/stop controls, capture recording, and saved-capture playback.
- [ ] Keep reception outside the UI thread with bounded communication to the interface.
- [ ] Display the currently implemented telemetry and lap fields first.
- [ ] Add a searchable browser covering every catalogued field, with car selection, values, units, and availability.
- [ ] Support selectable dashboard fields.
- [ ] Add timing, tyre/status, and event views using the shared application state.
- [ ] Add a track/session history browser and lap/session comparisons backed by the catalog and kept telemetry; show conditions and missing data when comparing results.

**Completion criteria:** The interface stays responsive during reception and playback, supports clean shutdown and reconnects, and provides access to every catalogued field.

## 6. Verify and package

Validation should grow alongside each milestone; this final milestone completes coverage and release checks.

- [ ] Add fixtures for layout sizes, signed values, conversions, car indices, event variants, unsupported versions, unknown enums, and malformed captures.
- [ ] Check session resets, flashbacks, stale data, restricted fields, and multipart history.
- [ ] Compare decoded values with the game and record remaining verification gaps.
- [ ] Check interface responsiveness, disconnect/reconnect, playback, and shutdown.
- [ ] Package the application for Windows with PyInstaller.
- [ ] Document installation, game settings, capture/playback, and troubleshooting.
- [ ] Verify the packaged application on Windows without a development Python installation.

**Completion criteria:** Full documented decoding coverage, passing fixture and state checks, recorded game-verification results and gaps, and a working Windows package.

## Scope

Windows and the 2026 packet format are the initial targets. The roadmap can grow as the project develops; cloud services, support for other protocol years, and race-strategy predictions are possible future directions. Raw captures stay excluded from Git.

## Earlier milestone task notes (superseded by the resume task above)

**Completed October 23:** shared storage functions and a permanent disk round-trip check in `capture_io.py`. It writes complete records of 15 and 17 bytes to ignored `compression_roundtrip.bin`, closes/reopens the file, compares each restored record with its original, and checks EOF. Running `python -B capture_io.py` prints `Success!`. This is storage evidence, not telemetry fixture or game verification; do not reassign it.

**One next lesson:** explain and guide storage identification and versioning in the real capture I/O code. Teach why a file marker identifies the saved layout and why its version differs from the game's packet version. Follow with legacy raw compatibility and append-time format checks so incompatible records cannot be mixed. Account explicitly for today's unversioned experimental format; do not guess from the `.bin` extension or label every unknown file as valid legacy data. The user writes all implementation and test code, extending the existing reusable functions/checks.

Then expand checks to truncated prefixes/contents, invalid zlib data, zero or unreasonable compressed lengths, and restored-size mismatches. Current reads have no explicit size cap and ordinary zlib decompression does not enforce that the entire supplied compressed region is exactly one stream. Address bounded decompression as well. Keep original packet lengths inside compression unchanged. Then continue toward multi-record blocks, bounded memory/timed flushing, minimum session/track/FLBK decoding, kept history, and archives/catalog. Individual rev lights remain queued.

The isolated check is complete. Live recording remains deferred while storage identification/compatibility and a clearly separated recording destination are addressed; the receiver still appends to `f1_capture.bin` without checking an existing file's format. The raw capture name, existing ZIP, and experimental check file are explicitly ignored. Add ignore coverage for future storage paths when introduced. The user writes all implementation and test code.

The October 22 storage priority still governs the sequence. Shared compressed I/O, header functions, raw reading, and explicit record selection are complete, with the October 24 storage evidence recorded above. Playback integration, one-time header handling, and safe append checks come next. Continue pipeline separation, then bring forward the minimum session/track and flashback fields needed for kept history and completed-session archiving; see ROADMAP.md milestones 2A-2B. Individual rev lights remain queued: `m_revLightsBitValue`, uint16 at record +20, with bits 0-14 representing the 15 lights. This is the only remaining undecoded field within the player Car Telemetry record; trailing fields and other car slots remain unimplemented. Keep storage-check evidence, capture observations, exact game comparisons, and telemetry fixture checks distinct.

Engine temperature, four-wheel brake/surface/core temperatures, tyre pressures, contact surfaces, clutch, DRS, and rev-light percentage are implemented, specification-reviewed, and syntax-checked. Playback, fixture testing, and exact game comparisons for these additions remain pending.
