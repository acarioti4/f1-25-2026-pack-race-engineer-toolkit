import struct

packet_names = {
      0: "Motion",
      1: "Session",
      2: "Lap Data",
      3: "Event",
      4: "Participants", # For Multiplayer lobbies.
      5: "Car Setups",
      6: "Car Telemetry",
      7: "Car Status",
      8: "Final Classification",
      9: "Lobby Info", # Multiplayer
      10: "Car Damage",
      11: "Session History", # Lap and tyre data for session
      12: "Tyre Sets", # Extended tyre set data
      13: "Extended Motion", # For player car only
      14: "Time Trial", # Time trial specific data (leaderboards probably?)
      15: "Lap Positions", # Lap positions on each lap so a chart can be constructed
      16: "Car Telemetry 2", # Additional telemetry for all cars
}

with open("f1_capture.bin", "rb") as capture:
    record_counter = 0
    while True:
        timestamp_bytes = capture.read(8)

        if timestamp_bytes == b"":
                break # End of file.
        elif len(timestamp_bytes) < 8:
                raise ValueError("Truncated timestamp.")
        else:
            timestamp = int.from_bytes(timestamp_bytes, "little")

            length_bytes = capture.read(4)

            if len(length_bytes) < 4:
                raise ValueError("Truncated packet length!")
            else:
                length = int.from_bytes(length_bytes, "little")

                payload = capture.read(length)

                if len(payload) != length:
                        raise ValueError("Truncated packet payload!")
                else:
                        if len(payload) < 29:
                                raise ValueError("Packet is shorter than the header!")

                        packet_format = int.from_bytes(payload[0:2], "little")
                        if packet_format != 2026:
                            raise ValueError("Incorrect packet format.")
                        packet_id = payload[6]
                        packet_name = packet_names.get(packet_id, "Unknown")
                        if packet_id == 6:
                            if payload[5] != 1:
                                raise ValueError("Incorrect packet version.")

                            player_index = payload[27]
                            speed_offset = 29 + player_index * 59
                            if len(payload) < speed_offset + 2:
                                raise ValueError("Telemetry packet is missing the player's speed data.")
                            speed = int.from_bytes(payload[speed_offset:speed_offset + 2], "little")

                            gear_offset = speed_offset + 15
                            if len(payload) < gear_offset + 1:
                                raise ValueError("Telemetry packet is missing player's gear data.")
                            gear = int.from_bytes(payload[gear_offset:gear_offset + 1], "little", signed=True)

                            throttle_offset = speed_offset + 2
                            throttle = struct.unpack_from("<f", payload, throttle_offset)[0]
                            throttle = throttle * 100

                            brake_offset = speed_offset + 10
                            if len(payload) < brake_offset + 4:
                                raise ValueError("Telemetry packet is missing player's brake data.")
                            brake = struct.unpack_from("<f", payload, brake_offset)[0]
                            brake = brake * 100

                            rpm_offset = speed_offset + 16
                            if len(payload) < rpm_offset + 2:
                                raise ValueError("Telemetry packet is missing player's RPM data.")
                            rpm = int.from_bytes(payload[rpm_offset:rpm_offset + 2], "little")

                            steering_offset = speed_offset + 6
                            if len(payload) < steering_offset + 4:
                                raise ValueError("Telemetry packet is missing player's steering data.")
                            steering = struct.unpack_from("<f", payload, steering_offset)[0]

                            print(
                                f"Speed: {speed} km/h | "
                                f"Gear: {gear} | "
                                f"Throttle %: {throttle} | "
                                f"Brake %: {brake} | "
                                f"RPM: {rpm} | "
                                f"Steering: {steering} | "
                            )

                        record_counter += 1
                        print(f"Timestamp: {timestamp}")
                        print(f"Packet length: {length}")
                        print(f"Payload bytes received: {len(payload)}")
                        print(f"Packet format: {packet_format}")
                        print(f"Packet ID: {packet_id}")
                        print(f"Packet type: {packet_name}")

    print(f"Total complete records: {record_counter}")
