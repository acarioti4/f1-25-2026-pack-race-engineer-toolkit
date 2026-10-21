# socket receives UDP datagrams; time supplies receive timestamps; Path locates the file.
import socket
import time
from pathlib import Path

# These must match the game's telemetry destination. This address is local to this PC.
UDP_IP = "127.0.0.1"
UDP_PORT = 20888
# Allow room for a full UDP datagram rather than truncating it in recvfrom.
BUFFER_SIZE = 65535
CAPTURE_PATH = Path(__file__).resolve().parent / "f1_capture.bin"

# Create an IPv4 UDP socket and reserve the configured local address and port.
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
# Flush startup messages immediately so the listening address and file are visible.
print(f"Listening for F1 UDP telemetry on {UDP_IP}:{UDP_PORT}", flush=True)
print(f"Saving capture to: {CAPTURE_PATH}", flush=True)
# Append in binary mode: starting the receiver again keeps earlier recordings.
with open(CAPTURE_PATH, "ab") as capture:
    try:
        while True:
            # Wait for one datagram. data is its raw payload; addr identifies the sender.
            data, addr = sock.recvfrom(BUFFER_SIZE)

            # Store receive time (8 bytes), payload length (4 bytes), then payload.
            # The two integers are little-endian; the game bytes are saved unchanged.
            capture.write(time.time_ns().to_bytes(8, "little"))
            capture.write(len(data).to_bytes(4, "little"))
            capture.write(data)
            # Flush Python's buffer after each packet so it is available to readers.
            capture.flush()

    # Ctrl+C stops capture; leaving the with block closes the capture file.
    except KeyboardInterrupt:
        print("\nCapture stopped.")
    # Release the socket on normal interruption or an error inside the try block.
    finally:
        sock.close()
