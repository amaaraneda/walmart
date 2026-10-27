"""Run the experimental void detector on the review queue; outputs are not labels."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps

from .model import Detector, VOID_CANDIDATE_WEIGHTS


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "stock_ground_truth_v1"
OUTPUT = ROOT / "artifacts" / "diagnostics" / "stock-pilot-triage"


def run():
    detector = Detector(VOID_CANDIDATE_WEIGHTS, class_name="void", imgsz=512)
    if not detector.ready:
        raise FileNotFoundError(detector.weights)
    with (DATA / "cola_revision.csv").open(encoding="utf-8-sig", newline="") as file:
        queue = list(csv.DictReader(file))
    OUTPUT.mkdir(parents=True, exist_ok=True)
    results = []
    for item in queue:
        path = DATA / "images" / item["image"]
        with Image.open(path) as source:
            image = ImageOps.exif_transpose(source).convert("RGB")
        boxes = detector.predict(image)
        regions = [{"xyxy": [round(box.x1), round(box.y1), round(box.x2), round(box.y2)],
                    "confidence": round(box.confidence, 4)} for box in boxes]
        results.append({"image": path.name, "role": item["role"], "candidate_count": len(boxes),
                        "regions": regions})
        preview = ImageOps.contain(image, (1200, 900))
        sx, sy = preview.width / image.width, preview.height / image.height
        draw = ImageDraw.Draw(preview)
        for box in boxes:
            draw.rectangle((box.x1 * sx, box.y1 * sy, box.x2 * sx, box.y2 * sy),
                           outline="#f03038", width=3)
            draw.text((box.x1 * sx, max(0, box.y1 * sy - 14)), f"{box.confidence:.2f}",
                      fill="#ffeff0", stroke_width=2, stroke_fill="#9a141b")
        preview.save(OUTPUT / f"{path.stem}.jpg", quality=88)
        print(f"{path.name}: {len(boxes)} candidatos", flush=True)
    (OUTPUT / "propuestas.json").write_text(json.dumps({"model": str(detector.weights),
        "confidence_threshold": 0.25, "warning": "Predicciones sin validar; NO son etiquetas ni stock",
        "images": results}, indent=2, ensure_ascii=False), encoding="utf-8")
    return results


if __name__ == "__main__":
    run()
