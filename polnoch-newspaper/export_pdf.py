#!/usr/bin/env python3
"""Export the screen-approval PDF and a contact sheet. No press imposition."""

import shutil
import subprocess
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent
HTML = ROOT / "index.html"
EXPORT = ROOT / "export"
PDF = EXPORT / "polnoch-approval.pdf"
PREVIEW = EXPORT / "polnoch-preview.jpg"
PAGES = EXPORT / "pages"


def export_pdf() -> None:
    EXPORT.mkdir(exist_ok=True)
    chrome = shutil.which("google-chrome") or shutil.which("google-chrome-stable")
    if not chrome:
        raise SystemExit("google-chrome is not installed")
    profile = Path("/tmp/polnoch-chrome-profile")
    if profile.exists():
        shutil.rmtree(profile)
    cmd = [
        chrome,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--no-pdf-header-footer",
        "--hide-scrollbars",
        "--no-first-run",
        "--disable-background-networking",
        "--disable-sync",
        "--disable-extensions",
        f"--user-data-dir={profile}",
        f"--print-to-pdf={PDF}",
        HTML.as_uri(),
    ]
    subprocess.run(cmd, check=True, timeout=90)
    if not PDF.exists() or PDF.stat().st_size < 1000:
        raise SystemExit("PDF export failed")


def contact_sheet() -> None:
    pdftoppm = shutil.which("pdftoppm")
    if not pdftoppm:
        raise SystemExit("pdftoppm is not installed")
    if PAGES.exists():
        shutil.rmtree(PAGES)
    PAGES.mkdir()
    subprocess.run(
        [pdftoppm, "-png", "-r", "110", str(PDF), str(PAGES / "page")],
        check=True,
    )
    images = sorted(PAGES.glob("page-*.png"))
    if len(images) != 8:
        raise SystemExit(f"expected 8 pages, got {len(images)}")
    thumbs = [Image.open(path).convert("RGB") for path in images]
    width, height = thumbs[0].size
    gap = 18
    cols, rows = 2, 4
    sheet = Image.new(
        "RGB",
        (cols * width + (cols + 1) * gap, rows * height + (rows + 1) * gap),
        (12, 14, 22),
    )
    for index, thumb in enumerate(thumbs):
        col, row = index % cols, index // cols
        sheet.paste(thumb, (gap + col * (width + gap), gap + row * (height + gap)))
    sheet.save(PREVIEW, quality=86, optimize=True)
    print(f"pdf {PDF} ({PDF.stat().st_size} bytes)")
    print(f"preview {PREVIEW} ({PREVIEW.stat().st_size} bytes)")
    print(f"pages {len(images)} size {width}x{height}")


if __name__ == "__main__":
    export_pdf()
    contact_sheet()
