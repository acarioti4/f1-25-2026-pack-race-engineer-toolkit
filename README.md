# F1 25 (2026 Pack) Race Engineer Toolkit

## Overview

F1 25 (2026 Pack) Race Engineer Toolkit is a prototype for receiving live data from **F1 25 using the 2026 Season Pack UDP format** and displaying it in a desktop dashboard that updates as telemetry packets arrive while the game is running.

The current prototype captures UDP packets and decodes player speed, gear, throttle, brake, engine RPM, and steering from Car Telemetry packets in saved captures. The decoder also reads current lap time, position, and lap number from Lap Data packets. Next, refine the lap-time display and refactor decoding into reusable functions before building a live desktop display. The emphasis is on understanding the data and building a dependable foundation before expanding the dashboard.

## How the project fits together

The intended data flow is:

1. **The game sends telemetry.** F1 broadcasts data over UDP when telemetry output is enabled and configured.
2. **A receiver listens for packets.** The Python receiver waits on a local IP address and port.
3. **Packets are captured for inspection.** Raw packets can be saved so the incoming data can be checked and used during development.
4. **A decoder interprets packet contents.** The game sends different packet types for different kinds of information. The packet header identifies the format and packet type; the decoder must use the matching structure from the specification.
5. **The desktop app displays decoded values.** Once the data is structured, the interface can refresh as each new packet arrives and indicate when data is unavailable or has gone stale.

The supplied specification states that packet values use **little-endian encoding** and packed structures. It also documents multiple packet types rather than one packet containing all telemetry. The decoder therefore needs to identify packet types and parse each supported layout correctly.

## Current state

The Python files form an early proof of concept for receiving, recording, and decoding captured telemetry. There is not yet a desktop application. The decoder has code for player speed, gear, throttle, brake, engine RPM, and steering from Car Telemetry packets, plus current lap time, position, and lap number from Lap Data packets. These values still need to be checked against a game capture.

- **`udpreceiver.py`** binds a UDP socket to `127.0.0.1:20888`, prints the packet length, packet format and packet ID, prints each packet as hexadecimal bytes, and appends the packet to `f1_capture.bin` with a timestamp and payload length. It already imports `time` for timestamps.
- **`f1decoder.py`** reads all records from `f1_capture.bin` and reports truncated timestamps, lengths, or payloads. It checks for the 2026 packet format, identifies packet types by ID, and decodes the player's speed, signed gear, throttle percentage, brake percentage, engine RPM, and steering value from Car Telemetry packets (ID 6, packet version 1). It also decodes current lap time in seconds, race position, and lap number from Lap Data packets (ID 2, version 1). The decoded values have not yet been verified against a game capture.
- **The desktop UI is not implemented yet.** The planned interface will use PySide6 and target Windows first.

### Latest development session

The decoder now includes the user’s Lap Data additions: current lap time in seconds, race position, and current lap number. These use packet ID 2, version 1, 57-byte car records, and field offsets +4, +32, and +33 respectively. Current lap time is decoded in milliseconds and divided by 1,000 for seconds. Each field has a bounds check before it is read.

The uploaded code has been reviewed against the supplied specification and passed a Python syntax check. No fixture or game-capture validation has been performed. Current lap time still needs a seconds label and fixed three-decimal display formatting. See [Where We Left Off.md](Where%20We%20Left%20Off.md) for the next learning task.

## Getting started

### 1. Enable UDP telemetry in the game

In the game's UDP telemetry settings:

- Enable UDP telemetry output.
- Set the target IP to `127.0.0.1` when the receiver runs on the same computer.
- Set the target port to **`20888`** to match the current receiver, or change the receiver to match the port configured in the game.
- Select the **`2026`** UDP format to match the supplied *F1 25: 2026 Season Pack* specification.
- Choose a send rate supported by the game settings.

The specification's example configuration shows port `20777`, while this project's receiver currently listens on `20888`. These values must match; the README uses `20888` because that is what the current Python code configures. If the game and receiver are on different computers, the receiver address and network configuration will also need to be adjusted.

### 2. Prepare Python

Use a Python installation and environment for the project. The current receiver and decoder use only Python's built-in modules. No third-party packages are required for the current scripts.

### 3. Run the receiver

Run:

```bash
python udpreceiver.py
```

When the game is configured to send packets, the terminal should print basic information about each incoming datagram. Raw packets are appended to `f1_capture.bin` in the current working directory. Stop capture with `Ctrl+C`.

The receiver currently prints every packet in hexadecimal, which is useful for initial debugging but can produce a large amount of terminal output during a session.

### 4. Inspect a capture

Run:

```bash
python f1decoder.py
```

The decoder processes each complete record in `f1_capture.bin`, prints packet metadata and a readable packet type, and prints player speed, gear, throttle percentage, brake percentage, engine RPM, and steering for Car Telemetry packets. For Lap Data packets, it also prints current lap time in seconds, race position, and lap number. The decoder stops with a clear error if it encounters a truncated record or an unsupported UDP format. These decoded values still need to be checked against a game capture.

## Capture file format

The receiver writes each record to `f1_capture.bin` in this order:

| Field | Size | Meaning |
| --- | ---: | --- |
| Timestamp | 8 bytes | `time.time_ns()` value stored as a little-endian integer |
| Payload length | 4 bytes | Number of bytes in the UDP datagram, stored as a little-endian integer |
| Payload | Variable | Raw UDP datagram received from the game |

The decoder uses the length field to determine how many bytes belong to each packet. It loops until end-of-file and checks for incomplete timestamps, lengths, and payloads.

## What’s next

Build the project in small steps, making sure each layer works before adding more complexity.

1. **Decode a few more useful values**
   - Check the current Car Telemetry values against a game capture.
   - Add a seconds label and fixed three-decimal display for current lap time; the three Lap Data fields are implemented and syntactically checked.
   - Use the specification's field types, units, packed layouts, and vehicle indices rather than guessing from raw bytes.

2. **Create a clean boundary between the receiver and decoder**
   - Keep UDP receiving separate from packet parsing.
   - Convert supported packets into a consistent, structured representation for the UI.
   - Make sure slow parsing or display work does not block packet reception.

3. **Choose and build the desktop app**
   - Use PySide6 for the Windows desktop interface, with packet reception outside the UI thread.
   - Display a small set of values and refresh as new telemetry arrives.
   - Show whether data is connected, stale, or unavailable.
   - Keep receiving packets responsive while the UI updates.
   - Add more information only after the first values update consistently.

4. **Harden and document the prototype**
   - Handle unsupported packet versions and malformed packets clearly.
   - Keep generated capture files out of version control; `.gitignore` already excludes `f1_capture.bin`.

## Longer-term direction

The target is a Windows desktop app using Python and PySide6 that makes every field exposed by specification v1.2 accessible, including all documented cars and packet types 0–16. Track decoding coverage and verification status separately. Respect multiplayer restrictions and mode-specific availability; unavailable data must not appear as genuine zero measurements.

The roadmap includes shared session and car state, connection and freshness status, capture recording and playback through the same decoder, a searchable field browser, selectable dashboard values, and timing, tyre/status, and event views. Package the app with PyInstaller and verify it on Windows without a development Python installation. These are planned capabilities, not implemented features.

## Reference

The project includes **`Data Output from F1 25 2026 Season Pack.pdf`**, version 1.2. Use it when implementing the decoder. It describes the packet header, packet IDs, data structures, data types, and encoding conventions for the 2026 Season Pack. Packet layouts should be checked against the chosen in-game UDP format and the version of the specification being used.

## Milestones

- **Current:** receive and record raw UDP telemetry packets; decode player speed, gear, throttle, brake, RPM, and steering from Car Telemetry packets. Check those values against a game capture.
- **Next:** refine lap-time display, inventory specification coverage, then refactor decoding into functions that return structured telemetry data.
- **After that:** display live values in a desktop app with connection and freshness status.
