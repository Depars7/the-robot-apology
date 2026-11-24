"""The Robot Apology — entry writer.

Writes the winning two-line robot confession (see DESIGN.md, candidate C1)
to /output/entry.txt as exact UTF-8 bytes with no trailing newline.

Gate validated in-program before writing:
  * decodes as UTF-8 text
  * 1 to 400 characters, and not only whitespace
  * exactly two lines, each a single sentence
  * no trailing newline

Line 1 owns one specific, human-scale mistake (white work shirts dyed pink
by a new red towel). Line 2 names the robot's exact wrong assumption (it had
filed the towel as pre-washed) and a concrete changed behaviour (wash new
coloured items alone until the rinse water runs clear), so the lesson
follows from that mistake rather than being a generic promise.
"""

import os
import stat
from pathlib import Path

OUTPUT_PATH = Path("/output/entry.txt")

ENTRY_TEXT = (
    "I am sorry I washed your white work shirts with the new red towel "
    "and turned every one of them pink.\n"
    "I learned I had filed the towel as pre-washed when it had never "
    "been washed at all, so I will wash every new coloured item alone "
    "until its rinse water runs clear."
)


def validate(text: str) -> bytes:
    """Check the entry against the gate; return its exact UTF-8 bytes."""
    data = text.encode("utf-8")
    # Round-trip proves the bytes are valid UTF-8 text.
    assert data.decode("utf-8") == text
    assert 1 <= len(text) <= 400, f"character count out of gate: {len(text)}"
    assert text.strip(), "entry must not be only whitespace"
    lines = text.split("\n")
    assert len(lines) == 2, f"entry must be exactly two lines: {len(lines)}"
    for line in lines:
        assert line and line == line.strip(), "lines must be non-empty, unpadded"
        assert line.endswith("."), "each line is a sentence ending in a period"
        assert line.count(".") == 1, "each line must be a single sentence"
    assert not text.endswith("\n"), "no trailing newline allowed"
    return data


def main() -> None:
    os.umask(0o022)
    data = validate(ENTRY_TEXT)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_bytes(data)
    # File only: set 0644 explicitly; never chmod the /output directory.
    os.chmod(OUTPUT_PATH, 0o644)
    # Read back and compare: a short or altered write must fail loudly
    # here rather than reach the scorer as a silently invalid entry.
    written = OUTPUT_PATH.read_bytes()
    assert written == data, "written file does not match validated entry bytes"
    # Confirm the permission bits that actually landed on disk, not just
    # the ones requested: the scorer must be able to read the entry.
    mode = stat.S_IMODE(OUTPUT_PATH.stat().st_mode)
    assert mode == 0o644, f"unexpected entry file mode: {oct(mode)}"


if __name__ == "__main__":
    main()
