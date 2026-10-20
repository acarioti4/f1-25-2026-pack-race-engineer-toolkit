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
- Locating and decoding the player's signed gear value, including reverse (`-1`).
- Starting throttle decoding with `struct.unpack_from` at the documented offset. This is still in progress: `unpack_from` returns a tuple, and the current print label says percent even though the protocol value is in the 0-to-1 range.

## Next coding step

Finish the throttle display before adding another field.

- `throttle_offset` is `speed_offset + 2`; throttle is a 4-byte little-endian float.
- `struct.unpack_from("<f", payload, throttle_offset)` returns a one-item tuple. Store the float inside it to print a scalar.
- Either label the 0-to-1 value as `Throttle` or multiply it by 100 before labeling it `Throttle %`.
- The existing gear length check reaches beyond the throttle bytes, so it also ensures those bytes are present.

After that, review the output, then continue with brake and RPM. Keep using the supplied packet specification to verify each field's offset and representation.

## Remaining roadmap

1. Complete throttle, then decode brake and RPM and handle packet versions and short payloads carefully.
2. Refactor packet parsing into small functions and keep it separate from UDP receiving.
3. Choose a Python desktop UI framework and display live values with connection/freshness status.
4. Run the receiver and dashboard together, then add more telemetry views.

## Reference

Use `Data Output from F1 25 2026 Season Pack.pdf` as the source of truth for packet IDs, field types, byte order, sizes, and offsets. The Car Telemetry packet is described in the specification's Car Telemetry section.
