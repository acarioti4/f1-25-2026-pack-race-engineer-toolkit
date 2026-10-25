# struct reads binary floating-point fields; Path locates the capture beside this script.
# zlib restores each compressed record before its original fields are selected.
import struct
from pathlib import Path
from capture_io import read_capture_record, read_file_header

# Packet IDs identify layouts, not individual cars. Only IDs 2 and 6 are decoded below.
packet_names = {
      0: "Motion",
      1: "Session",
      2: "Lap Data",
      3: "Event",
      4: "Participants", # Driver and participant information.
      5: "Car Setups",
      6: "Car Telemetry",
      7: "Car Status",
      8: "Final Classification",
      9: "Lobby Info", # Multiplayer
      10: "Car Damage",
      11: "Session History", # Lap and tyre data for session
      12: "Tyre Sets", # Extended tyre set data
      13: "Extended Motion", # For player car only
      14: "Time Trial", # Time trial comparison data.
      15: "Lap Positions", # Lap positions on each lap so a chart can be constructed
      16: "Car Telemetry 2" # Additional telemetry for all cars
}

# Future Session lookup; currently unused. Unknown track -1 needs handling when connected.
track_id = {
     0: "Melbourne",
     2: "Shanghai",
     3: "Sakhir (Bahrain)",
     4: "Catalunya",
     5: "Monaco",
     6: "Montreal",
     7: "Silverstone",
     9: "Hungaroring",
     10: "Spa",
     11: "Monza",
     12: "Singapore",
     13: "Suzuka",
     14: "Abu Dhabi",
     15: "Texas",
     16: "Brazil",
     17: "Austria",
     19: "Mexico",
     20: "Baku (Azerbaijan)",
     26: "Zandvoort",
     27: "Imola",
     29: "Jeddah",
     30: "Miami",
     31: "Las Vegas",
     32: "Losail",
     39: "Silverstone (Reverse)",
     40: "Austria (Reverse)",
     41: "Zandvoort (Reverse)",
     42: "Madrid"
}

# Partial lookup for modern 2026 F1 teams; currently unused by decoding.
team_id = { # 2026 Teams
     476: "Mercedes", 
     477: "Ferrari",
     478: "Red Bull",
     479: "Williams",
     480: "Aston Martin",
     481: "Alpine",
     482: "Racing Bulls",
     483: "Haas",
     484: "McLaren",
     485: "Audi",
     486: "Cadillac"
}

# Selected driver IDs, not the full specification table; currently unused.
driver_id = {
     0: "Carlos Sainz",
     2: "Daniel Ricciardo",
     3: "Fernando Alonso",
     4: "Felipe Massa",
     7: "Lewis Hamilton",
     9: "Max Verstappen",
     10: "Nico Hülkenberg",
     11: "Kevin Magnussen",
     14: "Sergio Pérez",
     15: "Valtteri Bottas",
     17: "Esteban Ocon",
     19: "Lance Stroll",
     50: "George Russell",
     54: "Lando Norris",
     58: "Charles Leclerc",
     59: "Pierre Gasly",
     62: "Alex Albon",
     77: "Ayrton Senna",
     80: "Guanyu Zhou",
     90: "Michael Schumacher",
     94: "Yuki Tsunoda",
     109: "Jenson Button",
     112: "Oscar Piastri",
     113: "Liam Lawson",
     147: "Oliver Bearman",
     149: "Isack Hadjar",
     161: "Gabriel Bortoleto",
     162: "Franco Colapinto",
     165: "Andrea-Kimi Antonelli",
     188: "Arvid Lindblad"
}

# Future Session lookup; defining names does not yet decode Session packets.
session_type = {
     0: "Unknown",
     1: "Practice 1",
     2: "Practice 2",
     3: "Practice 3",
     4: "Short Practice",
     5: "Qualifying 1",
     6: "Qualifying 2",
     7: "Qualifying 3",
     8: "Short Qualifying",
     9: "One-Shot Qualifying",
     10: "Sprint Shootout 1",
     11: "Sprint Shootout 2",
     12: "Sprint Shootout 3",
     13: "Short Sprint Shootout",
     14: "One-Shot Sprint Shootout",
     15: "Race",
     16: "Race 2",
     17: "Race 3",
     18: "Time Trial"
}

# Surface IDs describe contact at each wheel; the raw IDs are retained below.
surface_names = {
     0: "Tarmac",
     1: "Rumble strip",
     2: "Concrete",
     3: "Rock",
     4: "Gravel",
     5: "Mud",
     6: "Sand",
     7: "Grass",
     8: "Water",
     9: "Cobblestone",
     10: "Metal",
     11: "Ridged"
}

# Display preference: Closed/Open labels for the specification field m_drs.
wing_position = {
     0: "Closed",
     1: "Open"
}

# Future Event lookup; currently unused by decoding.
penalty_type = {
     0: "Drive through",
     1: "Stop & Go",
     2: "Grid penalty",
     3: "Penalty reminder",
     4: "Time penalty",
     5: "Warning",
     6: "Disqualified",
     7: "Removed from formation lap",
     8: "Parked too long timer",
     9: "Tyre regulations",
     10: "This lap invalidated",
     11: "This and next lap invalidated",
     12: "This lap invalidated without reason",
     13: "This and next lap invalidated without reason",
     14: "This and previous lap invalidated",
     15: "This and previous lap invalidated without reason",
     16: "Retired",
     17: "Black flag timer"
}

# Future Event lookup. Braces in these ordinary strings remain literal characters.
infringement_type = {
     0: "Blocking by slow driving",
     1: "Blocking by wrong way driving",
     2: "Reversing off the start line",
     3: "Big Collision",
     4: "Small Collision",
     5: "Collision: failed to hand back single position",
     6: "Collision: failed to hand back multiple positions",
     7: "Corner cutting: gained time",
     8: "Corner cutting: single overtake",
     9: "Corner cutting: multiple overtakes",
     10: "Crossed pit exit lane",
     11: "Ignoring blue flags",
     12: "Ignoring yellow flags",
     13: "Ignoring drive through",
     14: "Too many drive throughs",
     15: "Drive through reminder, serve within {n} laps",
     16: "Drive through reminder, server this lap",
     17: "Pit lane speeding",
     18: "Parked for too long",
     19: "Ignoring tyre regulations",
     20: "Too many penalties",
     21: "Multiple warnings",
     22: "Approaching disqualification",
     23: "Tyre regulations select single",
     24: "Tyre regulations select multiple",
     25: "Lap invalidated: Corner cutting",
     26: "Lap invalidated: Running wide",
     27: "Curner cutting: Ran wide, gained minor time",
     28: "Corner cutting: Ran wide, gained significant time",
     29: "Corner cutting: Ran wide, gained extreme time",
     30: "Lap invalidated: Wall riding",
     31: "Lap invalidated: Flashback used",
     32: "Lap invalidated: Reset to track",
     33: "Blocking pit lane",
     34: "Jump start",
     35: "{Safety Car} Collision",
     36: "{Safety Car} Illegal overtake",
     37: "{Safety Car} Exceeding allowed pace",
     38: "{Virtual Safety Car} Exceeding allowed pace",
     39: "Formation lap below allowed speed",
     40: "Formation lap parking",
     41: "Retired: Mechanical failure",
     42: "Retired: Terminal damage",
     43: "{Safety Car} Falling too far back",
     44: "Black flag timer",
     45: "Unserved: Stop & Go penalty",
     46: "Unserved: Drive through penalty",
     47: "Engine component change",
     48: "Gearbox change",
     49: "Parc Fermé change",
     50: "{League} Grid penalty",
     51: "Retry penalty",
     52: "Illegal time gain",
     53: "Mandatory pitstop",
     54: "Attribute assigned"
}

input_format = "unversioned_compressed"
# Choose raw, unversioned_compressed, or identified_compressed to match the file.
# This is an explicit choice; ZIP archives are not supported here.
# capture stays an open file object; its read calls advance the position on disk.
with open(Path(__file__).resolve().parent / "f1_capture.bin", "rb") as capture:
    record_counter = 0
    if input_format == "raw":
        capture_format = "raw"
    elif input_format == "unversioned_compressed":
        capture_format = "compressed"
    elif input_format == "identified_compressed":
        # Consume the file header once, leaving the first record ready for the loop.
        read_file_header(capture)
        capture_format = "compressed"
    else: raise ValueError("Unknown format.")

    while True:
        restored_record = read_capture_record(capture, capture_format)
        if restored_record is None:
             break # End of file.
        else:
            timestamp_bytes = restored_record[0:8]
            if timestamp_bytes == b"":
                raise ValueError("Incomplete record.")
            elif len(timestamp_bytes) < 8:
                raise ValueError("Truncated timestamp.")
            else:
                timestamp = int.from_bytes(timestamp_bytes, "little")

            # Positions 8-11 encode the original UDP payload size, not compressed size.
            length_bytes = restored_record[8:12]

            if len(length_bytes) < 4:
                raise ValueError("Truncated packet length!")
            else:
                length = int.from_bytes(length_bytes, "little")

                # Select all bytes from position 12 to the end of this restored record.
                # This does not read from disk or include any later capture records.
                payload = restored_record[12:]

                # Reject either too few or too many payload bytes for the recorded size.
                if len(payload) != length:
                        raise ValueError("Truncated packet payload!")
                else:
                        # All supported game packets begin with a 29-byte packed header.
                        if len(payload) < 29:
                                raise ValueError("Packet is shorter than the header!")

                        # Offsets are zero-based. Multibyte game values are little-endian.
                        packet_format = int.from_bytes(payload[0:2], "little")
                        if packet_format != 2026:
                            raise ValueError("Incorrect packet format.")
                        # Header byte 6 selects the packet type; unknown IDs still get metadata.
                        packet_id = payload[6]
                        packet_name = packet_names.get(packet_id, "Unknown")
                        if packet_id == 6:
                            # Header byte 5 is this packet type's layout version.
                            if payload[5] != 1:
                                raise ValueError("Incorrect packet version.")

                            # Header byte 27 selects the player's slot in the 24-car array.
                            player_index = payload[27]
                            if player_index > 23:
                                 raise ValueError("Incorrect Player Index data.")
                            # Skip the header and earlier 59-byte CarTelemetryData records.
                            # Speed starts at record offset +0 and is an unsigned 16-bit km/h value.
                            speed_offset = 29 + player_index * 59
                            if len(payload) < speed_offset + 2:
                                raise ValueError("Telemetry packet is missing the player's speed data.")
                            speed = int.from_bytes(payload[speed_offset:speed_offset + 2], "little")

                            # Gear at +15 is signed: -1 = reverse, 0 = neutral, 1-8 = forward.
                            gear_offset = speed_offset + 15
                            if len(payload) < gear_offset + 1:
                                raise ValueError("Telemetry packet is missing player's gear data.")
                            gear = int.from_bytes(payload[gear_offset:gear_offset + 1], "little", signed=True)

                            # Throttle at +2 is a 4-byte float; the gear bounds check above
                            # already ensures these earlier bytes exist. '<f' means little-endian
                            # float; [0] extracts the value from unpack_from's one-item tuple.
                            throttle_offset = speed_offset + 2
                            throttle = struct.unpack_from("<f", payload, throttle_offset)[0]
                            # Convert the normalized 0-1 input to a percentage for printing.
                            throttle = throttle * 100

                            # Brake at +10 uses the same normalized float representation.
                            brake_offset = speed_offset + 10
                            if len(payload) < brake_offset + 4:
                                raise ValueError("Telemetry packet is missing player's brake data.")
                            brake = struct.unpack_from("<f", payload, brake_offset)[0]
                            brake = brake * 100

                            # Clutch is one unsigned byte at +14, already a percentage (0-100).
                            clutch_offset = speed_offset + 14
                            if len(payload) < clutch_offset + 1:
                                 raise ValueError("Telemetry packet is missing player's clutch data.")
                            clutch = payload[clutch_offset]

                            # m_drs at +18 is one state value, so it needs one dictionary lookup.
                            # Keep the raw number in drs and label unrecognized values Unknown.
                            drs_offset = speed_offset + 18
                            if len(payload) < drs_offset + 1:
                                 raise ValueError("Telemetry packet is missing player's wing data.")
                            drs = payload[drs_offset]
                            drs_state = wing_position.get(drs, "Unknown")

                            # +19 is the supplied rev-light percentage, not a value calculated from RPM.
                            rev_light_offset = speed_offset + 19
                            if len(payload) < rev_light_offset + 1:
                                 raise ValueError("Telemetry packet is missing player's rev light %.")
                            rev_light = payload[rev_light_offset]


                            # Engine RPM at +16 is an unsigned 16-bit integer.
                            rpm_offset = speed_offset + 16
                            if len(payload) < rpm_offset + 2:
                                raise ValueError("Telemetry packet is missing player's RPM data.")
                            rpm = int.from_bytes(payload[rpm_offset:rpm_offset + 2], "little")

                            # Steering at +6 is a float: -1 = full left, +1 = full right.
                            steering_offset = speed_offset + 6
                            if len(payload) < steering_offset + 4:
                                raise ValueError("Telemetry packet is missing player's steering data.")
                            steering = struct.unpack_from("<f", payload, steering_offset)[0]

                            # In this specification engine temperature is one byte at +38, in Celsius.
                            engine_temp_offset = speed_offset + 38
                            if len(payload) < engine_temp_offset + 1:
                                raise ValueError("Telemetry packet is missing player's engine temp data.")
                            engine_temp = payload[engine_temp_offset]
                            
                            # Four 2-byte brake temperatures occupy eight bytes at +22.
                            brake_temp_offset = speed_offset + 22
                            if len(payload) < brake_temp_offset + 8:
                                raise ValueError("Telemetry packet is missing player's brake temp data.")
                            brake_temps = struct.unpack_from("<4H", payload, brake_temp_offset) # Order is LR, RR, LF, RF.
                            
                            # Surface and core temperatures each contain four 1-byte Celsius values.
                            surface_temp_offset = speed_offset + 30
                            if len(payload) < surface_temp_offset + 4:
                                raise ValueError ("Telemetry packet is missing player's tyre surface temp data.")
                            t_surface_temps = struct.unpack_from("<4B", payload, surface_temp_offset) # Order is LR, RR, LF, RF.
                            
                            # Core is our display name for the specification field m_tyresInnerTemperature.
                            core_temp_offset = speed_offset + 34
                            if len(payload) < core_temp_offset + 4:
                                raise ValueError("Telemetry packet is missing player's core tyre temp data.")
                            t_core_temps = struct.unpack_from("<4B", payload, core_temp_offset) # Order is LR, RR, LF, RF.

                            # Four 4-byte floats at +39 occupy 16 bytes; pressures arrive in PSI.
                            t_pressure_offset = speed_offset + 39
                            if len(payload) < t_pressure_offset + 16:
                                raise ValueError("Telemetry packet is missing player's tyre pressure data.")
                            tyre_pressures = struct.unpack_from("<4f", payload, t_pressure_offset) # Order is LR, RR, LF, RF.

                            # Four surface IDs at +55 follow the same LR, RR, LF, RF wheel order.
                            contact_surface_offset = speed_offset + 55
                            if len(payload) < contact_surface_offset + 4:
                                 raise ValueError("Telemetry packet is missing player's tyre contact surface data.")
                            t_contact_surface = struct.unpack_from("<4B", payload, contact_surface_offset)
                            # Unlike the single DRS state, each of the four IDs needs its own lookup.
                            surface_name = [surface_names.get(surface_id, "Unknown") for surface_id in t_contact_surface]


                            # Present the player values together for capture inspection.
                            print(
                                f"Speed: {speed} km/h | "
                                f"Gear: {gear} | "
                                f"Throttle %: {throttle}% | "
                                f"Brake %: {brake}% | "
                                f"Clutch %: {clutch}% | "
                                f"RPM: {rpm} | "
                                f"Rev Light %: {rev_light}% | "
                                f"Steering: {steering} | "
                                f"DRS: {drs_state} | "
                                f"Engine Temp: {engine_temp}°C | "
                                f"Brake Temps: LR - {brake_temps[0]}°C | RR - {brake_temps[1]}°C | LF - {brake_temps[2]}°C | RF - {brake_temps[3]}°C | "
                                f"Tyre Surface Temp: LR - {t_surface_temps[0]}°C | RR - {t_surface_temps[1]}°C | LF - {t_surface_temps[2]}°C | RF - {t_surface_temps[3]}°C | "
                                f"Tyre Core Temp: LR - {t_core_temps[0]}°C | RR - {t_core_temps[1]}°C | LF - {t_core_temps[2]}°C | RF - {t_core_temps[3]}°C | "
                                f"Tyre Pressure: LR - {tyre_pressures[0]}PSI | RR - {tyre_pressures[1]}PSI | LF - {tyre_pressures[2]}PSI | RF - {tyre_pressures[3]}PSI | "
                                f"Tyre's Contact Surface: LR - {surface_name[0]} | RR - {surface_name[1]} | LF - {surface_name[2]} | RF - {surface_name[3]} | "
                            )
                            
                        elif packet_id == 2:
                             # Lap Data has its own version and 57-byte per-car layout.
                             if payload[5] != 1:
                                  raise ValueError("Incorrect Lap Data packet version.")
                             player_index = payload[27]
                             if player_index > 23:
                                 raise ValueError("Incorrect Player Index data.")
                             # Locate the player's LapData record after the shared header.
                             lap_offset = 29 + player_index * 57
                             # Current lap time is an unsigned 32-bit millisecond value at +4.
                             cur_lap_time_offset = lap_offset + 4
                             if len(payload) < cur_lap_time_offset + 4:
                                  raise ValueError("Telemetry packet is missing Current Lap Time data.")
                             cur_lap_timeMS = int.from_bytes(payload[cur_lap_time_offset:cur_lap_time_offset + 4], "little")
                             # Divide by 1000 to display seconds, retaining the raw milliseconds.
                             cur_lap_timeS = cur_lap_timeMS / 1000
                             print(f"Current Lap Time: {cur_lap_timeS}")

                             # Position at +32 and lap number at +33 each occupy one byte.
                             race_position_offset = lap_offset + 32
                             if len(payload) < race_position_offset + 1:
                                  raise ValueError("Telemetry packet is missing Position data.")
                             race_position = payload[race_position_offset]
                             print(f"Current Position: P{race_position}")

                             lap_number_offset = lap_offset + 33
                             if len(payload) < lap_number_offset + 1:
                                  raise ValueError("Telemetry packet is missing Lap data.")
                             lap_number = payload[lap_number_offset]
                             print(f"Lap: {lap_number}")


                        # Count each complete record and print metadata for every packet type,
                        # including types whose payload fields are not decoded yet.
                        record_counter += 1
                        print(f"Timestamp: {timestamp}")
                        print(f"Packet length: {length}")
                        print(f"Payload bytes received: {len(payload)}")
                        print(f"Packet format: {packet_format}")
                        print(f"Packet ID: {packet_id}")
                        print(f"Packet type: {packet_name}")

    # Reached only after normal EOF; malformed or unsupported input raises above.
    print(f"Total complete records: {record_counter}")
