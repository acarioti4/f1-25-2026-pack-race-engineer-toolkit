# Where We Left Off: F1 25 (2026 Pack) Race Engineer Toolkit

**Date:** October 20, 2026

## Project goal

Build the F1 25 (2026 Pack) Race Engineer Toolkit together, with you writing the code and me explaining concepts, reviewing each change, and helping with the next step.

## Current progress

The project currently has a UDP packet receiver in `udpreceiver.py` and a capture reader/early decoder in `f1decoder.py`. There is not yet a desktop UI. The latest decoder changes are committed locally on the `main` branch.

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

## Next coding step: begin Lap Data decoding

Add player lap information from Lap Data packets (packet ID `2`). This is a different packet layout from Car Telemetry.

- The packet header is 29 bytes. It contains 24 packed 57-byte Lap Data records, one per car.
- Use the player car index from header byte `27` to find the player's record: start at byte `29`, then skip `player_index * 57` bytes. Do not reuse Car Telemetry's 59-byte record size.
- A useful first value is current lap time: it is a little-endian unsigned 32-bit millisecond value at offset `+4` within the player's record.
- Position is a byte at record offset `+32`; current lap number is a byte at offset `+33`.
- Check that the payload contains the field being read before decoding it. The Lap Data packet version in the supplied specification is `1`.

Add one field at a time and review each change. Keep using the supplied packet specification to verify offsets, types, units, and vehicle indices. Test against a game capture later, as planned.

## Remaining roadmap

1. Add Lap Data current lap time, position, and lap number; later verify decoded values against a game capture.
2. Refactor packet parsing into small functions and keep it separate from UDP receiving.
3. Choose a Python desktop UI framework and display live values with connection/freshness status.
4. Run the receiver and dashboard together, then add more telemetry views.

## Reference

Use `Data Output from F1 25 2026 Season Pack.pdf` as the source of truth for packet IDs, field types, byte order, sizes, and offsets. The Car Telemetry packet is described in the specification's Car Telemetry section.
