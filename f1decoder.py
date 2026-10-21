# struct reads binary floating-point fields; Path locates the capture beside this script.
import struct
from pathlib import Path

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
      16: "Car Telemetry 2", # Additional telemetry for all cars
}

# Read the receiver's timestamp-length-payload records in binary mode.
with open(Path(__file__).resolve().parent / "f1_capture.bin", "rb") as capture:
    record_counter = 0
    while True:
        # Each record begins with an 8-byte receive timestamp in Unix nanoseconds.
        timestamp_bytes = capture.read(8)

        # No bytes means normal EOF; a partial field means an incomplete capture.
        if timestamp_bytes == b"":
                break # End of file.
        elif len(timestamp_bytes) < 8:
                raise ValueError("Truncated timestamp.")
        else:
            timestamp = int.from_bytes(timestamp_bytes, "little")

            # The next 4 bytes say how many bytes belong to this UDP payload.
            length_bytes = capture.read(4)

            if len(length_bytes) < 4:
                raise ValueError("Truncated packet length!")
            else:
                length = int.from_bytes(length_bytes, "little")

                # Read exactly one datagram before interpreting its game packet layout.
                payload = capture.read(length)

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

                            engine_temp_offset = speed_offset + 38
                            if len(payload) < engine_temp_offset + 1:
                                 raise ValueError("Telemetry packet is missing player's engine.temp data.")
                            engine_temp = payload[engine_temp_offset]

                            # Present the player values together for capture inspection.
                            print(
                                f"Speed: {speed} km/h | "
                                f"Gear: {gear} | "
                                f"Throttle %: {throttle} | "
                                f"Brake %: {brake} | "
                                f"RPM: {rpm} | "
                                f"Steering: {steering} | "
                                f"Engine Temp: {engine_temp}°C | "
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
