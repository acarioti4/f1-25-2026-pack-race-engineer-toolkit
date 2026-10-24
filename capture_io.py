import zlib
from pathlib import Path
# Eight identifying bytes, written once at the start of a new identified capture.
MARKER = b"F1DVZCAP"
# Our storage layout version, independent of the game's 2026 packet format.
version = 1

def write_file_header(capture):
    # The caller opens the file and calls this once, before writing any records.
    capture.write(MARKER)
    # to_bytes returns encoded bytes; version itself remains the integer 1.
    byte_version = version.to_bytes(1, "little")
    capture.write(byte_version)

def read_file_header(capture):
    # Reading advances the file position; compare the returned bytes with our label.
    header = capture.read(8)
    if header != MARKER:
        raise ValueError("Invalid header.")
    format = capture.read(1)
    # Check the number of bytes received, not the version number they represent.
    if len(format) != 1:
        raise ValueError("Invalid format.")
    # Despite its name, byte_version now holds an integer decoded from those bytes.
    byte_version = int.from_bytes(format, "little")
    if byte_version != version:
        raise ValueError("Invalid format.")
    # A successful read leaves the file positioned at the first record's size prefix.
    return byte_version

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
        # This check exercises the reusable header writer once for the whole file.
        write_file_header(roundtrip)
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
        # Validate and consume the header before asking read_record for record bytes.
        read_version = read_file_header(capture)
        if read_version != version:
            raise ValueError("Invalid version.")

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

def check_missing_version():
    # Replace only our generated test file with an intentionally incomplete header.
    capture_path = Path(__file__).resolve().parent / "compression_roundtrip.bin"
    with open(capture_path, "wb") as capture:
        capture.write(MARKER)

    with open(capture_path, "rb") as capture:
        try:
            read_file_header(capture)
        except ValueError:
            # Rejection is the expected successful outcome for this invalid input.
            print("Missing version correctly rejected!")
        else:
            # else runs only if the reader did not raise an error.
            raise AssertionError("A header without a version was accepted.")


if __name__== "__main__":
    # Imports expose the functions without running checks or replacing test data.
    check_round_trip()
    # This runs last, so the generated file is left containing only the marker.
    check_missing_version()
