import zlib
from pathlib import Path

def read_record(capture):
    compressed_length_bytes = capture.read(4)
    if compressed_length_bytes == b"":
        return None # End of file.
    elif len(compressed_length_bytes) < 4:
        raise ValueError("Truncated compressed length.")
    else:
        # Turn the size bytes into an integer count, then read that many contents bytes.
        compressed_length = int.from_bytes(compressed_length_bytes, "little")
        comp_read = capture.read(compressed_length)
        # Compare the returned byte count with the requested count.
        if len(comp_read) != compressed_length:
            raise ValueError("Truncated packet payload")
        else:
            restored_record = zlib.decompress(comp_read)
            return restored_record

def write_record(capture, full_packet):
    smol_packet = zlib.compress(full_packet, 6)
    # Outside compression, four bytes tell the reader the compressed record size.
    smol_length = len(smol_packet).to_bytes(4, "little")
    # Compare complete byte contents, not just their lengths, before writing.
    packet_check = zlib.decompress(smol_packet)
    if packet_check != full_packet:
        raise ValueError("Incorrect packet/invalid decompression")
    else:
        # On disk: compressed-size prefix, then exactly those compressed bytes.
        capture.write(smol_length)
        capture.write(smol_packet)
        # Empty Python's file buffer; this is not a guarantee against power loss.
        capture.flush()

def check_round_trip():
    with open(Path(__file__).resolve().parent / "compression_roundtrip.bin", "wb") as roundtrip:
        timestamp = 1000
        timestamp = timestamp.to_bytes(8, "little")
        payload = b"ABC"
        payload_length = len(payload).to_bytes(4, "little")
        first_packet = timestamp + payload_length + payload
        write_record(roundtrip, first_packet)

        timestamp = 2000
        timestamp = timestamp.to_bytes(8, "little")
        payload = b"DEFGH"
        payload_length = len(payload).to_bytes(4, "little")
        second_packet = timestamp + payload_length + payload
        write_record(roundtrip, second_packet)

    CAPTURE_PATH = Path(__file__).resolve().parent / "compression_roundtrip.bin"
    with open(CAPTURE_PATH, "rb") as capture:
        first_record = read_record(capture)
        if first_packet != first_record:
            raise ValueError("Incorrect first record.")

        second_record = read_record(capture)
        if second_packet != second_record:
            raise ValueError("Incorrect second record.")

        result = read_record(capture)
        if result is not None:
            raise ValueError("Unexpected record.")
        else:
            print("Success!")

if __name__== "__main__":
    check_round_trip()