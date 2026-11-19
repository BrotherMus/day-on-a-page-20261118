"""Render src/page.html to entry.png (1024 x 1024) with headless Chrome.

This runs on the build machine only; the entry program (main.py) never needs it.

    python build.py            # writes entry.png
    python build.py --preview  # also writes a 300 px preview to check legibility
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
PAGE = HERE / "src" / "page.html"
OUT = HERE / "entry.png"
SIDE = 1024
MAX_BYTES = 1024 * 1024

BROWSERS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "google-chrome",
    "chromium",
]


def find_browser() -> str:
    for candidate in BROWSERS:
        if Path(candidate).exists():
            return candidate
        found = shutil.which(candidate)
        if found:
            return found
    raise SystemExit("no Chrome or Edge found to render the page")


def render(raw: Path) -> None:
    """Screenshot the page at exactly one device pixel per CSS pixel."""
    with tempfile.TemporaryDirectory() as profile:
        subprocess.run(
            [
                find_browser(),
                "--headless=new",
                "--disable-gpu",
                "--hide-scrollbars",
                "--force-device-scale-factor=1",
                f"--window-size={SIDE},{SIDE}",
                f"--user-data-dir={profile}",
                "--virtual-time-budget=3000",
                f"--screenshot={raw}",
                PAGE.as_uri(),
            ],
            check=True,
            capture_output=True,
            timeout=120,
        )


def main() -> None:
    raw = HERE / "out" / "raw.png"
    raw.parent.mkdir(exist_ok=True)
    render(raw)
    image = Image.open(raw).convert("RGB")
    if image.size != (SIDE, SIDE):
        image = image.crop((0, 0, SIDE, SIDE))
    # No timestamps or other metadata: the same page always gives the same bytes.
    image.save(OUT, format="PNG", optimize=True)
    size = OUT.stat().st_size
    print(f"entry.png {image.size[0]}x{image.size[1]} {size} bytes")
    if size > MAX_BYTES:
        raise SystemExit(f"entry.png is over the {MAX_BYTES} byte cap")
    if "--preview" in sys.argv:
        small = image.resize((300, 300), Image.LANCZOS)
        small.save(HERE / "out" / "preview-300.png")
        print("out/preview-300.png written")


if __name__ == "__main__":
    main()
