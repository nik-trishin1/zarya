#!/usr/bin/env python3
"""Build collage assets from the supplied archive photo.

The galaxy crop stays to the right of the printed caption on that spread.
The child portrait and readable article pages are not used.
"""

import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
SOURCE = Path(
    "/home/ubuntu/.cursor/projects/workspace/assets/"
    "69851797-48eb-40ed-800b-08c0aaa96732.jpg"
)
COVER = Path(
    "/home/ubuntu/.cursor/projects/workspace/assets/"
    "eec33577-b631-4274-bc3a-1fc248c0ed73.webp"
)


def grade(image: Image.Image) -> Image.Image:
    image = ImageEnhance.Color(image).enhance(0.15)
    image = ImageEnhance.Contrast(image).enhance(1.3)
    image = ImageEnhance.Brightness(image).enhance(0.88)
    width, height = image.size
    mask = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse(
        (-int(width * 0.15), -int(height * 0.15), int(width * 1.15), int(height * 1.15)),
        fill=255,
    )
    mask = mask.filter(ImageFilter.GaussianBlur(radius=min(width, height) // 8))
    night = Image.new("RGB", (width, height), (8, 10, 18))
    return Image.composite(image, night, mask)


def main() -> None:
    ASSETS.mkdir(exist_ok=True)
    shutil.copy(COVER, ASSETS / "cover.webp")
    source = Image.open(SOURCE).convert("RGB")
    # Right-hand star field only: the caption column sits further left.
    crop = source.crop((530, 860, 950, 1240))
    grade(crop).save(ASSETS / "collage-galaxy.jpg", quality=92, subsampling=0)


if __name__ == "__main__":
    main()
