# Roadmap

Build a Windows desktop application using Python and PySide6 that exposes all available fields and car slots in **F1 25: 2026 Season Pack UDP specification v1.2**, covering packet types 0–16. Milestones describe development order without fixed release dates.

## Current status — October 27, 2026

Shared compressed capture I/O, storage headers, raw record reading, explicit playback selection, and recording header compatibility are implemented. Recording uses the separate ignored `live_capture.bin` destination. Temporary diagnostics passed initialization, exact append/readback, EOF, and rejection of incompatible headers without modifying their bytes. These results do not establish live UDP operation, telemetry correctness, or existing-record integrity.

Next: callable receiver/playback entry points with complete resource cleanup, followed by shared decoding and separate presentation. Milestones 2, 2A, and 2B remain incomplete. Block storage, rewind reconciliation, archives, and the catalog are not implemented.

Player decoding covers 15 of 16 Car Telemetry record fields plus current lap time, position, and lap number. The October 20 playback covered the original six telemetry fields and three lap fields; later additions still need playback, fixture, and exact game comparisons. See [project status](Where%20We%20Left%20Off.md) for evidence and limitations.

Performance requirements added October 27 are planned work throughout the milestones below. Reception, display refresh, memory limits, maintenance scheduling, and target-PC release budgets have not yet been implemented or verified.

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
- [x] Integrate explicit playback input selection and one-time identified-header validation (October 24; temporary in-memory checks passed for all three arrangements and selected invalid inputs; real-file playback remains pending).
- [x] Prevent header-incompatible appends and use a separate ignored recording destination (October 25; temporary receiver diagnostics passed; existing-record integrity checks remain pending).
- [ ] Preserve new reader coverage in permanent regression checks.
- [ ] Separate UDP reception, capture reading, decoding, and presentation.
- [ ] Keep the reception path limited to receiving, timestamping, basic validation, and bounded handoff. Move compression, compression verification, disk writes/flushes, and expensive history processing to downstream workers.
- [ ] Bound pending work by bytes, including in-flight buffers, and never wait for storage capacity in the receive loop. UDP cannot make the game slow its transmission; implement the explicit overload policy in milestone 2A.
- [ ] Use the same decoder for live packets and saved captures.
- [ ] Return structured header and payload results rather than printing within parsing logic.
- [ ] Report malformed and unsupported packets without terminating live reception.
- [ ] Rate-limit recurring diagnostics and aggregate counters instead of logging every packet. Use blocking waits or event-driven wakeups rather than continuous polling, with a small worker count justified by measurements. Worker threads still consume CPU and disk resources.
- [ ] Preserve the existing timestamp–length–payload capture format.

**Completion criteria:** Decoding works independently of networking and PySide6, and live reception and playback can feed the same downstream data path. Reception does not perform storage or expensive history work, and stalled storage cannot create an unbounded backlog or block the receive loop.

## 2A. Build compressed recording and kept session history early

**Planning decision: October 22, 2026. Foundation started; block storage and kept history are not implemented.** Build this foundation alongside the pipeline separation, before broad packet expansion and desktop work. Historical storage must support comparing kept laps and sessions by track. "Kept results" includes detailed telemetry from the accepted driving timeline, not just finishing position or summary statistics. Abandoned rewind attempts are excluded from permanent session history.

Current intermediate format compresses one complete record at level 6, prefixes its compressed size with four little-endian bytes, and flushes the file after each write. The two-record check passes, but this is not the planned multi-record, timed-flush design below. Original timestamp-length-payload bytes remain unchanged inside compression. Legacy raw reading and explicit playback selection are implemented; cross-format decoded-value comparisons remain pending.

Implementation sequence:

1. Separate capture input/output from decoding and presentation. Retain legacy uncompressed capture reading and the existing timestamp-length-payload records. Live, legacy, compressed, and archived playback must ultimately feed the same decoder.
2. Add lossless compression during recording in a worker outside reception, before waiting for track decoding. Use bounded, independently compressed binary blocks in temporary session storage. The initial design uses zlib/DEFLATE at level 6, with approximately 1 MiB of uncompressed records per block as a starting measurement, not a fixed performance promise. Close blocks on record boundaries and session boundaries; also use a timed flush so sparse traffic does not remain unsaved indefinitely. Benchmark block size, flush interval, total pending bytes, and CPU cost with the game running. Do not flush the compressor for every packet or accumulate a whole session in memory.
3. Bring forward just the shared-header, Session, and Event fields needed for identity and rewind handling: session UID, session time, ordinary and overall frame counters, track/layout and session type, and session-start/end and FLBK events. Consult the supplied specification for exact layouts and availability. Full Session and Event decoding can continue later. Until track identity is known, retain an unclassified temporary session rather than guessing a track.
4. Build the accepted timeline and minimal shared state before permanent archiving. Then add finalization, track ZIPs, and the catalog described below. Then extend individual rev lights and wider packet coverage; storage must not wait for complete decoding or the UI.

Each temporary block needs a versioned wrapper with its sequence, record count, sizes, checksum, and session/time/frame range. A small index locates blocks without decompressing the entire session. Compression must recover the exact original record bytes; do not round values, downsample, or discard undecoded packet types to save space. Keep packet protocol version and storage format version distinct. Preserve raw availability information and distinguish missing or restricted data from measured zero.

**Storage overload policy:** Preserve incoming telemetry at its received rate while recording has capacity. If the capture queue reaches its byte budget, the writer fails, or the configured capture-size limit is reached, stop recording and mark the capture incomplete with the reason and loss counters. Preserve queued records where possible without exceeding the existing budgets, and keep draining UDP for live state. Report the failure through a bounded status path; never block reception, silently downsample capture data, or grow the backlog. Distinguish known capture omissions from upstream UDP loss that may not be measurable. Recording under overload must not be described as lossless.

Define limits for total capture size, raw payload length, compressed record/block size, and decompressed record/block output. Check declared lengths before reading or allocating buffers, and enforce actual output limits during decompression rather than trusting metadata. Bound indexes and recovery work too. The same defensive limits apply to legacy input, playback, and future archive entries; reject oversized input with a clear error.

On a confirmed rewind, keep accepted history before the destination and replace the abandoned continuation. Use FLBK's target time/frame within the same session, together with receipt order and the overall frame counter to distinguish repeated attempts. Ordinary frame numbers and session times can repeat. Reject stale or duplicate packets; a lone backwards packet must not trigger destructive trimming. If FLBK is missing, reconcile corroborating evidence and mark uncertainty rather than silently accepting or deleting ambiguous history.

Discard temporary blocks wholly in the abandoned continuation; decompress the boundary block, retain the accepted records, and recompress that portion. Reconcile samples at the destination per packet/data group as resumed packets arrive, avoiding duplicate boundary samples. Repeated or longer rewinds can reach older blocks; do not assume a fixed 15-second history buffer. Rebuild current state, completed laps, events, best laps, and derived summaries so abandoned results cannot survive. Retain only a small rewind/provenance marker if needed, not the abandoned telemetry. Packet bytes themselves remain unchanged; branch metadata governs playback. Validate the precise boundary behavior using real captures and fixtures before enabling removal.

Give rewind reconciliation a bounded work budget per step, including decompression and rebuilding derived state. Run it outside reception, yield between steps, and bound pending reconciliation work. Mark affected history as reconciling until it is consistent; large or repeated rewinds must not trigger an unlimited synchronous rebuild while driving.

- [ ] Legacy and compressed playback recover identical retained records and decoded values.
- [x] Two synthetic complete records pass shared-function disk readback and EOF checks.
- [ ] Compression/decompression checks pass byte-for-byte, including undecoded payloads.
- [ ] Live recording has measured throughput and byte limits covering queued and in-flight work. Slow/stalled storage exercises the stop-recording policy without blocking UDP reception or hiding omissions.
- [ ] Test capture-size and declared-length limits before allocation, actual decompressed-output limits, and oversized raw/compressed/archive input.
- [ ] Test rewinds within/across blocks, across lap boundaries, repeated destinations, duplicate/delayed/missing FLBK, and session changes.
- [ ] Measure rewind work and pending memory under long and repeated rewinds; verify bounded processing while new packets arrive.
- [ ] Test interrupted writes, corrupt blocks, recovery, and low disk space. Show space usage and stop cleanly before exhaustion.

**Completion criteria:** Compressed temporary recording and accepted-history playback work without changing legacy capture semantics. Capture and decompression limits are enforced, and overload leaves an explicitly incomplete capture while reception continues. Rewinds remove abandoned measurements and results from the accepted history within a measured work and memory budget. Implementation, fixture evidence, and game observations remain separately recorded.

## 2B. Finalize completed sessions into track archives

After the session is completed and rewind reconciliation has settled, finalize its kept history. Session end, user stopping capture, a disconnect, and a crash are distinct: an interrupted recording must remain recoverable and explicitly incomplete, not be silently presented as a completed session. Define a bounded end-of-session settling policy for late result packets and mode-specific absence of final classification.

The permanent layout is one ZIP per track/layout containing uniquely named session entries, for example a session directory with a binary capture, metadata, and summary. Include date, session type, and a unique recording identity so repeated sessions never overwrite one another. Use stable track/layout identity for grouping and readable names for display. Unknown track IDs remain explicitly unclassified. Separate incompatible protocol/game formats in metadata and comparisons.

**Compression lifecycle:**

1. During recording, write the independently compressed temporary blocks described in milestone 2A. Rewind edits operate on these blocks, not on the permanent track ZIP.
2. After completion, stream the accepted blocks through decompression into a new session capture entry in the track ZIP. Use ZIP DEFLATE compression, initially level 6. The ZIP writer recompresses the original binary records as they stream through it. No full uncompressed session file is needed on disk or in memory.
3. Store metadata and summaries as additional ZIP entries. Do not wrap sessions in nested ZIPs or put already-compressed temporary blocks through a second compression layer; the permanent ZIP supplies the compression.
4. Close and verify the archive's new entries, record counts, checksums, and readback before marking the session archived. Retain temporary data until the archive and catalog update are confirmed; cleanup follows successful finalization.

Archive writes must be recoverable and must preserve existing sessions. Decide and test the ZIP append/recovery strategy before implementation; replacement or deletion of existing entries can require rebuilding a large track archive. Budget free space for temporary data plus archive growth and any rebuild. Streamed compression avoids a full raw copy but does not remove that space requirement. If finalization fails, leave the temporary session recoverable and do not publish a successful catalog entry. Retry must not duplicate a session.

Schedule ZIP creation, archive rebuilding, catalog recovery, and detailed comparison work through bounded background jobs. Defer or pause expensive maintenance during active driving, including when a new session starts before finalization finishes; prioritize reception and capture writing. Make long operations resumable or cancellable at bounded work boundaries and limit concurrent CPU/disk work. Streaming bounds buffers but still consumes compression CPU and disk bandwidth, so archive and recovery work must satisfy the measured budgets in milestone 6.

Maintain a small catalog outside the ZIPs for quick browsing: stable session identity, track/layout, date, session type, completion status, archive entry location, format versions, summary statistics, and available comparison context such as car, weather, tyres, and assists. Keep corresponding metadata inside the ZIP so the catalog can be rebuilt. Catalog technology is an implementation choice, not yet selected. Load detailed telemetry on demand through the shared playback path; derive summaries only from kept history and preserve missing-data indicators. CSV is an optional export format, not the primary recording format.

- [ ] Archive only kept history; verify no abandoned telemetry, lap completion, event, or best-lap result remains.
- [ ] Archive playback matches the finalized temporary session, including packets not yet decoded.
- [ ] Test two sessions at the same track, multiple layouts, unknown tracks, and repeated session names.
- [ ] Test archive failure, retry, catalog reconstruction, and recovery without damaging older sessions.
- [ ] Browse summaries without decompressing every track archive; load selected laps/sessions for comparison.
- [ ] Bound archive/recovery job queues, catalog caches, and comparison count and loaded bytes; stream or evict details instead of retaining every selected session indefinitely.
- [ ] Verify maintenance pauses/deferment during driving and safe cancellation/retry without disrupting capture or publishing partial results.

**Completion criteria:** Completed sessions are compressed into their track archives, remain replayable, and are discoverable through a rebuildable catalog. Maintenance and comparison work respect bounded memory, concurrency, and driving-time resource budgets. No permanent archive feature is considered complete until failure recovery and legacy playback checks pass.

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
- [ ] Define explicit byte/count/time limits and eviction or expiry behavior for chart history, event lists, caches, multipart assemblies, and pending state work. Persist kept telemetry separately so trimming display history does not discard capture detail.

**Completion criteria:** Live reception and playback update the same state model, with clear distinctions between current, stale, missing, and restricted data. Retained application state and pending work stay within documented limits during long sessions and session changes.

## 5. Build the Windows desktop interface

- [ ] Add configurable connection settings, initially using `127.0.0.1:20888`.
- [ ] Add start/stop controls, capture recording, and saved-capture playback.
- [ ] Keep reception outside the UI thread with bounded communication to the interface.
- [ ] Preserve telemetry at its incoming rate while refreshing dashboard values independently. Start by measuring a 20–30 Hz display cadence; publish the latest snapshot and coalesce intermediate display updates so queued signals cannot accumulate per packet. Do not apply display coalescing to capture records or required history events.
- [ ] Reduce display refreshes while minimized and refresh from current state on restore. Bound chart/render work as well as displayed history; measure cadence and cost with the game running.
- [ ] Display the currently implemented telemetry and lap fields first.
- [ ] Add a searchable browser covering every catalogued field, with car selection, values, units, and availability.
- [ ] Support selectable dashboard fields.
- [ ] Add timing, tyre/status, and event views using the shared application state.
- [ ] Add a track/session history browser and lap/session comparisons backed by the catalog and kept telemetry; show conditions and missing data when comparing results.

**Completion criteria:** The interface stays responsive during reception and playback, supports clean shutdown and reconnects, and provides access to every catalogued field. Display work runs at a measured cadence with bounded pending updates and lower minimized activity, independently of full-rate telemetry preservation.

## 6. Verify and package

Validation should grow alongside each milestone; this final milestone completes coverage and release checks.

- [ ] Add fixtures for layout sizes, signed values, conversions, car indices, event variants, unsupported versions, unknown enums, and malformed captures.
- [ ] Check session resets, flashbacks, stale data, restricted fields, and multipart history.
- [ ] Compare decoded values with the game and record remaining verification gaps.
- [ ] Check interface responsiveness, disconnect/reconnect, playback, and shutdown.
- [ ] Establish numerical CPU and RAM release budgets on the target Windows PC, recording hardware, game settings, packet rate, test duration, and measurement methods. Include peak memory, sustained CPU, and short CPU bursts; no budgets or performance results are established yet.
- [ ] Compare game frame times with a game-only baseline under matching conditions, recording tail frame times and stutter alongside toolkit CPU/RAM, disk throughput/latency, and GPU activity. A low average CPU percentage alone is not acceptance evidence.
- [ ] Verify the budgets during sustained driving, long captures, full/minimized dashboards, overload, rewinds, playback, and maintenance transitions. Record worker count and queue/memory peaks; block release on budget failures or unexplained frame-time regressions.
- [ ] Package the application for Windows with PyInstaller.
- [ ] Document installation, game settings, capture/playback, and troubleshooting.
- [ ] Verify the packaged application on Windows without a development Python installation.

**Completion criteria:** Full documented decoding coverage, passing fixture and state checks, recorded game-verification results and gaps, and a working Windows package. Release also requires recorded target-PC evidence that numerical CPU/RAM and agreed game-frame-time, disk, and GPU budgets pass, including short bursts and worst-case scenarios rather than averages alone.

## Scope

Windows and the 2026 packet format are the initial targets. The roadmap can grow as the project develops; cloud services, support for other protocol years, and race-strategy predictions are possible future directions. Raw captures stay excluded from Git.
