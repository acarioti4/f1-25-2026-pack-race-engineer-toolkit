import socket
import time

UDP_IP = "127.0.0.1"
UDP_PORT = 20888
BUFFER_SIZE = 65535

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
print(f"Listening for F1 UDP telemetry on port {UDP_PORT}")
with open("f1_capture.bin", "ab") as capture:
    try:
        while True:
            data, addr = sock.recvfrom(BUFFER_SIZE)

            # F1 packet header: packet format is first 2 bytes
            # packet ID is byte 6
            if len(data) >= 7:
                packet_format = int.from_bytes(data[0:2], "little")
                packet_id = data[6]
            else:
                packet_format = None
                packet_id = None

            print(
                f"Length={len(data)} | "
                f"Format={packet_format} | "
                f"Packet ID={packet_id} | "
                f"From={addr}"
            )
            print(data.hex(" "))

            # Save timestamp, packet length, and packet bytes.
            capture.write(time.time_ns().to_bytes(8, "little"))
            capture.write(len(data).to_bytes(4, "little"))
            capture.write(data)
            capture.flush()

    except KeyboardInterrupt:
        print("\nCapture stopped.")
    finally:
        sock.close()