"""Generate a visual contact sheet and exact/near-duplicate candidates for pilot review."""

from __future__ import annotations

import csv
import hashlib
from itertools import combinations
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps


ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / "data" / "stock_ground_truth_v1" / "images"
OUTPUT = ROOT / "artifacts" / "diagnostics" / "stock-pilot-audit"


def dhash(image):
    gray = image.convert("L").resize((9, 8))
    values = list(gray.getdata())
    return sum((values[y * 9 + x] > values[y * 9 + x + 1]) << (y * 8 + x)
               for y in range(8) for x in range(8))


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    records = []
    for path in sorted(IMAGES.iterdir()):
        if not path.is_file() or path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
            continue
        with Image.open(path) as image:
            records.append((path, image.size, hashlib.sha256(path.read_bytes()).hexdigest(), dhash(image)))
    for start in range(0, len(records), 15):
        sheet = Image.new("RGB", (1200, 900), "#e9edf1")
        draw = ImageDraw.Draw(sheet)
        for i, (path, size, _, _) in enumerate(records[start:start + 15]):
            col, row = i % 3, i // 3
            x, y = col * 400, row * 180
            with Image.open(path) as image:
                thumb = ImageOps.contain(image.convert("RGB"), (380, 140))
            sheet.paste(thumb, (x + (400 - thumb.width) // 2, y))
            draw.text((x + 10, y + 145), f"{path.name}  {size[0]}x{size[1]}", fill="#102c43")
        sheet.save(OUTPUT / f"contacto_{start // 15 + 1:02d}.jpg", quality=90)
    with (OUTPUT / "candidatos_duplicados.csv").open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow(("image_a", "image_b", "same_sha256", "dhash_distance"))
        for a, b in combinations(records, 2):
            distance = (a[3] ^ b[3]).bit_count()
            if a[2] == b[2] or distance <= 5:
                writer.writerow((a[0].name, b[0].name, a[2] == b[2], distance))
    print(f"{len(records)} fotos; {len(list(OUTPUT.glob('contacto_*.jpg')))} hojas; {OUTPUT}")


if __name__ == "__main__":
    main()
