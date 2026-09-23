#!/usr/bin/env python3
"""Build the A3 duplex press PDF for roll print + fold into an 8-page newspaper.

Page order in the output (4 × A3 landscape):
  1 — outer sheet, face   → 08 | 01
  2 — outer sheet, back   → 02 | 07
  3 — inner sheet, face   → 06 | 03
  4 — inner sheet, back   → 04 | 05
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

# ISO A3 landscape in PDF points (1 pt = 1/72 in).
A3_W = 1190.55
A3_H = 841.89

# Source page index (0-based) → reading-order page number.
# Each press sheet is (left_page, right_page).
SHEETS = (
    (8, 1),  # outer face
    (2, 7),  # outer back
    (6, 3),  # inner face
    (4, 5),  # inner back
)


def _place_half(sheet: PageObject, src: PageObject, *, left: bool) -> None:
    """Scale one A4 page into the left or right half of an A3 landscape sheet."""
    src_w = float(src.mediabox.width)
    src_h = float(src.mediabox.height)
    half_w = A3_W / 2.0
    scale_x = half_w / src_w
    scale_y = A3_H / src_h
    # Uniform scale keeps proportions; slight letterbox is fine at the cut edge.
    scale = min(scale_x, scale_y)
    scaled_w = src_w * scale
    scaled_h = src_h * scale
    tx = (0.0 if left else half_w) + (half_w - scaled_w) / 2.0
    ty = (A3_H - scaled_h) / 2.0
    sheet.merge_transformed_page(
        src,
        Transformation().scale(scale, scale).translate(tx, ty),
    )


def build_press_pdf(source: Path = SOURCE, dest: Path = PRESS) -> Path:
    if not source.exists():
        raise SystemExit(f"missing source PDF: {source}")
    reader = PdfReader(str(source))
    if len(reader.pages) != 8:
        raise SystemExit(f"expected 8 A4 pages, got {len(reader.pages)}")

    writer = PdfWriter()
    for left_no, right_no in SHEETS:
        sheet = PageObject.create_blank_page(width=A3_W, height=A3_H)
        _place_half(sheet, reader.pages[left_no - 1], left=True)
        _place_half(sheet, reader.pages[right_no - 1], left=False)
        writer.add_page(sheet)

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
    sheet = Image.new(
        "RGB",
        (2 * width + 3 * gap, 2 * height + 3 * gap),
        (12, 14, 22),
    )
    labels = (
        "A face  08|01",
        "A back  02|07",
        "B face  06|03",
        "B back  04|05",
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
    for index, label in enumerate(labels, start=1):
        print(f"  PDF page {index}: {label}")


if __name__ == "__main__":
    build_press_pdf()
    contact_sheet()
