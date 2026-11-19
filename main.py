"""The day on a page: Wednesday 18 November 2026.

Entry program for make.fun's "Sum up 18 November's world news in one image".
The front page itself is drawn in src/page.html and rendered once, on the
build machine, by build.py. The grader's sandbox has no network and no
browser, so this program only checks the rendered PNG and hands it over.

Run it locally with:
    MAKEFUN_OUTPUT_DIR=out python main.py
"""

import os
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
IMAGE = HERE / "entry.png"

MAX_BYTES = 1024 * 1024  # the gate takes at most 1 MiB
MAX_SIDE = 1024  # and at most 1024 by 1024 pixels
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def png_size(data: bytes) -> tuple[int, int]:
    """Read width and height from the IHDR chunk, refusing anything that is not a PNG."""
    if data[:8] != PNG_SIGNATURE or data[12:16] != b"IHDR":
        raise ValueError("entry.png is not a PNG file")
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def check(data: bytes) -> None:
    """Fail loudly here rather than hand the gate a file it would refuse."""
    if len(data) > MAX_BYTES:
        raise ValueError(f"entry.png is {len(data)} bytes, over the {MAX_BYTES} byte cap")
    width, height = png_size(data)
    if width > MAX_SIDE or height > MAX_SIDE:
        raise ValueError(f"entry.png is {width}x{height}, over {MAX_SIDE}x{MAX_SIDE}")
    if not data.rstrip(b"\x00").endswith(b"IEND\xaeB`\x82"):
        raise ValueError("entry.png has no IEND chunk: the file is cut short")


def main() -> int:
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    data = IMAGE.read_bytes()
    check(data)
    out_dir.mkdir(parents=True, exist_ok=True)
    # The same bytes on every run: the grader runs this twice and compares.
    (out_dir / "entry.png").write_bytes(data)
    return 0


if __name__ == "__main__":
    sys.exit(main())
