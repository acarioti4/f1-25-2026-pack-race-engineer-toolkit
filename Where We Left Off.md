# Where We Left Off: F1 25 (2026 Pack) Race Engineer Toolkit

**Date:** October 20, 2026

## Project goal

Build the F1 25 (2026 Pack) Race Engineer Toolkit together, with you writing the code and me explaining concepts, reviewing each change, and helping with the next step.

## Current progress

The project currently has a UDP packet receiver in `udpreceiver.py` and a capture reader/early decoder in `f1decoder.py`. There is not yet a desktop UI. The decoder contains Car Telemetry decoding and the user’s uploaded Lap Data additions. The uploaded file has been reviewed and passed a Python syntax check. No fixture or game-capture validation has been performed.

In `f1decoder.py`, we have worked through:

- Reading every capture record until end of file.
- Detecting incomplete timestamps, packet lengths, and payloads.
- Counting complete records.
- Checking that the payload contains the 29-byte packet header.
- Reading the packet format and confirming it is `2026`.
- Reading the packet ID and mapping IDs to readable names.
- For Car Telemetry packets (ID `6`), checking packet version `1`.
- Reading the player's car index from header byte `27`.
- Locating and decoding the player's speed in km/h, with a length check first.
- Locating and decoding the player's signed gear value, including reverse (`-1`).
- Decoding throttle and brake floats and converting their normalized 0-to-1 values to percentages. `struct.unpack_from` returns a tuple, so the first item is used as the float value.
- Decoding engine RPM as an unsigned little-endian 16-bit integer.
- Decoding steering as a float from -1.0 (left) to +1.0 (right), with a length check for the bytes at the steering offset.
- The Car Telemetry decoding has had a Python syntax check, but has not yet been checked against a live game capture; testing is intentionally deferred.

## Lap Data work completed

We reviewed these additions one field at a time for Lap Data packets (ID `2`, version `1`):

- Find the player's record using header byte `27`: `29 + player_index * 57`.
- Read current lap time as an unsigned little-endian 32-bit value at record offset `+4`. Divide milliseconds by **1,000** to get seconds; display with three decimal places.
- Read race position as a single unsigned byte at record offset `+32`.
- Read current lap number as a single unsigned byte at record offset `+33`.
- Check that the payload contains each complete field before reading it.

The uploaded branch uses the correct divisor of 1,000 and the documented offsets, field types, version check, and field bounds checks. It passed a Python syntax check. Its lap-time output does not yet include a seconds label or fixed three-decimal formatting. The missing-field messages could identify Lap Data more precisely. Values remain unverified against fixtures or a game capture.

## Next steps

1. The next user coding task is to label current lap time in seconds and display it with three decimal places. Review that small change before continuing.
2. Establish a coverage inventory for specification v1.2, tracking implementation, review, syntax checks, fixture checks, and game verification separately.
3. Refactor Car Telemetry decoding into a function, then Lap Data decoding, one small change at a time. Return structured values separately from capture reading and presentation.

The user writes the code; the assistant explains and reviews without supplying code unless explicitly requested. Keep using the supplied specification to verify layouts. Game-capture validation remains deferred until the user is ready.

## Remaining roadmap

1. Validate the existing telemetry and lap fields against a game capture before relying on them in the UI; capture validation remains deferred until the user is ready.
2. Separate receiving, capture reading, decoding, and presentation while preserving the timestamp–length–payload capture format.
3. Expand decoding to every field and car slot documented in specification v1.2, covering packet IDs 0–16 and availability restrictions.
4. Build shared application state with session identity, freshness, availability, and history handling.
5. Build a Windows desktop interface using **PySide6**, including live capture, playback, a searchable field browser, and selectable dashboard values.
6. Package for Windows using PyInstaller and record fixture checks and remaining game-verification gaps.

Private collaboration instructions are kept in the local, ignored `AGENTS.md`; do not commit that file.

## Reference

Use `Data Output from F1 25 2026 Season Pack.pdf` as the source of truth for packet IDs, field types, byte order, sizes, and offsets. The Car Telemetry packet is described in the specification's Car Telemetry section.
