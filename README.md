# F1 25 (2026 Pack) Race Engineer Toolkit

A learning project exploring F1 telemetry with Python. The goal is a Windows desktop app built with PySide6 for viewing the data exposed by **F1 25: 2026 Season Pack UDP specification v1.2**.

The current prototype records UDP packets and decodes selected player telemetry and lap data from saved captures. A desktop interface is planned but is not implemented yet.

## Features

- Record raw game UDP packets with receive timestamps.
- Read saved captures and display packet metadata and selected player values.
- Decode speed, gear, throttle, brake, RPM, steering, and engine temperature from Car Telemetry packets, plus brake, tyre surface, and tyre core temperatures for all four player wheels.
- Decode current lap time, race position, and lap number from Lap Data packets.
- Identify packet types 0–16; payload decoding currently covers selected fields in packet types 2 and 6.
- Check capture boundaries, packet headers, the 2026 format, and supported versions and player indices for the implemented packet types.

## Getting started

### Requirements

- Python 3
- F1 25 with the 2026 Season Pack for recording live telemetry

The current scripts use only the Python standard library. PySide6 is planned for the desktop interface and is not required to run the prototype.

### Configure the game

Enable UDP telemetry, select the 2026 format, and set the destination to:

| Setting | Value |
| --- | --- |
| IP address | `127.0.0.1` |
| Port | `20888` |

These defaults assume the game and receiver run on the same PC. The game's destination must match `UDP_IP` and `UDP_PORT` in `udpreceiver.py`. This project uses port `20888`, which differs from the specification's example port `20777`.

### Record telemetry

From the project directory, run:

```bash
python udpreceiver.py
```

The receiver prints its listening address and capture path, then records packets to `f1_capture.bin` beside the scripts. Stop recording with **Ctrl+C**.

Each recording appends to the same file. To start a separate capture, move or rename the existing file before restarting the receiver. Raw captures are excluded from Git.

### Decode a capture

After recording, run:

```bash
python f1decoder.py
```

The decoder reads `f1_capture.bin` beside the scripts, prints packet metadata and supported values, and reports the total record count. File paths are resolved relative to the scripts, regardless of the terminal's working directory.

## Decoded fields

Only the player car's selected fields are currently decoded.

| Packet | Field | Displayed unit or range |
| --- | --- | --- |
| Car Telemetry (6) | Speed | km/h |
| Car Telemetry (6) | Gear | Signed value; 0 = neutral, 1–8 = forward gears, -1 = reverse |
| Car Telemetry (6) | Throttle | % |
| Car Telemetry (6) | Brake | % |
| Car Telemetry (6) | Engine speed | RPM |
| Car Telemetry (6) | Steering | -1 = left, +1 = right |
| Car Telemetry (6) | Engine temperature | Degrees Celsius |
| Car Telemetry (6) | Brake temperatures | Degrees Celsius, all four wheels |
| Car Telemetry (6) | Tyre surface temperatures | Degrees Celsius, all four wheels |
| Car Telemetry (6) | Tyre core temperatures | Degrees Celsius, all four wheels |
| Lap Data (2) | Current lap time | Seconds, converted from milliseconds |
| Lap Data (2) | Race position | Position number |
| Lap Data (2) | Current lap number | Lap number |

Wheel temperatures are displayed in left rear (LR), right rear (RR), left front (LF), right front (RF) order. The application uses **core temperature** to match the user's preferred racing terminology; this maps to `m_tyresInnerTemperature` in the UDP specification.

## Validation and limitations

Before engine temperature was added, an October 20, 2026 capture playback processed **71,243 records** without error, including **9,695 Car Telemetry** and **9,695 Lap Data** packets. Observed values included speeds of 0–318 km/h, neutral and forward gears 1–8, a stop in neutral, and simultaneous throttle and brake input.

These results demonstrate successful playback with plausible values; exact comparisons with the game's display remain incomplete. Reverse uses signed gear decoding and is assumed working, but was not observed in that capture. Lap progression and full steering travel also remain unverified.

Engine temperature and the four-wheel brake, tyre surface, and tyre core temperatures are implemented for the player car. Layout review against the specification and Python syntax checking passed. Playback of these additions, fixture testing, and comparison with the game remain pending; the earlier capture results do not cover them.

There is no automated test suite yet. Synthetic fixtures, malformed-input tests, other car indices, and restricted-data handling still need coverage. Malformed captures, unsupported formats, and unsupported versions of the implemented packet types currently stop the offline decoder with an error.

## Capture format

Each capture record contains:

| Field | Size | Encoding |
| --- | --- | --- |
| Receive timestamp | 8 bytes | Unix nanoseconds, little-endian integer |
| Payload length | 4 bytes | Unsigned little-endian byte count |
| Payload | Variable | Original game UDP bytes |

The reader distinguishes normal end-of-file from truncated timestamps, lengths, and payloads. Captures can contain multiple recording periods because recording appends to the existing file.

## Roadmap

See [ROADMAP.md](ROADMAP.md) for milestones, progress, and completion criteria.

- The [Car Telemetry inventory](CAR_TELEMETRY_INVENTORY.md) is complete. Extend the inventory to other packets and track implementation and validation coverage separately.
- Separate packet receiving, capture reading, decoding, and presentation into shared components.
- Expand decoding to all documented fields and available car slots across packet types 0–16.
- Respect multiplayer restrictions and mode-specific availability, keeping withheld data distinct from measured zero values.
- Maintain shared session and car state, including data freshness, events, and historical records.
- Build a PySide6 interface with live telemetry, capture playback, a searchable field browser, and selectable dashboards.
- Add automated fixture and state checks, complete game comparisons, and package for Windows with PyInstaller.

The initial focus is Windows and the 2026 packet format. Future directions may include support for other protocol years, cloud services, and race-strategy predictions as the project develops.

## License

Licensed under the [MIT License](LICENSE).
