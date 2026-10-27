"""Diagnóstico por fotografía contra sus etiquetas YOLO, sin cambiar pesos."""

import argparse
import json
import time
from pathlib import Path

from PIL import Image, ImageDraw
from ultralytics import YOLO

from .model import DEFAULT_WEIGHTS
from .tiled_detection import predict_with_tiles


ROOT = Path(__file__).resolve().parents[1]


def iou(a, b):
    intersection = max(0, min(a[2], b[2]) - max(a[0], b[0])) * max(0, min(a[3], b[3]) - max(a[1], b[1]))
    area_a = (a[2] - a[0]) * (a[3] - a[1])
    area_b = (b[2] - b[0]) * (b[3] - b[1])
    return intersection / max(area_a + area_b - intersection, 1)


def ground_truth(image: Path, label: Path):
    with Image.open(image) as source:
        width, height = source.size
    boxes = []
    for line in label.read_text(encoding="utf-8").splitlines():
        values = line.split()
        if len(values) < 5:
            continue
        _, cx, cy, w, h = map(float, values[:5])
        boxes.append(((cx - w / 2) * width, (cy - h / 2) * height, (cx + w / 2) * width, (cy + h / 2) * height))
    return boxes


def score(predictions, truth):
    unmatched = set(range(len(truth)))
    matched = 0
    for box, confidence in sorted(predictions, key=lambda item: item[1], reverse=True):
        if not unmatched:
            break
        candidate = max(unmatched, key=lambda j: iou(box, truth[j]))
        if iou(box, truth[candidate]) >= .5:
            unmatched.remove(candidate)
            matched += 1
    return {"predictions": len(predictions), "matched": matched, "precision": round(matched / max(len(predictions), 1), 3), "recall": round(matched / max(len(truth), 1), 3)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=Path, required=True)
    parser.add_argument("--weights", type=Path, default=DEFAULT_WEIGHTS)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--preview-dir", type=Path)
    parser.add_argument("--tiles", action="store_true")
    args = parser.parse_args()
    image = args.image.resolve()
    label = Path(str(image).replace("\\images\\", "\\labels\\").replace("/images/", "/labels/")).with_suffix(".txt")
    if not label.is_file():
        raise FileNotFoundError(label)
    truth = ground_truth(image, label)
    model = YOLO(str(args.weights))
    if args.preview_dir:
        args.preview_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for size in (640, 960, 1280):
        started = time.perf_counter()
        result = model.predict(str(image), imgsz=size, conf=.10, max_det=1000, device="cpu", verbose=False)[0]
        elapsed = time.perf_counter() - started
        all_predictions = [(tuple(row[:4]), float(row[4])) for row in result.boxes.data.cpu().tolist()]
        for threshold in (.10, .25, .35, .50):
            selected = [(box, confidence) for box, confidence in all_predictions if confidence >= threshold]
            rows.append({"imgsz": size, "confidence": threshold, "seconds": round(elapsed, 3), **score(selected, truth)})
            if args.preview_dir and size == 640 and threshold in (.25, .35, .50):
                with Image.open(image) as source:
                    preview = source.convert("RGB")
                draw = ImageDraw.Draw(preview)
                for box, _ in selected:
                    draw.rectangle(box, outline="#00d496", width=2)
                preview.save(args.preview_dir / f"predictions_{int(threshold*100)}.jpg", quality=90)
    if args.preview_dir:
        with Image.open(image) as source:
            preview = source.convert("RGB")
        draw = ImageDraw.Draw(preview)
        for box in truth:
            draw.rectangle(box, outline="#ffbe2f", width=2)
        preview.save(args.preview_dir / "ground_truth.jpg", quality=90)
    if args.tiles:
        with Image.open(image) as source:
            tiled_image = source.convert("RGB")
        started = time.perf_counter()
        tiled = predict_with_tiles(model, tiled_image)
        elapsed = time.perf_counter() - started
        rows.append({"imgsz": 640, "confidence": .25, "method": "full_plus_four_tiles", "seconds": round(elapsed, 3), **score([((box.x1, box.y1, box.x2, box.y2), box.confidence) for box in tiled], truth)})
        if args.preview_dir:
            draw = ImageDraw.Draw(tiled_image)
            for box in tiled:
                draw.rectangle((box.x1, box.y1, box.x2, box.y2), outline="#00d496" if box.confidence >= .5 else "#e6a828", width=2)
            tiled_image.save(args.preview_dir / "predictions_tiled.jpg", quality=90)
    report = {"image": str(image), "ground_truth_boxes": len(truth), "rows": rows}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
