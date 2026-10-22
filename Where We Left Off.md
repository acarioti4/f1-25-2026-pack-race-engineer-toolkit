# Where We Left Off: F1 25 (2026 Pack) Race Engineer Toolkit

**Date:** October 21, 2026

## Collaboration and learning preferences

The user is not an engineer and is learning through a hobby project. Teach in plain language, explain unfamiliar terms, and give one substantial, coherent practical lesson at a time. The user writes all implementation and test code; the assistant teaches, investigates, and reviews. Follow AGENTS.md. The user asked the assistant to prepare the inventory because that documentation exercise was not interesting to them. Prefer useful coding lessons, with documentation support when requested.

The user authorized updating all documentation, saving and publishing their current changes, and updating the private local AGENTS.md at the end of this session. This does not authorize assistant-written implementation or tests in future sessions. AGENTS.md is intentionally ignored by Git and remains a local instruction file; these learning preferences are also recorded here for the published handoff.

Use **tyre core temperature** alongside **tyre surface temperature** in the application and teaching. Core is the user's deliberate racing terminology choice and maps to the specification's `m_tyresInnerTemperature`; do not suggest changing the display back to inner temperature. Preserve specification names in protocol reference tables.

The application deliberately displays `m_drs` as **Closed/Open** (0/1), with **Unknown** for unexpected values. Retain the specification name in protocol references and respect this display preference. Raw DRS and surface IDs remain in variables but are not printed. Support for the 2025 packet format is much later; the current decoder accepts 2026 only.

The user plans to play and collect a longer capture after this documentation/comment update is published. No new playback or game results have been supplied yet.

## Completed work

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

The user plans to collect a longer game capture next. After recording, run the updated decoder, confirm normal completion and the total-record count, and inspect all newly added fields. Record playback observations separately from exact game comparisons. The next coding lesson after capture review is individual rev lights: `m_revLightsBitValue`, uint16 at record +20, with bits 0-14 representing the 15 lights. This is the only remaining undecoded field within the player Car Telemetry record; the three packet trailing fields and other car slots are still unimplemented.

The receiver appends to `f1_capture.bin`; stop it with Ctrl+C before reviewing the recording. The README records a short capture plan. Keep raw captures out of Git, including any renamed copies. The private AGENTS.md remains local and ignored.

## Remaining roadmap

There is no automated test suite, desktop UI, full-specification catalog, or structured decoder interface yet. The Car Telemetry inventory is complete, but other packets and the shared header still need cataloguing. The offline decoder stops on errors; future live decoding must report diagnostics without stopping reception. Continue toward complete documented decoding, shared state, a PySide6 Windows UI, and packaging. Preserve the capture format and default receiver address. Raw captures remain excluded from Git.

Use the supplied Data Output from F1 25 2026 Season Pack.pdf v1.2 as the source of truth.
