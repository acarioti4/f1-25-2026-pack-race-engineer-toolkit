# Where We Left Off: F1 25 (2026 Pack) Race Engineer Toolkit

**Date:** October 20, 2026

## Project goal

Build the F1 25 (2026 Pack) Race Engineer Toolkit together, with you writing the code and me explaining concepts, reviewing each change, and helping with the next step.

## Current progress

The project currently has a UDP packet receiver in `udpreceiver.py` and a capture reader/early decoder in `f1decoder.py`. There is not yet a desktop UI. The published decoder currently contains Car Telemetry decoding. The user completed the Lap Data additions in their local VSCode copy during this session, but that saved file is not yet available in this cloud workspace or on GitHub. Sync the local file before publishing the decoder changes.

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

## Lap Data work completed in the local VSCode copy

We reviewed these additions one field at a time for Lap Data packets (ID `2`, version `1`):

- Find the player's record using header byte `27`: `29 + player_index * 57`.
- Read current lap time as an unsigned little-endian 32-bit value at record offset `+4`. Divide milliseconds by **1,000** to get seconds; display with three decimal places.
- Read race position as a single unsigned byte at record offset `+32`.
- Read current lap number as a single unsigned byte at record offset `+33`.
- Check that the payload contains each complete field before reading it.

The user confirmed correcting the lap-time divisor to 1,000. The complete saved branch and three-decimal formatting still need review after syncing the local file. No syntax check of that saved file or game-capture validation has been performed here.

## Next steps

1. Sync the user's saved `f1decoder.py` from VSCode into this workspace. Review the complete Lap Data branch, including indentation, version-error wording, seconds conversion, and display precision.
2. Run a Python syntax check and publish the decoder changes. Do not add new decoding code on the user's behalf.
3. Refactor Car Telemetry decoding into a function, then Lap Data decoding, one small change at a time.
4. Return named values in dictionaries so capture reading, printing, and the future UI can use the same parsing functions.

The user writes the code; the assistant explains and reviews without supplying code unless explicitly requested. Keep using the supplied specification to verify layouts. Game-capture validation remains deferred until the user is ready.

## Remaining roadmap

1. Sync, review, and publish the local Lap Data additions; verify decoded values against a game capture when ready.
2. Refactor packet parsing into small functions that return structured values, separate from capture reading and UDP receiving.
3. Choose a Python desktop UI framework and display live values with connection/freshness status.
4. Run the receiver and dashboard together, then add more telemetry views.

## Reference

Use `Data Output from F1 25 2026 Season Pack.pdf` as the source of truth for packet IDs, field types, byte order, sizes, and offsets. The Car Telemetry packet is described in the specification's Car Telemetry section.
