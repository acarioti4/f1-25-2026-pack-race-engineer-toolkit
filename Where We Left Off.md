# Where We Left Off: F1 25 (2026 Pack) Race Engineer Toolkit

**Date:** October 23, 2026 (shared storage functions, successful disk round-trip check, and roadmap/publication review)

## Latest lesson and review — resume here

The user completed a lasting storage refactor and check:

- `capture_io.py` contains `write_record(capture, full_packet)` and `read_record(capture)`. The receiver imports the writer; the decoder imports the reader. Each call processes one complete record. The reader returns restored bytes or `None` at normal EOF; malformed prefixes/contents still raise errors.
- The receiver assembles the original eight-byte timestamp, four-byte payload length, and payload before calling the shared writer. The writer uses level-6 zlib, checks decompression equality, writes a four-byte compressed-size prefix followed by compressed contents, and flushes the open file.
- The decoder obtains each restored record from the shared reader, then retains its timestamp/length/payload slicing and telemetry/lap decoding. Decoding and presentation are not yet separated, and importing the receiver/decoder themselves would still execute their top-level work.
- `check_round_trip` is permanent code in `capture_io.py`. It writes two known complete records through `write_record`, closes/reopens ignored `compression_roundtrip.bin`, compares each result from `read_record` with its original, and confirms the third call returns `None`.
- The known records use timestamps 1000/2000 and payloads `ABC`/`DEFGH`; complete lengths are 15 and 17 bytes. These are arbitrary storage inputs, not F1 packets. Both length fields occupy four bytes regardless of the payload length.
- The module's `__name__` condition invokes the check only on direct execution. Imports make the functions available without running the check.

**Verification:** `python -B capture_io.py` printed `Success!` during the lesson and again during the documentation/publication review. This establishes exact-byte disk recovery for both records, crossing the first compressed boundary, and EOF detection. All three Python files pass AST syntax checking. Only the ignored experimental file was written; no live receiver or game-capture playback ran. The raw capture is absent; the existing ZIP remains untouched and ignored.

Publication review also imported the two shared functions successfully without invoking the disk check. Documentation whitespace checks passed, and the remote branch was checked before committing.

**Limits:** this does not verify F1 telemetry fields, the decoder's restored-field validation, full game-capture playback, malformed inputs, or performance. Legacy raw and ZIP reading are unsupported. The format has no identifying marker/version, size/decompression caps, or strict rejection of extra compressed streams/bytes. Per-record compression and flushing are intermediate steps toward multi-record blocks. There is a repeatable storage self-check, not a broader automated test suite.

**Roadmap review:** work remains aligned with milestone 2 (partial capture I/O separation) and the beginning of 2A (lossless storage). The accepted plan still leads through versioning/legacy reads, validation and blocks, minimum session/track/FLBK fields, kept history, track archives/catalog, wider decoding, shared state, PySide6, and Windows packaging. Neither milestone 2 nor 2A is complete. The goal remains every available field/car across 2026 packet types 0-16, with availability restrictions respected.

**One next lesson:** explain and guide storage identification/versioning using the real shared I/O module, then restore legacy raw compatibility and prevent appending incompatible formats. Explain the purpose of a file marker before assigning code, and distinguish the storage version from the F1 protocol version. Account for today's unversioned experimental captures explicitly. Do not reassign the completed two-record check or create disposable practice code.

Then extend checks to truncated prefixes/contents, invalid zlib data, unreasonable sizes, bounded decompression, extra compressed data, and restored-size mismatches. Keep original packet bytes unchanged. Continue toward multi-record blocks, timed flushing, minimum session/track/FLBK decoding, kept history, and archives/catalog. Individual rev lights remain queued.

The isolated verification setup is complete. Keep live recording deferred while format identification/compatibility and a clearly separated recording destination are addressed: the receiver still appends to the historical `f1_capture.bin` name without checking existing contents. Git ignore checks cover `f1_capture.bin`, `f1_capture.zip`, `compression_roundtrip.bin`, and private `AGENTS.md`; future data paths will need corresponding coverage.

All implementation and test code was written by the user. Earlier assistant comment-only AST comparisons remain historical. The current user request explicitly authorizes reviewing the plan, updating all documentation, and committing/pushing today's project changes. It does not authorize assistant-written implementation changes. The local instructions remain private and are not part of the published commit.

## Earlier October 22 review details

The following validation and capture observations are historical; the file-mode, file-object, and compressed-boundary blockers from that lesson were resolved in source on October 23.

New ID tables were compared with the supplied v1.2 PDF (Session unknown-track value on page 4; appendix tables on pages 25-27, 29, and 31-33):

| Dictionary | Coverage and review |
| --- | --- |
| `track_id` | All 28 listed track IDs match, including reverse layouts and Madrid. Session also defines track -1 as unknown; handle it when connecting the lookup. |
| `team_id` | IDs 476-486 correctly identify the 11 modern 2026 F1 teams. The appendix also includes generic/custom teams and other series, including 2026 F2 IDs 489-499; this is a partial table even within the 2026 protocol. Red Bull/Racing Bulls are readable labels for the specification's Red Bull Racing/RB. |
| `driver_id` | All 30 included numeric assignments match. This is a selected subset of the appendix. Alex Albon is a shortened display name for Alexander Albon. |
| `session_type` | All 19 entries (0-18) match. |
| `penalty_type` | All 18 entries (0-17) match in meaning; Stop & Go is a display variant of Stop Go. |
| `infringement_type` | All 55 numeric assignments (0-54) match in meaning. ID 16 says `server this lap` instead of `serve this lap`; ID 27 says `Curner` instead of `Corner`. Braces such as `{n}` and `{Safety Car}` are literal characters in these ordinary strings; no substitution is implemented. ID 35 refers specifically to a safety-car-to-car collision. |

The six new tables are definitions only: none is used by the current parsing or output. They do not implement Session, Participants, or Event decoding, and unknown-ID fallbacks for their future lookups remain to be added. Existing telemetry/lap parsing was otherwise unchanged in the source diff.

Validation: both source files passed AST syntax checking with the bundled Python runtime. No implementation or test code was written. A follow-up run of the saved decoder stopped at line 229 with FileNotFoundError because the raw capture is absent; no records were decoded. Live recording was not run. The file/data-type findings above remain source-review findings; the missing-file failure was reproduced directly. The earlier user-written practice.py demonstration (five bytes compressed to 13 and restored exactly) remains a small historical in-memory check; do not assign more practice-file exercises.

Historical capture state: `f1_capture.bin` was absent beside the scripts. The then-untracked `f1_capture.zip` directory listed one `f1_capture.bin` entry of 363,003,398 uncompressed bytes (67,144,886 compressed bytes). Its standard-library ZIP integrity check passed without extraction. This checked archive integrity, not capture framing, decoded values, or game observations. Neither script reads ZIP archives. October 23 update: the raw file remains absent, and the ZIP and experimental data file are now explicitly ignored.

## Teaching adjustments agreed this session

Teach first, then let the user apply the concept with help as needed. The user is not an engineer; naming an operation and assigning it is not teaching. Start from their actual saved expressions, explain what each relevant value contains and what the operation returns, and group connected edits into one manageable task. When an explanation fails, identify the missing foundation instead of repeating the assignment with more terminology.

The user subsequently requested a somewhat faster pace and concise explanations. Avoid excessive repetition, artificial pauses, and unrelated tiny exercises. **Work directly in the real project files; no more separate practice-file assignments.** This changes the teaching location and pace, not the rule that the user writes all code. Preserve learning progress without assuming verbally introduced concepts have been mastered.

October 23 clarification: use lasting reusable implementation and checks, not throwaway code placed inside a project file. A separate replaceable test-data file is appropriate to protect real captures. The shared module and its check satisfy this preference. The user explained correctly that a function's local variable name need not match the caller's: the return value connects them. Continue distinguishing imports from calls, returned bytes from file objects, integer counts from encoded field widths, and assignment from changing existing data. Review saved attempts before moving on. Requests for a larger lesson mean several explained, connected steps rather than an entire turn for each tiny edit.

## October 22 historical-storage decision

The user requested documentation of an early historical-storage system for per-track, per-session comparison and analysis. This update changes documentation only; it does not implement compression, track decoding, rewind trimming, archives, or a catalog. Earlier verification notes below describe the October 21 handoff; this storage-planning edit does not rerun or certify decoder tests.

Permanent storage should contain only the accepted driving timeline, including detailed telemetry and kept lap/session results. Abandoned rewind attempts must not remain in permanent statistics or telemetry. Record in losslessly compressed temporary binary blocks during driving so disk use is reduced immediately, even before track decoding is added. Initial design: zlib/DEFLATE level 6, approximately 1 MiB blocks plus timed flushing, bounded memory, original timestamp-length-payload records preserved. Block sizing and timing need measurement.

Rewinds trim accepted history at the destination within the same session, remove abandoned blocks, and rebuild the boundary block and affected state/results. Repeated destinations, lap crossings, stale packets, and missing events require explicit checks. Keep temporary recording separate from finalized track ZIPs.

After completion, stream the kept temporary blocks through decompression into uniquely identified session entries inside the track/layout ZIP, where ZIP DEFLATE compresses them. No nested ZIP and no full uncompressed intermediate file. Include metadata and summaries, verify archive readback, update the external catalog, then clean up temporary files. Preserve existing archive sessions and allow safe retries. A small catalog enables track/session browsing and comparisons without unpacking everything; metadata inside each archive makes the catalog rebuildable. Incomplete recordings must remain recoverable and clearly labelled.

**Early sequence:** capture I/O separation and compressed read/write; minimum header/Session/Event identity and FLBK decoding; accepted-history state; completed-session archive and catalog; then wider field coverage and the desktop browser. Bring these dependencies forward rather than waiting for every packet or UI work. Full design and acceptance checks are in ROADMAP.md milestones 2A-2B.

**Historical October 22 next task:** compressed capture writing and reading. The October 23 lesson above supersedes this task: shared storage and the disk round-trip check are complete; format identification/versioning is next. Individual rev lights remain queued after storage foundations. Earlier limited comment/documentation authorization is superseded for this publication task by the user's explicit request to update documentation and publish the current changes.

## Collaboration and learning preferences

The user is not an engineer and is learning through a hobby project. Teach in plain language, explain unfamiliar terms, and give one substantial, coherent practical lesson at a time. The user writes all implementation and test code; the assistant teaches, investigates, and reviews. Follow AGENTS.md. The user asked the assistant to prepare the inventory because that documentation exercise was not interesting to them. Prefer useful coding lessons, with documentation support when requested.

On October 21, the user authorized publishing then-current changes; the October 22 storage-planning request authorized documentation only. On October 23, after completing the storage lesson, the user again explicitly requested a roadmap review, all documentation updates, and Git publication of today's work. These requests do not authorize assistant-written implementation or tests in future sessions. AGENTS.md is intentionally ignored by Git and remains local; these learning preferences are also recorded here for the published handoff.

Use **tyre core temperature** alongside **tyre surface temperature** in the application and teaching. Core is the user's deliberate racing terminology choice and maps to the specification's `m_tyresInnerTemperature`; do not suggest changing the display back to inner temperature. Preserve specification names in protocol reference tables.

The application deliberately displays `m_drs` as **Closed/Open** (0/1), with **Unknown** for unexpected values. Retain the specification name in protocol references and respect this display preference. Raw DRS and surface IDs remain in variables but are not printed. Support for the 2025 packet format is much later; the current decoder accepts 2026 only.

At the October 21 handoff, a longer capture was planned. The current priority is the October 22 storage decision above; the historical verification notes below have not been refreshed by this documentation-only update.

## Earlier completed work (before the receiver compression experiment)

- Receiver records on 127.0.0.1:20888, appending timestamp-length-payload records to f1_capture.bin beside the scripts.
- Decoder checks capture framing and the 2026 format. Packet IDs 6 and 2 require version 1 and a player index from 0 to 23.
- Car Telemetry now reads 15 of the 16 player record fields: speed, signed gear, throttle, brake, clutch, RPM, steering, DRS, rev-light percentage, engine temperature, and four-wheel brake temperatures, tyre surface temperatures, tyre core temperatures, pressures, and contact surfaces. Player record starts at 29 + index * 59.
- The user added engine temperature in packet 6 at record offset +38, checks that the byte exists, reads it as an unsigned byte, and prints degrees Celsius. Review against the specification and Python syntax check passed. The user also corrected the print comment to avoid the outdated six-field count.
- On October 21, the user added brake temperatures at +22 (eight bytes, `<4H`), tyre surface temperatures at +30 (four bytes, `<4B`), and tyre core temperatures at +34 (four bytes, `<4B`). Each has an offset-plus-size bounds check. The four-value tuples are indexed directly in the Celsius output, in LR, RR, LF, RF order. Layout review against the supplied specification and Python syntax checking passed.
- The user added tyre pressures at +39 (four little-endian floats, 16 bytes, PSI) and contact surfaces at +55 (four unsigned bytes), both in LR, RR, LF, RF order with bounds checks. A surface dictionary maps each ID to a name with an Unknown fallback.
- The user added clutch at +14, DRS at +18, and rev-light percentage at +19, each as one unsigned byte with a bounds check. Clutch and rev-light percentage already use percent units. DRS uses one dictionary lookup with an Unknown fallback and the chosen Closed/Open labels. Syntax check passed after the user corrected clutch indexing and the initial DRS loop.
- Lap Data reads current lap time (uint32 milliseconds at record +4, displayed in seconds), position (+32), and lap number (+33). Player record starts at 29 + index * 57.
- CAR_TELEMETRY_INVENTORY.md covers all 16 record fields and three trailing fields, including offsets, sizes, units, availability, wheel order, surface lookup, and separate implementation/review/fixture/game statuses. Packet size totals 1448 bytes.
- README, roadmap, inventory, local instructions, and this handoff distinguish all additions since the original six telemetry fields from earlier capture evidence.
- Explanatory comments were added for the new fields, storage sizes, units, wheel order, raw values, and single-value versus four-value lookups. Syntax-tree comparison against the user-written decoder immediately before these comment edits confirmed unchanged executable behavior. This is not a runtime test.

## Verification evidence and gaps

Before engine temperature was added, capture playback processed **71,243 records** without error, including **9,695 Car Telemetry** and **9,695 Lap Data** packets. No fixture suite exists or was run.

- Speed: 0-318 km/h; neutral and forward gears 1-8 observed.
- Throttle/brake: each 0-100%; 617 samples had both positive. One sample had 0 km/h, neutral, 30.25% throttle, 98.46% brake, and 10,584 RPM.
- 5,796 samples showed a stop in neutral.
- RPM: 3,920-13,204; steering approximately -1.00 to +0.73.
- Lap time: 0-32.35 seconds; positions P10/P11/P12/P15/P16/P17; lap 1 throughout.
- Engine temperature, four-wheel brake/surface/core temperatures, tyre pressures, contact surfaces, clutch, DRS, and rev-light percentage are implemented, specification-reviewed, and syntax-checked. Playback, fixture testing, and exact game comparisons for these additions remain pending. No new capture observations have been reported.

Capture observations are plausible values, not exact comparisons with the game. Reverse is assumed working at the user's request; signed decoding supports it but the capture contained no reverse samples. Do not require another reverse capture next. A burnout was not confirmed. Full steering travel, lap progression, other car slots, malformed input, and restricted-data handling still need verification.

## Next coding lesson and deferred verification

The October 22 storage priority still governs the sequence. Shared compressed record I/O and the two-record disk check are complete; storage identification/versioning and legacy compatibility come next. Continue pipeline separation, then bring forward the minimum session/track and flashback fields needed for kept history and completed-session archiving; see ROADMAP.md milestones 2A-2B. Individual rev lights remain queued: `m_revLightsBitValue`, uint16 at record +20, with bits 0-14 representing the 15 lights. This is the only remaining undecoded field within the player Car Telemetry record; trailing fields and other car slots remain unimplemented. Keep storage-check evidence, capture observations, exact game comparisons, and telemetry fixture checks distinct.

The receiver still targets `f1_capture.bin` in binary append mode. The isolated round-trip check has passed, but new live recording is deferred pending format identification/compatibility and a clearly separated recording destination. Keep raw and compressed captures out of Git, including renamed copies. The private AGENTS.md remains local and ignored.

## Remaining roadmap

There is one repeatable storage self-check, but no broader automated test suite, desktop UI, full-specification catalog, or structured decoder interface yet. The Car Telemetry inventory is complete, but other packets and the shared header still need cataloguing. The offline decoder stops on errors; future live decoding must report diagnostics without stopping reception. Continue toward complete documented decoding, shared state, a PySide6 Windows UI, and packaging. Preserve the timestamp-length-payload records and default receiver address. Captures remain excluded from Git.

Use the supplied Data Output from F1 25 2026 Season Pack.pdf v1.2 as the source of truth.
