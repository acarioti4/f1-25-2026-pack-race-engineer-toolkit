# Where We Left Off: F1 25 (2026 Pack) Race Engineer Toolkit

**Date:** October 20, 2026

## Collaboration rules

The user writes implementation and test code. The assistant teaches, investigates, and reviews one manageable task at a time. Follow AGENTS.md and the supplied specification. In this session the user explicitly authorized explanatory comments in both Python files, documentation updates, and committing/pushing all project changes. Only comments were added to Python during this documentation work; behavior was preserved.

## Completed work

- The receiver records on 127.0.0.1:20888 using the existing timestamp-length-payload format, appending to f1_capture.bin beside the script. It prints startup details, not individual packets.
- The decoder checks capture framing and the 2026 format, labels packet IDs, and prints metadata. Packet IDs 6 and 2 require version 1 and a player index from 0 to 23.
- Car Telemetry decoding covers player speed, signed gear, throttle percentage, brake percentage, RPM, and steering. Player record start: 29 + index * 59.
- Lap Data decoding covers current lap time (unsigned 32-bit milliseconds at record +4, displayed as seconds), position (byte +32), and lap number (byte +33). Player record start: 29 + index * 57.
- Added comments explaining capture framing, offsets, types, conversions, bounds checks, output, and socket/file lifecycle. Syntax-tree comparison confirms these comments preserve executable behavior.
- Published the capture review, comments, documentation, and pending local project changes in commit `6fa735a`. Incorporated the existing remote history with merge commit `d5675db` and pushed it to `origin/main` successfully. The raw capture was excluded.
- Synchronized AGENTS.md and the other Markdown files: Lap Data is implemented, capture playback is complete, reverse is assumed working, and the next task is the coverage inventory. The standing user-written implementation/test rule remains in effect; requested source comments are a limited exception.

## Game-capture check

The existing decoder processed **71,243 complete records** without error, including **9,695 Car Telemetry** and **9,695 Lap Data** packets. No fixture suite was written or run.

- Speed: 0-318 km/h; neutral and forward gears 1-8 observed.
- Throttle/brake: each 0-100%; 617 samples had both positive.
- One overlap sample: 0 km/h, neutral, 30.25% throttle, 98.46% brake, 10,584 RPM.
- 5,796 samples showed a complete stop in neutral.
- RPM: 3,920-13,204; steering: approximately -1.00 to +0.73.
- Lap time: 0-32.35 seconds; positions P10/P11/P12/P15/P16/P17; lap 1 throughout.

These are plausible observations from a game capture, not exact comparisons with on-screen instruments. Reverse is assumed working at the user's request; signed decoding supports -1, but the capture contains no reverse samples. Do not make another reverse capture the next task. A burnout cannot be confirmed from the six decoded fields alone. Lap offsets match the specification, but lap values, progression, and full steering travel still have game-verification gaps.

## Unresolved work

There is no automated test suite, desktop UI, complete coverage catalog, or structured decoder interface. Capture success does not verify malformed input, unsupported versions, other car indices, restricted data, or every field. The offline decoder stops on errors; future live decoding must report diagnostics without stopping reception. Raw captures remain ignored by Git.

## One next task: Car Telemetry coverage inventory

Create a documentation table for every field in the Car Telemetry record and its packet trailing fields. Record the specification name, type, record/packet offset, unit, availability, and separate statuses for implementation, specification review, fixture testing, and game verification. Mark the six implemented fields and preserve the verification gaps above. Completion means every field in this packet is accounted for against the supplied PDF. No new decoder code is needed for this task.

## Roadmap and reference

Continue the inventory across packet types 0-16, then separate capture reading, decoding, and presentation; expand all documented data; build shared session/car state; add the PySide6 Windows UI; package with PyInstaller. Preserve the capture format and default address. Use Data Output from F1 25 2026 Season Pack.pdf, version 1.2, as the source of truth. README contains current usage and validation details.
