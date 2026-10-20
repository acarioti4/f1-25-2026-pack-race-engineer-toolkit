# Where We Left Off: F1 25 (2026 Pack) Race Engineer Toolkit

**Date:** October 19, 2026

## Project goal

Build the F1 25 (2026 Pack) Race Engineer Toolkit together, with you writing the code and me explaining concepts, reviewing each change, and helping with the next step.

## Current progress

The project currently has a UDP packet receiver in `udpreceiver.py` and a capture reader/early decoder in `f1decoder.py`. There is not yet a desktop UI.

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

## Next coding step

Decode the player's gear from the same Car Telemetry car record.

- `speed_offset` is the start of the player's 59-byte telemetry record.
- Gear is 15 bytes into that record, so its byte offset is `speed_offset + 15`.
- Gear is a signed 8-bit value. Use `int.from_bytes` with `signed=True` so reverse can be `-1`.
- Print the decoded gear beside the speed.

After you make the change, ask me to check it. We can then decode throttle, brake, and RPM, and make the decoder easier to read before connecting it to a live dashboard.

## Remaining roadmap

1. Decode a few useful car values and handle packet versions and short payloads carefully.
2. Refactor packet parsing into small functions and keep it separate from UDP receiving.
3. Choose a Python desktop UI framework and display live values with connection/freshness status.
4. Run the receiver and dashboard together, then add more telemetry views.

## Reference

Use `Data Output from F1 25 2026 Season Pack.pdf` as the source of truth for packet IDs, field types, byte order, sizes, and offsets. The Car Telemetry packet is described in the specification's Car Telemetry section.
