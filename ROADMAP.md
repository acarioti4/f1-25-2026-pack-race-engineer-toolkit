# Roadmap

The goal is a Windows desktop application built with Python and PySide6 that exposes every field available through **F1 25: 2026 Season Pack UDP specification v1.2**, across all available cars and packet types 0–16.

This is a hobby learning project. Milestones describe the intended development order, with no fixed release dates. See the [README](README.md) for setup instructions and current features.

## Current progress

- [x] Record raw UDP packets with receive timestamps.
- [x] Read saved captures and identify packet types 0–16.
- [x] Decode player speed, signed gear, throttle, brake, RPM, and steering.
- [x] Decode player current lap time, race position, and lap number.
- [x] Exercise the original six telemetry fields and three lap fields through saved game-capture playback.
- [x] Add player engine temperature; specification review and syntax check passed.
- [x] Add brake, tyre surface, and tyre core temperatures for all four player wheels; layout review and syntax check passed.
- [x] Add four-wheel tyre pressures and contact-surface names; reviewed and syntax-checked.
- [x] Add clutch, DRS Closed/Open state, and rev-light percentage; reviewed and syntax-checked.
- [ ] Exercise all additions since the original six telemetry fields through saved-capture playback.
- [ ] Add individual rev-light bits, the remaining field within the player Car Telemetry record.
- [ ] Complete exact comparisons with the game's display.
- [ ] Add automated fixture tests.
- [ ] Build the desktop interface.

Before engine temperature was added, the October 20, 2026 playback processed 71,243 records without error, including 9,695 Car Telemetry and 9,695 Lap Data packets. This establishes successful playback with plausible values, not complete decoder verification, and does not cover the temperature, pressure, contact-surface, clutch, DRS, or rev-light-percentage additions. Reverse is assumed working through signed decoding but was not observed in that capture. Lap progression and full steering travel remain unverified.

The application calls the specification's `m_tyresInnerTemperature` **tyre core temperature**, following the user's preferred racing terminology.

The application deliberately displays `m_drs` as **Closed/Open** (0/1), with **Unknown** for unexpected values. Retain the specification name in protocol references and respect this display preference. Raw DRS and surface IDs remain in variables but are not printed. Support for the 2025 packet format is much later; the current decoder accepts 2026 only.

## 1. Catalogue the specification

- [x] Complete the [Car Telemetry inventory](CAR_TELEMETRY_INVENTORY.md), including every per-car record field and packet trailing field.
- [x] Record Car Telemetry specification names, types, offsets, units, array ordering, and availability rules.
- [x] Track Car Telemetry implementation, specification review, fixture testing, and game verification as separate statuses.
- [ ] Extend the inventory to every packet type, header field, event variant, and lookup table.

**Completion criteria:** Every documented field has an inventory entry, and the existing decoder's coverage and verification gaps are accurately represented.

## 2. Separate the data pipeline

- [ ] Separate UDP reception, capture reading, decoding, and presentation.
- [ ] Use the same decoder for live packets and saved captures.
- [ ] Return structured header and payload results rather than printing within parsing logic.
- [ ] Report malformed and unsupported packets without terminating live reception.
- [ ] Preserve the existing timestamp–length–payload capture format.

**Completion criteria:** Decoding works independently of networking and PySide6, and live reception and playback can feed the same downstream data path.

## 3. Complete documented decoding

- [ ] Expand Car Telemetry and Lap Data to every documented field and available car slot.
- [ ] Add Session and Participants.
- [ ] Add Car Status, Car Damage, Car Setups, and Car Telemetry 2.
- [ ] Add Motion and Motion Ex.
- [ ] Add Events and every documented event payload variant.
- [ ] Add Session History, Tyre Sets, and Lap Positions.
- [ ] Add Final Classification, Lobby Info, and Time Trial.
- [ ] Handle active counts, player and split-screen indices, and multipart lap-position history.
- [ ] Preserve unknown enum values and distinguish withheld or unavailable data from genuine zero measurements.

**Completion criteria:** Every field in the specification is accessible through structured results, with mode-specific availability and multiplayer restrictions respected. Implementation coverage remains separate from verification coverage.

## 4. Maintain shared application state

- [ ] Track session identity, car identity, latest values, events, and supplied historical records independently of widgets.
- [ ] Preserve raw values alongside units and readable labels.
- [ ] Track receive time, freshness, and availability by data group.
- [ ] Handle session changes, flashbacks, missing packets, and stale data.
- [ ] Assemble multipart history without mixing incompatible session data.

**Completion criteria:** Live reception and playback update the same state model, with clear distinctions between current, stale, missing, and restricted data.

## 5. Build the Windows desktop interface

- [ ] Add configurable connection settings, initially using `127.0.0.1:20888`.
- [ ] Add start/stop controls, capture recording, and saved-capture playback.
- [ ] Keep reception outside the UI thread with bounded communication to the interface.
- [ ] Display the currently implemented telemetry and lap fields first.
- [ ] Add a searchable browser covering every catalogued field, with car selection, values, units, and availability.
- [ ] Support selectable dashboard fields.
- [ ] Add timing, tyre/status, and event views using the shared application state.

**Completion criteria:** The interface stays responsive during reception and playback, supports clean shutdown and reconnects, and provides access to every catalogued field.

## 6. Verify and package

Validation should grow alongside each milestone; this final milestone completes coverage and release checks.

- [ ] Add fixtures for layout sizes, signed values, conversions, car indices, event variants, unsupported versions, unknown enums, and malformed captures.
- [ ] Check session resets, flashbacks, stale data, restricted fields, and multipart history.
- [ ] Compare decoded values with the game and record remaining verification gaps.
- [ ] Check interface responsiveness, disconnect/reconnect, playback, and shutdown.
- [ ] Package the application for Windows with PyInstaller.
- [ ] Document installation, game settings, capture/playback, and troubleshooting.
- [ ] Verify the packaged application on Windows without a development Python installation.

**Completion criteria:** Full documented decoding coverage, passing fixture and state checks, recorded game-verification results and gaps, and a working Windows package.

## Scope

Windows and the 2026 packet format are the initial targets. The roadmap can grow as the project develops; cloud services, support for other protocol years, and race-strategy predictions are possible future directions. Raw captures stay excluded from Git.

## Next milestone task

The user plans to collect a longer game capture next. After recording, run the updated decoder, confirm normal completion and the total-record count, and inspect all newly added fields. Record playback observations separately from exact game comparisons. The next coding lesson after capture review is individual rev lights: `m_revLightsBitValue`, uint16 at record +20, with bits 0-14 representing the 15 lights. This is the only remaining undecoded field within the player Car Telemetry record; the three packet trailing fields and other car slots are still unimplemented.

Engine temperature, four-wheel brake/surface/core temperatures, tyre pressures, contact surfaces, clutch, DRS, and rev-light percentage are implemented, specification-reviewed, and syntax-checked. Playback, fixture testing, and exact game comparisons for these additions remain pending.
