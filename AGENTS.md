# Learning Roadmap to a Complete Telemetry Desktop App

## Goal and current state

Build a Windows desktop application using Python and PySide6 that makes every field in the supplied **F1 25: 2026 Season Pack UDP specification v1.2** accessible for display, including all available cars and packet types 0–16.

The project records UDP packets and decodes player speed, gear, throttle, brake, RPM, steering, current lap time, position, and lap number from saved captures. An October 20, 2026 capture playback processed 71,243 records without error and produced plausible values. Reverse is assumed working at the user's request, without a reverse capture sample. Exact in-game comparisons and fixture checks remain incomplete; see README.md and Where We Left Off.md. No desktop interface or automated test suite exists yet.

“All data” means data the game exposes through this specification. Respect multiplayer restrictions and mode-specific availability; do not present withheld values as genuine zero measurements.

## Standing learning and collaboration rules

- **The user writes all implementation and test code.** The assistant teaches, helps plan, investigates, and reviews.
- Do not provide implementation code, copyable solutions, patches, or direct source edits. Conceptual, language-neutral pseudocode is allowed.
- Documentation edits are allowed when requested; this does not authorize implementation changes.
- Give one manageable coding task at a time. Explain its purpose, relevant concepts, specification references, and completion criteria.
- Let the user attempt the task before offering progressively more detailed hints.
- Review user-written code with concrete observations and explanations. Describe corrections without writing replacements.
- Use the supplied PDF as the source of truth for layouts, versions, types, offsets, units, array ordering, and availability.
- Distinguish implemented, reviewed, syntactically checked, fixture-tested, and game-verified work. Never describe an untested decoder as verified.
- Finish each learning session with completed work, unresolved issues, and one next task. Update handoff documentation when requested.
- These rules continue across sessions unless the user explicitly changes them.

## Implementation roadmap

1. **Establish a coverage inventory and extend the current decoder.**
   Inventory every documented packet, header field, payload field, event variant, and lookup table. Track decoding and verification status separately. Continue with player current lap time, position, and lap number, one field at a time. Validate the existing six telemetry values using a capture before relying on them in the UI.

2. **Separate receiving, capture reading, decoding, and presentation.**
   Refactor the user’s code into independently understandable components. Live packets and saved captures must use the same decoder. Preserve the existing timestamp–length–payload capture format. Return structured results rather than printing inside parsing logic; report malformed or unsupported packets without terminating live reception.

3. **Complete documented data access.**
   Expand Car Telemetry and Lap Data to every documented field and car slot. Then add Session and Participants; Car Status, Damage, Setups, and Telemetry 2; Motion and Motion Ex; Events; Session History, Tyre Sets, and Lap Positions; and Final Classification, Lobby Info, and Time Trial. Handle active counts, event-specific payloads, split-screen indices, and multipart lap-position history according to the specification.

4. **Build shared application state.**
   Maintain session identity, car identity, latest values, event history, and supplied historical records independently of widgets. Preserve raw values alongside units and readable labels. Track receive time and availability by data group. Handle session changes, flashbacks, missing packets, and stale data without mixing incompatible state.

5. **Build the Windows desktop interface.**
   Use PySide6 with packet reception outside the UI thread and bounded communication to the interface. Add connection settings, start/stop controls, capture recording, and saved-capture playback. First show the existing telemetry and lap fields. Then add a searchable browser covering every documented field, with car selection, values, units, and availability. Let users select fields for a dashboard; add timing, tyre/status, and event views using the same state.

6. **Package and verify the application.**
   Package with PyInstaller for Windows. Document game settings, launching, capture/playback, and troubleshooting. Verify operation on a Windows machine without a development Python installation.

## Interfaces and acceptance checks

- The decoder accepts packet bytes and produces structured header/payload data or a diagnostic; it does not depend on networking or PySide6.
- A field catalog connects specification names, packet identity, units, labels, and availability to the data browser.
- Live reception and playback feed the same state and display path.
- The user writes tests for layout sizes, signed values, conversions, car indices, event variants, malformed captures, unsupported versions, and unknown enum values.
- State checks cover session resets, flashbacks, stale data, restricted fields, and multipart history.
- Desktop checks cover responsiveness, disconnect/reconnect, playback, shutdown, and access to every catalogued field.
- Completion requires full documented decoding coverage, fixture checks, and clearly recorded game verification gaps.

## Defaults and first learning task

Retain `127.0.0.1:20888` as the initial configurable receiver address. Target Windows first; cloud services, other protocol years, and derived race-strategy predictions are outside this roadmap.

The initial Lap Data fields are implemented. The next learning task is a Car Telemetry coverage inventory: document every record field and packet trailing field with type, offset, unit, availability, and separate implementation, review, fixture-test, and game-verification statuses. The assistant supplies guidance and reviews the user’s work without giving implementation or test code.
