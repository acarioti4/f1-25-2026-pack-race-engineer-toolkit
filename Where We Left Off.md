# Where We Left Off: F1 25 (2026 Pack) Race Engineer Toolkit

## October 25 — recording header checks complete

This is the current status; older dated sections below are historical. Playback selection and recording header compatibility are complete. The receiver now uses the separate Git-ignored `live_capture.bin` destination in `a+b` mode. It seeks to the end and uses `tell()` to determine size, writes the nine-byte marker/version header only for a new or empty file, or seeks to the beginning and validates an existing header before any write. Both successful branches return to the end before reception. Incompatible files are rejected unchanged.

Temporary terminal diagnostics executed the saved receiver with a temporary destination, simulated socket, and controlled timestamps. Missing and empty files initialized correctly; stopping before packets left a valid header-only file; restarting appended a second record without changing earlier bytes or inserting another header. Both complete records (timestamps 1000/2000, payloads ABC/DEFGH) read back exactly and reached EOF. Raw records, unversioned compressed records, a partial marker, missing version, unsupported version, and wrong marker were rejected unchanged before reception. File and simulated-socket cleanup passed in these cases. All three Python files passed syntax parsing, and `live_capture.bin` passed Git ignore checking.

These are temporary diagnostics, not permanent regression tests, actual UDP reception, telemetry fixtures, or game verification. No existing captures were changed. Header validation does not check existing record integrity. A file-open failure after socket creation still lies outside the current cleanup block; address resource ownership in the next lesson. Milestones 2, 2A, and 2B remain incomplete.

Publication review: explanatory receiver comments were added at the user's request. Syntax-tree comparison against the saved pre-comment source confirmed unchanged executable behavior; all three Python files still parse. Captures and private instructions remain Git-ignored.

**Next lesson:** deliberate script startup. Use the existing direct-run condition in `capture_io.py` as the foundation for callable receiver/playback entry functions so importing them does not start work. Explain file/socket ownership and cleanup. Do not reassign playback selection or recording header checks.

## October 24 lesson close — playback integration complete

This supersedes the playback-integration next task below. At the tired user's explicit request to finish the lesson, the assistant corrected the saved playback conditions to compare input_format and set its default to unversioned_compressed, matching the previous expected input arrangement. The existing user-written branches now select raw or compressed record reading, with identified files validating their header once before the loop.

All three Python files passed syntax parsing. Temporary in-memory diagnostics ran the decoder with its input-format setting overridden and file opening replaced with BytesIO: each of the three arrangements processed two synthetic header-only packets and reached EOF. Unknown selection, missing version, unsupported version, and wrong marker were rejected. No permanent tests were added and no capture files were changed. This does not verify telemetry fields or game values. The real f1_capture.bin is absent; ZIP input remains unsupported.

The lesson is finished; no further assignment tonight. Next, when the user is ready: safe append checks and a separate ignored recording destination. Live recording remains deferred. Milestones 2, 2A, and 2B remain incomplete.

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

## Current game plan — resume after October 25

1. **Deliberate script startup:** teach callable entry functions and direct-run conditions using the saved code. Explain ownership and cleanup of sockets/files, including failures before the receive loop.
2. **Shared decoding and presentation:** return named results from packet decoding and separate console formatting, preserving current fields and labels. Feed live and saved payloads through the same decoder.
3. **Permanent checks:** the user writes regression checks for integrated paths, header rejection without mutation, and error handling. Today's temporary diagnostics do not replace these.
4. Continue defensive size/decompression checks, blocks, minimum session/track/flashback fields, kept history, and archives/catalog under milestones 2A-2B.

The learner completed the recording changes. The assistant ran requested diagnostics and later added comments/documentation under explicit authorization. Comment edits preserve executable behavior. The user found the concrete teaching sequence helpful: explain actual values and Python arguments, then give numbered connected edits and review the saved attempt. Use named `os.SEEK_END` and `os.SEEK_SET` options; distinguish calling with parentheses from selecting with brackets.

## October 23 end-of-session update: file headers

The user implemented `write_file_header(capture)` and `read_file_header(capture)` in `capture_io.py`. The identified layout starts with the eight literal bytes `F1DVZCAP`, followed by storage version 1 encoded in one byte, then the existing length-prefixed compressed records. This storage version is independent of the game's protocol version. The reader validates the marker and version and returns the decoded integer version, leaving the file at the first record. File opening and closing remain with the caller.

The existing two-record disk check now uses these header functions and checks the returned version, both exact-byte record comparisons, and EOF. At the user's explicit request, the assistant implemented `check_missing_version`: it writes only the marker and confirms that reading the incomplete header raises `ValueError`. `python -B capture_io.py` printed both `Success!` and `Missing version correctly rejected!`. The second check replaces the same ignored `compression_roundtrip.bin`, so that generated file ends with only the marker. No real capture or archive was modified.

Publication checks: both storage checks passed again, all three Python files passed syntax parsing, and the syntax tree of `capture_io.py` matched its pre-comment snapshot exactly. The explanatory comments preserve executable behavior. Captures and private instructions remain Git-ignored.

Only the shared module and its checks use the new header so far. The receiver and decoder still use the unversioned compressed arrangement; they do not call the header functions. Legacy raw reading, explicit format selection, safe append checks, and a separate live-recording destination remain unfinished. Live recording stays deferred. Unsupported-version, wrong-marker, and partial-marker rejection are present by source review but have not received dedicated checks. No live UDP, game-capture playback, telemetry fixtures, or new game comparisons ran. Milestones 2, 2A, and 2B remain incomplete.

**Resume with one task:** teach and guide `read_raw_record(capture)` in the shared module. Read eight timestamp bytes (empty means EOF; partial means error), four payload-length bytes, then exactly the decoded payload length. Return the original timestamp bytes + length bytes + payload, preserving the same complete-record result as `read_record`. Keep encoded length bytes separate from the decoded integer count. This was explained but has not been implemented. Then add explicit legacy/raw and unversioned-compressed selection, integrate identified headers, and prevent incompatible appends before continuing pipeline separation. ZIP input remains later work. Do not reassign the completed header or missing-version checks.

The user paused because they were tired and found repeated tiny corrections/checks repetitive. Teach the operation and its values before assigning edits; use connected, manageable chunks and review saved attempts. The user's exception authorized the assistant to write the missing-version check only, not future implementation or tests. The user separately authorized explanatory comments, all documentation updates, and Git publication. Default learning rules still apply; private `AGENTS.md` stays local and ignored.

The following plan and earlier reviews are historical context; the resume task above takes precedence.

**Date:** October 23, 2026 (shared storage functions, successful disk round-trip check, and roadmap/publication review)

## Earlier milestone 2 game plan and lesson plan — retained reference

**Requested October 23:** plan a learning session aimed at finishing step 2 tonight and save the lesson plan here. This section supersedes the earlier next-lesson notes where sequencing differs. It records a plan, not completed implementation. The assistant reviewed the saved `capture_io.py`, `udpreceiver.py`, and `f1decoder.py`; no implementation or test code was changed or run for this planning update.

### Target and game plan

Finish roadmap milestone **2: Separate the data pipeline**, including the storage identification/compatibility groundwork already queued. A pipeline here simply means the steps a packet travels through: obtaining bytes, interpreting them, and displaying the result. Milestones 2A and 2B remain separate: multi-record compression blocks, rewind reconciliation, track archives, and the catalog are later work. Tonight is a target, not a promise about lesson duration; finish based on saved-code review and checks, not the clock.

Current starting point: shared compressed record reading/writing and the two-record disk check are complete. `f1decoder.py` still combines opening the capture, separating timestamp/length/payload, decoding packet fields, and printing. `udpreceiver.py` creates and binds its socket at import time. The existing direct-run condition in `capture_io.py` is the model for controlling when those scripts start.

Work in this order:

1. Identify new capture files and restore an explicit way to read older raw captures, preserving the timestamp-length-payload records. Prevent incompatible appends and keep recording destinations separate from existing captures.
2. Make the receiver and playback start only when deliberately called, with clear ownership of files and sockets.
3. Extract packet interpretation into a callable function that accepts only UDP payload bytes and returns named results. Keep capture timestamps outside the game packet decoder.
4. Move console presentation out of decoding and connect live reception and playback to the same decoding and presentation functions.
5. Check the separated paths and error handling with permanent user-written checks, then compare the evidence against milestone 2's completion criteria.

Preserve existing field coverage, wheel order, Closed/Open and tyre core terminology, and the default `127.0.0.1:20888`. This is a separation lesson, not a packet-expansion assignment. Keep the PDF as the source of truth whenever constructing F1 test packets or revisiting layout details.

### Teaching sequence

Teach and review one lesson chunk at a time. Each chunk can contain several connected edits; do not require a new prompt for every tiny edit. Explain each new concept before asking the user to apply it. The user writes all implementation and checking code. Do not supply replacement functions, patches, or copyable solutions. Review the saved attempt before advancing; explain the first point of confusion when needed. The following is the instructor's sequence, not a list to hand over as one assignment.

**Lesson 1 — Give saved files an identity.**

- Start with the existing four-byte compressed-size prefix: it describes one record's size but does not identify the file's format. Teach a file header as a label written once at the beginning, distinct from both a record prefix and the game's packet header. Teach the identifying marker first, then the storage version as the number describing our own saved layout; it is independent of the game's 2026 format and packet version.
- Guide a small documented marker/version design in `capture_io.py`; the instructor explains the layout rather than asking the learner to invent a storage architecture. Extend the existing reusable check to exercise file initialization and recognition while retaining both exact-byte record comparisons and EOF.
- Once that attempt is understood and reviewed, teach compatibility: a marker identifies new files; lack of a marker does not prove a file is valid legacy data. Provide explicit selection for legacy raw input and today's unversioned compressed experiment, with appropriate record validation. Unknown or unsupported identified formats receive clear errors. ZIP playback remains later work; do not interpret a ZIP as raw records.
- Teach append checks before writing: initialize an empty/new destination once, accept only the supported identified format for normal recording, and reject incompatible existing contents without changing them. Use a distinct ignored recording destination and protect the old capture/archive. Do not write a header before checking a nonempty file.
- Success: user-written checks cover recognized format/version, unsupported or incomplete headers, deliberate legacy/experimental reads, and refusal to append to incompatible files without changing their bytes. The original record contents remain identical after readback. This is basic compatibility evidence, not completion of all defensive storage work in 2A.

**Lesson 2 — Decide when a script starts.**

- Start with the user's existing direct-run condition in `capture_io.py`. Explain that importing makes definitions available but currently also executes the receiver's socket setup and the decoder's file-reading loop. A function postpones that work until it is called; the direct-run condition chooses when to call it.
- Guide moving receiver startup/loop and playback startup/loop into callable entry functions in their real files. Teach passing a capture path or connection setting as an argument using the familiar `write_record(capture, full_packet)` call as the comparison.
- Explain who opens and closes each resource. Ensure the socket closes even if opening the capture fails after socket creation; do not retain the current gap where only errors inside the receive-loop try block trigger socket cleanup.
- Success: importing the modules neither binds a port, opens/writes a capture, starts playback, nor prints telemetry. Deliberate execution still starts the chosen operation. Review saved code before any receiver launch; use only an isolated ignored destination for checks.

**Lesson 3 — Return a decoded result instead of printing it.**

- Start at `payload = restored_record[12:]`: these bytes are the same kind of bytes received as `data` by the receiver. Explain that capture timestamp/length handling belongs to capture reading, while interpreting the game's header and fields belongs to a function receiving just those payload bytes.
- Teach a dictionary as a collection of named results using the user's existing lookup dictionaries as the familiar starting point. Contrast looking up a surface name with returning a collection containing speed, gear, and other values. Explain return values again only as needed: returning a result does not print it or alter the caller's original bytes.
- First guide extraction using the existing header and speed/gear path, review it, then extend the same understood pattern to all currently implemented telemetry and lap fields. The intermediate extraction is not the final milestone state. Preserve raw values alongside display conversions and labels; do not invent zero-filled fields for packet types that are not decoded.
- Keep capture-record validation separate and reusable so playback obtains a timestamp and payload without putting disk operations into the packet decoder. A supported but not-yet-decoded packet can return its known metadata with an explicit undecoded status.
- Success: the decoder accepts packet bytes without a file/socket and returns named header/payload information without printing. All existing decoded fields survive the move. The caller retains the receive timestamp separately.

**Lesson 4 — Connect both sources and keep errors local.**

- Teach presentation as turning those returned values into text, using the existing print statements. Move formatting into a separate callable presentation function; preserve the familiar console output where practical. Both live reception and playback call the same decoder and presenter.
- Trace one packet through each route in plain language: live reception supplies payload bytes directly; playback first removes the saved timestamp/length wrapper. Recording keeps the original bytes, even for packet types we do not decode yet.
- Teach catching an expected decoding error at the caller as deciding what happens next. The decoder can raise a specific, understandable error; the live loop reports it and proceeds to the next datagram. Do not catch every possible exception and hide programming mistakes. Treat unsupported format/version explicitly and distinguish it from a known but undecoded packet type.
- Separate packet errors from storage errors: a malformed game packet must not end reception, but a disk-write failure must not be reported as successful recording. A corrupt capture boundary cannot safely be skipped by guessing where the next record begins; playback should report the problem and stop clearly.
- Success: both routes use the same interpretation and formatting functions; a bad or unsupported packet followed by a valid packet produces a diagnostic followed by the valid result. Storage failures are reported distinctly.

**Lesson 5 — Demonstrate the complete separation.**

- Explain a controlled test packet as bytes with deliberately known values, extending the reasoning behind the existing ABC/DEFGH storage check. Those old synthetic payloads are useful for storage but are not valid F1 packets. Consult the supplied PDF before guiding real packet fixtures. The user writes permanent checks in the project; generated data is temporary and ignored.
- Check known results for the currently supported telemetry and lap paths, then save/read the same packet bytes and compare the decoded results with direct decoding. Equality of two paths proves agreement; known expected values are also needed because both paths could share the same mistake.
- Check quiet imports, unchanged timestamp/length/payload bytes, explicit input-format selection, incompatible append refusal, and malformed/unsupported packet handling followed by a valid packet. Include a bounded local UDP check through the actual receive path, using an isolated ignored capture destination, to establish integration without requiring a game session. Teach its purpose and sender/receiver relationship before assigning it; do not introduce an unexplained testing framework.
- Review resource cleanup, run the relevant checks, and record precisely which passed. Retain earlier capture observations as historical evidence; synthetic and local UDP checks do not establish exact in-game accuracy or full game-capture performance.

### Completion gate and next handoff

Milestone 2 is complete only when packet decoding operates without networking, capture files, printing, or PySide6; both live and saved inputs feed that same decoder; returned values feed separate presentation; packet errors are reported without stopping live reception; and the original timestamp-length-payload records are preserved. Basic legacy compatibility and safe append handling must also work before normal recording resumes. All existing implemented fields must remain accessible, with the relevant user-written checks passing.

At session end, record completed lessons, saved function/file boundaries, exact checks and results, unresolved issues, and one next task. If the completion gate passes, resume 2A with stronger malformed-input/size/decompression checks and multi-record blocks, followed by minimum session/track/flashback fields. Do not mark 2A or 2B complete as part of finishing milestone 2. If tonight ends earlier, name the first unfinished lesson and resume there without reassigning completed work.

## Latest completed lesson and review — historical starting point

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

The October 22 storage priority still governs the sequence. Shared compressed I/O, header functions, raw reading, and explicit record selection are complete, with the October 24 storage evidence recorded above. Playback integration, one-time header handling, and safe append checks come next. Continue pipeline separation, then bring forward the minimum session/track and flashback fields needed for kept history and completed-session archiving; see ROADMAP.md milestones 2A-2B. Individual rev lights remain queued: `m_revLightsBitValue`, uint16 at record +20, with bits 0-14 representing the 15 lights. This is the only remaining undecoded field within the player Car Telemetry record; trailing fields and other car slots remain unimplemented. Keep storage-check evidence, capture observations, exact game comparisons, and telemetry fixture checks distinct.

The receiver still targets `f1_capture.bin` in binary append mode. The isolated round-trip check has passed, but new live recording is deferred pending format identification/compatibility and a clearly separated recording destination. Keep raw and compressed captures out of Git, including renamed copies. The private AGENTS.md remains local and ignored.

## Remaining roadmap

There is one repeatable storage self-check, but no broader automated test suite, desktop UI, full-specification catalog, or structured decoder interface yet. The Car Telemetry inventory is complete, but other packets and the shared header still need cataloguing. The offline decoder stops on errors; future live decoding must report diagnostics without stopping reception. Continue toward complete documented decoding, shared state, a PySide6 Windows UI, and packaging. Preserve the timestamp-length-payload records and default receiver address. Captures remain excluded from Git.

Use the supplied Data Output from F1 25 2026 Season Pack.pdf v1.2 as the source of truth.
