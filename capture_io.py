import zlib
from pathlib import Path
# Eight identifying bytes, written once at the start of a new identified capture.
MARKER = b"F1DVZCAP"
# Our storage layout version, independent of the game's 2026 packet format.
STORAGE_VERSION = 1

def write_file_header(capture):
    # The caller opens the file and calls this once, before writing any records.
    capture.write(MARKER)
    # to_bytes returns encoded bytes; STORAGE_VERSION remains the integer 1.
    version_bytes = STORAGE_VERSION.to_bytes(1, "little")
    capture.write(version_bytes)

def read_file_header(capture):
    # Reading advances the file position; compare the returned bytes with our label.
    header = capture.read(8)
    if header != MARKER:
        raise ValueError("Invalid header.")
    version_bytes = capture.read(1)
    # Check the number of bytes received, not the version number they represent.
    if len(version_bytes) != 1:
        raise ValueError("Invalid format.")
    # Interpret the saved bytes as an integer storage version.
    stored_version = int.from_bytes(version_bytes, "little")
    if stored_version != STORAGE_VERSION:
        raise ValueError("Invalid format.")
    # A successful read leaves the file positioned at the first record's size prefix.
    return stored_version

def read_record(capture):
    compressed_length_bytes = capture.read(4)
    if compressed_length_bytes == b"":
        return None # End of file.
    elif len(compressed_length_bytes) < 4:
        raise ValueError("Truncated compressed length.")
    else:
        # Turn the size bytes into an integer count, then read that many contents bytes.
        compressed_length = int.from_bytes(compressed_length_bytes, "little")
        compressed_record = capture.read(compressed_length)
        # Compare the returned byte count with the requested count.
        if len(compressed_record) != compressed_length:
            raise ValueError("Truncated packet payload")
        else:
            restored_record = zlib.decompress(compressed_record)
            return restored_record

def read_raw_record(capture):
    # The caller supplies an open file positioned at the next raw record.
    # read(8) takes up to eight bytes from that position and advances past them.
    timestamp_bytes = capture.read(8)
    # No timestamp bytes means normal EOF; a partial timestamp is a broken record.
    if len(timestamp_bytes) == 0:
        return None
    elif len(timestamp_bytes) != 8:
        raise ValueError("Incomplete record.")
    # For ABC, this four-byte field contains 03 00 00 00.
    payload_length_bytes = capture.read(4) # The bytes describing the payload length.
    if len(payload_length_bytes) != 4:
        raise ValueError("Incomplete record.")
    # Decode those bytes to the integer 3, keeping the original four bytes intact.
    payload_length = int.from_bytes(payload_length_bytes, "little") # How many payload bytes to read.
    # For ABC, take three bytes from the current position, not from offset 3.
    payload = capture.read(payload_length)
    # A file can end before the requested number of bytes has been read.
    if len(payload) != payload_length:
        raise ValueError("Incomplete record.")
    # Return the same timestamp-length-payload arrangement as the compressed reader.
    raw_record = timestamp_bytes + payload_length_bytes + payload
    return raw_record

def read_capture_record(capture, capture_format):
    # The caller supplies the text label, e.g. read_capture_record(capture, "raw").
    # capture_format holds that text; == compares its value with our chosen labels.
    # This selects a reader; it does not detect the file format automatically.
    if capture_format == "raw":
        # Call the reader, then pass its returned record bytes (or None) to our caller.
        return read_raw_record(capture)
    elif capture_format == "compressed":
        # For identified files, the caller must read the header once before records.
        # Unversioned compressed files start directly with the first record prefix.
        return read_record(capture)
    else:
        raise ValueError("Unknown capture format.")

def write_record(capture, record_bytes):
    smol_record = zlib.compress(record_bytes, 6)
    # Outside compression, four bytes tell the reader the compressed record size.
    smol_length_bytes = len(smol_record).to_bytes(4, "little")
    # Compare complete byte contents, not just their lengths, before writing.
    restored_record = zlib.decompress(smol_record)
    if restored_record != record_bytes:
        raise ValueError("Incorrect packet/invalid decompression")
    else:
        # On disk: compressed-size prefix, then exactly those compressed bytes.
        capture.write(smol_length_bytes)
        capture.write(smol_record)
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
        if read_version != STORAGE_VERSION:
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
