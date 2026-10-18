#!/usr/bin/env python3
"""Build the A3 duplex press PDF for roll print + fold into an 8-page newspaper.

Output is **A3 Portrait** (297 × 420 mm) so Canon TM-340 Portrait + A3
matches the page box 1:1 and cuts the roll at 420 mm.

Each sheet is the landscape pair rotated 90° CCW onto the portrait page:
  after printing, turn the sheet so the fold is vertical — left|right reads as below.

Page order (4 × A3 portrait):
  1 — outer face   (from 08|01)  → top 01, bottom 08 when portrait
  2 — outer back   (from 07|02)  → top 02, bottom 07  (order swapped for head-to-head flip)
  3 — inner face   (from 06|03)  → top 03, bottom 06
  4 — inner back   (from 05|04)  → top 04, bottom 05
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from pypdf import PdfReader, PdfWriter, PageObject, Transformation
from PIL import Image

ROOT = Path(__file__).resolve().parent
EXPORT = ROOT / "export"
SOURCE = EXPORT / "polnoch-approval.pdf"
PRESS = EXPORT / "polnoch-press-a3.pdf"
PRESS_PREVIEW = EXPORT / "polnoch-press-preview.jpg"
PRESS_PAGES = EXPORT / "press-pages"

# ISO A3 in PDF points. Portrait = 297 × 420 mm.
A3_SHORT = 841.89
A3_LONG = 1190.55

# Landscape reading order (left, right). Backs are left-right swapped vs the
# classic 02|07 / 04|05 so that a head-to-head Portrait flip puts 02 behind 01.
SHEETS = (
    (8, 1),  # outer face
    (7, 2),  # outer back — swapped for portrait duplex
    (6, 3),  # inner face
    (5, 4),  # inner back — swapped for portrait duplex
)


def _place_half_landscape(sheet: PageObject, src: PageObject, *, left: bool) -> None:
    """Scale one A4 page into the left or right half of an A3 landscape sheet."""
    src_w = float(src.mediabox.width)
    src_h = float(src.mediabox.height)
    half_w = A3_LONG / 2.0
    scale = min(half_w / src_w, A3_SHORT / src_h)
    scaled_w = src_w * scale
    scaled_h = src_h * scale
    tx = (0.0 if left else half_w) + (half_w - scaled_w) / 2.0
    ty = (A3_SHORT - scaled_h) / 2.0
    sheet.merge_transformed_page(
        src,
        Transformation().scale(scale, scale).translate(tx, ty),
    )


def _landscape_pair(reader: PdfReader, left_no: int, right_no: int) -> PageObject:
    landscape = PageObject.create_blank_page(width=A3_LONG, height=A3_SHORT)
    _place_half_landscape(landscape, reader.pages[left_no - 1], left=True)
    _place_half_landscape(landscape, reader.pages[right_no - 1], left=False)
    return landscape


def _to_portrait(landscape: PageObject) -> PageObject:
    """Rotate landscape 90° CCW onto an A3 portrait page (exact mediabox)."""
    portrait = PageObject.create_blank_page(width=A3_SHORT, height=A3_LONG)
    # rotate(90) is CCW around the origin → (x,y)->(-y,x); then +A3_SHORT in x.
    portrait.merge_transformed_page(
        landscape,
        Transformation().rotate(90).translate(A3_SHORT, 0),
    )
    return portrait


def build_press_pdf(source: Path = SOURCE, dest: Path = PRESS) -> Path:
    if not source.exists():
        raise SystemExit(f"missing source PDF: {source}")
    reader = PdfReader(str(source))
    if len(reader.pages) != 8:
        raise SystemExit(f"expected 8 A4 pages, got {len(reader.pages)}")

    writer = PdfWriter()
    for left_no, right_no in SHEETS:
        landscape = _landscape_pair(reader, left_no, right_no)
        writer.add_page(_to_portrait(landscape))

    dest.parent.mkdir(exist_ok=True)
    with dest.open("wb") as handle:
        writer.write(handle)
    return dest


def contact_sheet(pdf: Path = PRESS) -> None:
    pdftoppm = shutil.which("pdftoppm")
    if not pdftoppm:
        raise SystemExit("pdftoppm is not installed")
    if PRESS_PAGES.exists():
        shutil.rmtree(PRESS_PAGES)
    PRESS_PAGES.mkdir()
    subprocess.run(
        [pdftoppm, "-png", "-r", "90", str(pdf), str(PRESS_PAGES / "sheet")],
        check=True,
    )
    images = sorted(PRESS_PAGES.glob("sheet-*.png"))
    if len(images) != 4:
        raise SystemExit(f"expected 4 press sheets, got {len(images)}")
    thumbs = [Image.open(path).convert("RGB") for path in images]
    width, height = thumbs[0].size
    gap = 16
    # Portrait thumbs are taller — lay out 1×4 or 2×2 with room.
    sheet = Image.new(
        "RGB",
        (2 * width + 3 * gap, 2 * height + 3 * gap),
        (232, 230, 224),
    )
    labels = (
        "A face  portrait (01 top / 08 bottom)",
        "A back  portrait (02 top / 07 bottom)",
        "B face  portrait (03 top / 06 bottom)",
        "B back  portrait (04 top / 05 bottom)",
    )
    for index, thumb in enumerate(thumbs):
        col, row = index % 2, index // 2
        sheet.paste(
            thumb,
            (gap + col * (width + gap), gap + row * (height + gap)),
        )
    sheet.save(PRESS_PREVIEW, quality=86, optimize=True)
    print(f"press {pdf} ({pdf.stat().st_size} bytes)")
    print(f"preview {PRESS_PREVIEW} ({PRESS_PREVIEW.stat().st_size} bytes)")
    info = PdfReader(str(pdf)).pages[0]
    print(
        f"page box {float(info.mediabox.width):.2f} x {float(info.mediabox.height):.2f} pt "
        f"(A3 portrait)"
    )
    for index, label in enumerate(labels, start=1):
        print(f"  PDF page {index}: {label}")


if __name__ == "__main__":
    build_press_pdf()
    contact_sheet()
