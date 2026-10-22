"""Print the current automatic shelf proposals for local pilot images."""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageOps

from .model import COMPANION_WEIGHTS, Detector
from .shelves import analyze_shelves
from .visual_occupancy import estimate_visual_occupancy


def main(paths: list[str]):
    detector = Detector(COMPANION_WEIGHTS)
    for name in paths:
        path = Path(name)
        with Image.open(path) as source:
            image = ImageOps.exif_transpose(source).convert("RGB")
        boxes = detector.predict(image)
        bins = {}
        bin_size = max(12, round(image.height * .025))
        for box in boxes:
            key = round(box.y2 / bin_size) * bin_size
            bins[key] = bins.get(key, 0) + 1
        print(" bottom_peaks", sorted(bins.items(), key=lambda item: item[1], reverse=True)[:12])
        rows = analyze_shelves(image, boxes, 30)
        new = estimate_visual_occupancy(boxes, *image.size)
        print(path.name, "products", len(boxes), "image", image.size, "shelves", len(rows))
        print(" new", new["occupancy_percent"], new["reason"],
              [(s["region"]["top"], s["region"]["bottom"], s["occupancy_percent"])
               for s in new["shelves"]])
        for row in rows:
            print(" ", row["id"], row["source"], row["region"],
                  row["detections"], row["occupancy_percent"], "review", row["review_required"])


if __name__ == "__main__":
    main(sys.argv[1:])
