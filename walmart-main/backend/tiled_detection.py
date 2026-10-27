"""Inferencia por recortes solapados para objetos pequeños en fotos completas."""

from PIL import Image

from .coverage import Box


def overlap(a: Box, b: Box) -> float:
    x = max(0., min(a.x2, b.x2) - max(a.x1, b.x1))
    y = max(0., min(a.y2, b.y2) - max(a.y1, b.y1))
    intersection = x * y
    union = (a.x2-a.x1)*(a.y2-a.y1) + (b.x2-b.x1)*(b.y2-b.y1) - intersection
    return intersection / union if union > 0 else 0.


def merge_boxes(boxes: list[Box], threshold: float = .55) -> list[Box]:
    kept = []
    for box in sorted(boxes, key=lambda item: item.confidence, reverse=True):
        if not any(overlap(box, previous) >= threshold for previous in kept):
            kept.append(box)
    return kept


def predict_with_tiles(model, image: Image.Image, *, imgsz: int = 640, conf: float = .25) -> list[Box]:
    width, height = image.size
    positions = [(0, 0, width, height)]
    if width >= 400 and height >= 400:
        tile_width = round(width * .70)
        tile_height = round(height * .70)
        positions += [(left, top, left + tile_width, top + tile_height) for left in (0, width - tile_width) for top in (0, height - tile_height)]
    predictions = []
    for left, top, right, bottom in positions:
        crop = image.crop((left, top, right, bottom))
        result = model.predict(crop, conf=conf, imgsz=imgsz, max_det=1000, verbose=False)[0]
        for row in result.boxes.data.cpu().tolist():
            if int(row[5]) != 0:
                continue
            x1, y1, x2, y2, confidence = row[:5]
            predictions.append(Box(max(0., x1 + left), max(0., y1 + top), min(float(width), x2 + left), min(float(height), y2 + top), confidence))
    return merge_boxes(predictions)
