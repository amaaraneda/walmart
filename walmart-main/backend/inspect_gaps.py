"""Genera previsualizaciones para auditar el detector de huecos candidato."""

import argparse
import json
from pathlib import Path

from PIL import Image

from .gap_model import GapSegmenter
from .gaps import annotate_gaps, extract_gap_regions


ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--weights", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/gap_inspection")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    examples = sorted((ROOT / "data/shelf_products_v2/images/test").glob("*.jpg"))[:3]
    examples += sorted((ROOT / "data/standardized_yolo_v1/images/test").glob("*.jpg"))[:3]
    examples += sorted((ROOT / "data/gap_detection_public/WebMarket/Test/Images").glob("*.jpg"))[:3]
    examples += sorted((ROOT / "data/gap_detection_public/GroZi-120/Test/Images").glob("*.jpg"))[:3]
    segmenter = GapSegmenter(args.weights)
    rows = []
    for index, path in enumerate(examples, 1):
        with Image.open(path) as source:
            image = source.convert("RGB")
            mask, regions = extract_gap_regions(segmenter.predict(image))
            target = args.output / f"example_{index:02d}.jpg"
            annotate_gaps(image, mask, regions).save(target, quality=86)
            rows.append({"image": str(path), "preview": str(target), "regions": len(regions)})
    (args.output / "report.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
