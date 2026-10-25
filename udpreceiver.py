# socket receives UDP datagrams; time supplies receive timestamps; Path locates the file.
# capture_io handles headers and compressed records; os names file-position options.
import socket
import time
from pathlib import Path
from capture_io import write_record, write_file_header, read_file_header
import os

# These must match the game's telemetry destination. This address is local to this PC.
UDP_IP = "127.0.0.1"
UDP_PORT = 20888
# Allow room for a full UDP datagram rather than truncating it in recvfrom.
BUFFER_SIZE = 65535
# Keep new identified recordings separate from the historical playback filename.
CAPTURE_PATH = Path(__file__).resolve().parent / "live_capture.bin"
# This recording destination is ignored by Git.
# Create an IPv4 UDP socket and reserve the configured local address and port.
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
# Flush startup messages immediately so the listening address and file are visible.
print(f"Listening for F1 UDP telemetry on {UDP_IP}:{UDP_PORT}", flush=True)
print(f"Saving capture to: {CAPTURE_PATH}", flush=True)
# a preserves contents and appends writes; b uses bytes; + also permits header reads.
# A missing file is created; an existing file is never cleared by this mode.
with open(CAPTURE_PATH, "a+b") as capture:
    try:
        # SEEK_END chooses the end; 0 means zero bytes away from that point.
        capture.seek(0, os.SEEK_END)
        # tell() reports position, which equals file size after moving to the end.
        file_size = capture.tell()
        # Only a new/empty file needs the nine-byte marker/version header.
        if file_size == 0:
            write_file_header(capture)
        else:
            # SEEK_SET measures from the beginning; inspect before writing anything.
            capture.seek(0, os.SEEK_SET)
            # Invalid headers raise ValueError, skipping the loop and running finally.
            # A valid header does not prove that all existing records are undamaged.
            read_file_header(capture)
        # Both successful branches join here; prepare to continue at the file end.
        capture.seek(0, os.SEEK_END)
        while True:
            # Wait for one datagram. data is its raw payload; addr identifies the sender.
            data, addr = sock.recvfrom(BUFFER_SIZE)

            # Store receive time (8 bytes), payload length (4 bytes), then payload.
            # The two integers are little-endian; the game bytes are saved unchanged.
            timestamp = time.time_ns().to_bytes(8, "little")
            length = len(data).to_bytes(4, "little")
            # Joining bytes creates one record; the inner length still describes data only.
            full_packet = timestamp + length + data
            write_record(capture, full_packet)
           

    # Ctrl+C stops capture; leaving the with block closes the capture file.
    except KeyboardInterrupt:
        print("\nCapture stopped.")
    # Release the socket on normal interruption or an error inside the try block.
    finally:
        sock.close()
