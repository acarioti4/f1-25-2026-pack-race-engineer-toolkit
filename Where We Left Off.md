# Where We Left Off: F1 25 (2026 Pack) Race Engineer Toolkit

**Date:** October 20, 2026

## Collaboration and learning preferences

The user is not an engineer and is learning through a hobby project. Teach in plain language, explain unfamiliar terms, and give one substantial, coherent practical lesson at a time. The user writes all implementation and test code; the assistant teaches, investigates, and reviews. Follow AGENTS.md. The user asked the assistant to prepare the inventory because that documentation exercise was not interesting to them. Prefer useful coding lessons, with documentation support when requested.

The user authorized updating documentation and publishing the current changes at the end of this session. This does not authorize assistant-written implementation or tests in future sessions. AGENTS.md is intentionally ignored by Git and remains a local instruction file; these learning preferences are also recorded here for the published handoff.

## Completed work

- Receiver records on 127.0.0.1:20888, appending timestamp-length-payload records to f1_capture.bin beside the scripts.
- Decoder checks capture framing and the 2026 format. Packet IDs 6 and 2 require version 1 and a player index from 0 to 23.
- Car Telemetry now reads seven player fields: speed, signed gear, throttle, brake, RPM, steering, and engine temperature. Player record starts at 29 + index * 59.
- The user added engine temperature in packet 6 at record offset +38, checks that the byte exists, reads it as an unsigned byte, and prints degrees Celsius. Review against the specification and Python syntax check passed. The user also corrected the print comment to avoid the outdated six-field count.
- Lap Data reads current lap time (uint32 milliseconds at record +4, displayed in seconds), position (+32), and lap number (+33). Player record starts at 29 + index * 57.
- CAR_TELEMETRY_INVENTORY.md covers all 16 record fields and three trailing fields, including offsets, sizes, units, availability, wheel order, surface lookup, and separate implementation/review/fixture/game statuses. Packet size totals 1448 bytes.
- README, roadmap, inventory, local instructions, and this handoff now distinguish the new engine-temperature work from earlier capture evidence.
- Earlier source-comment additions were checked by syntax-tree comparison to preserve behavior. That historical check does not apply to the new user-written engine-temperature behavior.

## Verification evidence and gaps

Before engine temperature was added, capture playback processed **71,243 records** without error, including **9,695 Car Telemetry** and **9,695 Lap Data** packets. No fixture suite exists or was run.

- Speed: 0-318 km/h; neutral and forward gears 1-8 observed.
- Throttle/brake: each 0-100%; 617 samples had both positive. One sample had 0 km/h, neutral, 30.25% throttle, 98.46% brake, and 10,584 RPM.
- 5,796 samples showed a stop in neutral.
- RPM: 3,920-13,204; steering approximately -1.00 to +0.73.
- Lap time: 0-32.35 seconds; positions P10/P11/P12/P15/P16/P17; lap 1 throughout.
- Engine temperature: implemented, reviewed, and syntax-checked only. Updated-decoder playback, controlled fixture testing, and comparison with the game remain pending. No temperature observations have been reported.

Capture observations are plausible values, not exact comparisons with the game. Reverse is assumed working at the user's request; signed decoding supports it but the capture contained no reverse samples. Do not require another reverse capture next. A burnout was not confirmed. Full steering travel, lap progression, other car slots, malformed input, and restricted-data handling still need verification.

## One next task

Run the updated decoder on the existing capture. Confirm it reaches the total-record count without error and inspect a few engine-temperature values. Review those observations before adding another reading. Keep playback evidence separate from exact game verification.

## Remaining roadmap

There is no automated test suite, desktop UI, full-specification catalog, or structured decoder interface yet. The Car Telemetry inventory is complete, but other packets and the shared header still need cataloguing. The offline decoder stops on errors; future live decoding must report diagnostics without stopping reception. Continue toward complete documented decoding, shared state, a PySide6 Windows UI, and packaging. Preserve the capture format and default receiver address. Raw captures remain excluded from Git.

Use the supplied Data Output from F1 25 2026 Season Pack.pdf v1.2 as the source of truth.
