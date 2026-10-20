# F1 25 (2026 Pack) Race Engineer Toolkit

## Overview

F1 25 (2026 Pack) Race Engineer Toolkit is a prototype for receiving live data from **F1 25 using the 2026 Season Pack UDP format** and displaying it in a desktop dashboard that updates as telemetry packets arrive while the game is running.

The first goal is deliberately simple: receive the game's telemetry reliably, identify and decode the packets, and make a small set of useful values available to a live desktop display. The emphasis at the start is on understanding the data and building a dependable foundation—not on creating a fully featured racing dashboard immediately. The desktop UI framework has not been selected yet.

## How the project fits together

The intended data flow is:

1. **The game sends telemetry.** F1 broadcasts data over UDP when telemetry output is enabled and configured.
2. **A receiver listens for packets.** The Python receiver waits on a local IP address and port.
3. **Packets are captured for inspection.** Raw packets can be saved so the incoming data can be checked and used during development.
4. **A decoder interprets packet contents.** The game sends different packet types for different kinds of information. The packet header identifies the format and packet type; the decoder must use the matching structure from the specification.
5. **The desktop app displays decoded values.** Once the data is structured, the interface can refresh as each new packet arrives and indicate when data is unavailable or has gone stale.

The supplied specification states that packet values use **little-endian encoding** and packed structures. It also documents multiple packet types rather than one packet containing all telemetry. The decoder therefore needs to identify packet types and parse each supported layout correctly.

## Current state

The current Python files are an early proof of concept for receiving and inspecting telemetry. There is not yet a desktop application or a decoder for the game's telemetry fields.

- **`udpreceiver.py`** binds a UDP socket to `127.0.0.1:20888`, prints the packet length, packet format and packet ID, prints each packet as hexadecimal bytes, and appends the packet to `f1_capture.bin` with a timestamp and payload length. It already imports `time` for timestamps.
- **`f1decoder.py`** reads one record from `f1_capture.bin`, checks for incomplete timestamp, length, or payload data, and prints record metadata. It does **not** yet decode telemetry fields such as speed, lap time, or gear. Its `struct` import is currently unused.
- **The desktop UI is not implemented yet.** No desktop framework has been selected.

The decoder currently reads only one record each time it runs, rather than iterating through the complete capture.

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

Use a Python installation and environment for the project. The current receiver uses only Python's built-in `socket` and `time` modules. The `struct` import in the decoder is unused so far. No third-party packages are required for the current scripts.

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

The current decoder reads one record from `f1_capture.bin` and prints its timestamp and payload length. This verifies the capture-record framing; it is **not yet a decoder for the game's telemetry fields**. It does not yet continue through the rest of the capture file.

## Capture file format

The receiver writes each record to `f1_capture.bin` in this order:

| Field | Size | Meaning |
| --- | ---: | --- |
| Timestamp | 8 bytes | `time.time_ns()` value stored as a little-endian integer |
| Payload length | 4 bytes | Number of bytes in the UDP datagram, stored as a little-endian integer |
| Payload | Variable | Raw UDP datagram received from the game |

The decoder uses the length field to determine how many bytes belong to each packet. It should eventually loop over records until end-of-file and retain its current checks for incomplete records.

## What’s next

Build the project in small steps, making sure each layer works before adding more complexity.

1. **Make packet capture reliable**
   - Remove unused imports unless they become necessary.
   - Keep normal console output readable and report socket or file errors clearly.

2. **Process complete capture files**
   - Change `f1decoder.py` to read every record in `f1_capture.bin`.
   - Preserve the checks for truncated timestamps, lengths, and payloads.
   - Test empty files and incomplete records.

3. **Parse and validate the F1 packet header**
   - Use the supplied *Data Output from F1 25: 2026 Season Pack* specification as the source of truth for packet layouts.
   - Read the header fields, including packet format, packet version, packet ID, session information, frame identifiers, and player car index as appropriate.
   - Confirm the selected UDP format and packet versions before parsing packet bodies.

4. **Decode a small, useful set of values**
   - Start with a few fields that make a live display meaningful—for example, speed, gear, RPM, throttle, brake, lap number, lap time, and position.
   - Add session information where needed to give those values context.
   - Use the specification's field types, units, packed layouts, and vehicle indices rather than guessing from raw bytes.

5. **Create a clean boundary between the receiver and decoder**
   - Keep UDP receiving separate from packet parsing.
   - Convert supported packets into a consistent, structured representation for the UI.
   - Make sure slow parsing or display work does not block packet reception.

6. **Choose and build the desktop app**
   - Select a desktop UI framework that fits the project and can work with the Python telemetry layer.
   - Display a small set of values and refresh as new telemetry arrives.
   - Show whether data is connected, stale, or unavailable.
   - Keep receiving packets responsive while the UI updates.
   - Add more information only after the first values update consistently.

## Longer-term direction

The end goal is a desktop telemetry dashboard that makes the game's UDP data easy to read while driving or reviewing a session. It should update when new packets arrive and make the current connection and data freshness clear. Once the basic receiver, decoder, and UI are dependable, the project could grow to include more race and car information, tyre and damage data, event notifications, timing views, and richer visualizations.

These are possible future additions, not features implemented by the current scripts.

## Reference

The project includes **`Data Output from F1 25 2026 Season Pack.pdf`**, version 1.2. Use it when implementing the decoder. It describes the packet header, packet IDs, data structures, data types, and encoding conventions for the 2026 Season Pack. Packet layouts should be checked against the chosen in-game UDP format and the version of the specification being used.

## Milestones

- **Current:** receive and record raw UDP telemetry packets.
- **Next:** parse captured packets into validated, structured telemetry data.
- **After that:** display a small set of decoded values in a desktop app that updates as packets arrive.
