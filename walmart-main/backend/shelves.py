"""Localización automática preliminar de frentes de estante en una foto.

Combina líneas horizontales largas (rieles) con detecciones de productos. No
infiere inventario físico ni afirma que un tramo sin detección esté vacío.
"""

from dataclasses import dataclass

import cv2
import numpy as np
from PIL import Image

from .coverage import Box, measure_shelf_front


@dataclass(frozen=True)
class Shelf:
    x1: int
    y1: int
    x2: int
    y2: int
    source: str


def _rails(image: Image.Image) -> list[tuple[int, int, int]]:
    width, height = image.size
    scale = min(1.0, 960 / width)
    small = cv2.resize(np.asarray(image), (round(width * scale), round(height * scale)))
    gray = cv2.cvtColor(small, cv2.COLOR_RGB2GRAY)
    edge = cv2.Canny(cv2.GaussianBlur(gray, (5, 5), 0), 50, 150)
    lines = cv2.HoughLinesP(edge, 1, np.pi / 180, threshold=max(45, round(small.shape[1] * .07)), minLineLength=max(80, round(small.shape[1] * .20)), maxLineGap=round(small.shape[1] * .025))
    candidates = []
    if lines is None:
        return candidates
    for item in lines.reshape(-1, 4):
        x1, y1, x2, y2 = map(int, item)
        if abs(y2 - y1) > max(5, .015 * abs(x2 - x1)):
            continue
        candidates.append((round(min(x1, x2) / scale), round((y1 + y2) / (2 * scale)), round(max(x1, x2) / scale)))
    # Fusiona bordes superior/inferior del mismo riel cuando comparten extensión.
    groups: list[list[float]] = []
    tolerance = max(8, round(height * .012))
    for left, y, right in sorted(candidates, key=lambda row: row[1]):
        found = next((group for group in groups if abs(group[1] - y) <= tolerance and min(group[2], right) - max(group[0], left) > 0), None)
        if found:
            found[0] = min(found[0], left)
            found[1] = (found[1] * found[3] + y) / (found[3] + 1)
            found[2] = max(found[2], right)
            found[3] += 1
        else:
            groups.append([left, y, right, 1])
    return [(round(left), round(y), round(right)) for left, y, right, _ in groups if right - left >= width * .20]


def locate_shelves(image: Image.Image, boxes: list[Box]) -> list[Shelf]:
    width, height = image.size
    rails = _rails(image)
    def support(rail):
        left, y, right = rail
        return sum(1 for box in boxes if abs(box.y2 - y) < height * .03 and box.x2 >= left and box.x1 <= right)
    rails = [rail for rail in rails if support(rail) >= 4]
    candidates = []
    margin = max(3, round(height * .006))
    for left, bottom, right in rails:
        compatible = [(l2, y2, r2) for l2, y2, r2 in rails if y2 < bottom - height * .09 and y2 >= bottom - height * .45 and min(right, r2) - max(left, l2) >= .60 * min(right - left, r2 - l2)]
        if compatible:
            top_rail = max(compatible, key=lambda row: row[1])
            top = top_rail[1] + margin
            x1, x2 = max(left, top_rail[0]), min(right, top_rail[2])
            source = "rail_pair"
        else:
            matching = [box for box in boxes if left <= (box.x1 + box.x2) / 2 <= right and bottom - height * .40 <= box.y2 <= bottom + height * .03]
            if len(matching) < 2:
                continue
            top = max(0, round(min(box.y1 for box in matching)))
            x1, x2 = left, right
            source = "rail_inferred_top"
        if bottom - top < max(50, .08 * height) or x2 - x1 < .20 * width:
            continue
        # Una sola toma no permite confirmar estantes enteramente vacíos.
        product_count = sum(x1 <= (b.x1 + b.x2) / 2 <= x2 and top <= (b.y1 + b.y2) / 2 <= bottom for b in boxes)
        if product_count >= 2:
            candidates.append(Shelf(max(0, x1), max(0, top), min(width, x2), min(height, bottom - margin), source))
    # Sin riel verificable, sólo agrupa productos próximos en altura y reporta
    # un resultado para revisión; jamás usa toda la imagen como denominador.
    if not candidates and boxes:
        centers = sorted((((b.y1 + b.y2) / 2, b) for b in boxes), key=lambda item: item[0])
        groups: list[list[Box]] = []
        for cy, box in centers:
            if not groups or cy - (sum((b.y1 + b.y2) / 2 for b in groups[-1]) / len(groups[-1])) > height * .11:
                groups.append([box])
            else:
                groups[-1].append(box)
        for group in groups:
            if len(group) < 2:
                continue
            left = max(0, round(min(b.x1 for b in group)))
            right = min(width, round(max(b.x2 for b in group)))
            wide = len(group) >= 6 and (right - left) / width >= .80
            candidates.append(Shelf(0 if wide else left, max(0, round(min(b.y1 for b in group))), width if wide else right, min(height, round(max(b.y2 for b in group))), "image_width_products" if wide else "products_only"))
    # Rieles superpuestos representan el mismo nivel: preferir el mayor ancho.
    chosen = []
    for shelf in sorted(candidates, key=lambda s: (s.y1, s.x1)):
        if shelf.x2 - shelf.x1 < 64 or shelf.y2 - shelf.y1 < 64:
            continue
        duplicate = next((i for i, old in enumerate(chosen) if min(old.y2, shelf.y2) - max(old.y1, shelf.y1) > .50 * min(old.y2 - old.y1, shelf.y2 - shelf.y1) and min(old.x2, shelf.x2) - max(old.x1, shelf.x1) > .55 * min(old.x2 - old.x1, shelf.x2 - shelf.x1)), None)
        if duplicate is None:
            chosen.append(shelf)
        elif (shelf.source == "rail_pair", shelf.x2 - shelf.x1) > (chosen[duplicate].source == "rail_pair", chosen[duplicate].x2 - chosen[duplicate].x1):
            chosen[duplicate] = shelf
    return sorted(chosen, key=lambda s: (s.y1, s.x1))


def analyze_shelves(image: Image.Image, boxes: list[Box], threshold: float) -> list[dict]:
    rows = []
    for index, shelf in enumerate(locate_shelves(image, boxes), 1):
        selected = []
        for box in boxes:
            cy = (box.y1 + box.y2) / 2
            cx = (box.x1 + box.x2) / 2
            if shelf.y1 <= cy <= shelf.y2 and shelf.x1 <= cx <= shelf.x2:
                selected.append(Box(max(0, box.x1 - shelf.x1), max(0, box.y1 - shelf.y1), min(shelf.x2 - shelf.x1, box.x2 - shelf.x1), min(shelf.y2 - shelf.y1, box.y2 - shelf.y1), box.confidence))
        measurement = measure_shelf_front(selected, shelf.x2 - shelf.x1, shelf.y2 - shelf.y1)
        # Agrupar por productos produce un denominador sesgado hacia lo visible.
        # Estos niveles se muestran, pero no generan alertas automáticas.
        trusted = shelf.source in {"rail_pair", "image_width_products"} and len(selected) >= 2
        occupancy = measurement["occupancy_percent"]
        rows.append({"id": index, "region": {"left": shelf.x1, "top": shelf.y1, "right": shelf.x2, "bottom": shelf.y2}, "source": shelf.source, "detections": len(selected), "occupancy_percent": occupancy, "empty_percent": measurement["empty_percent"], "empty_regions": [{**gap, "x1": gap["x1"] + shelf.x1, "x2": gap["x2"] + shelf.x1, "y1": shelf.y1, "y2": shelf.y2} for gap in measurement["empty_regions"]], "low_stock_alert": occupancy < threshold if trusted and occupancy is not None else None, "review_required": not trusted or measurement["review_required"]})
    return rows
