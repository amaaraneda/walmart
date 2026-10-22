"""Estimación experimental de ocupación horizontal de una región de estante."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Box:
    x1: float
    y1: float
    x2: float
    y2: float
    confidence: float


def union_length(intervals: list[tuple[float, float]]) -> float:
    """Longitud de la unión; nunca cuenta dos veces cajas superpuestas."""
    total = 0.0
    end = 0.0
    for left, right in sorted(intervals):
        if right <= end:
            continue
        total += right - max(left, end)
        end = right
    return total


def estimate_occupancy(
    boxes: list[Box], width: int, height: int, *, samples: int = 9
) -> float:
    """Promedia la cobertura horizontal en líneas centrales de la región.

    La imagen debe representar un solo nivel de góndola. No equivale a unidades
    físicas en inventario y depende de la calidad del detector y el encuadre.
    """
    if width <= 0 or height <= 0 or samples <= 0:
        raise ValueError("Dimensiones y número de muestras deben ser positivos")
    fractions = []
    for i in range(samples):
        y = height * (0.2 + 0.6 * i / max(samples - 1, 1))
        intervals = [
            (max(0.0, box.x1), min(float(width), box.x2))
            for box in boxes
            if box.y1 <= y <= box.y2 and box.x2 > box.x1
        ]
        fractions.append(union_length(intervals) / width)
    return round(100 * sum(fractions) / samples, 1)


def measure_shelf_front(boxes: list[Box], width: int, height: int) -> dict:
    """Cobertura del frente útil: proyección horizontal, independiente de altura.

    La región debe corresponder a un único nivel. El complemento son tramos
    sin detecciones, no segmentación supervisada de espacios vacíos.
    """
    if width <= 0 or height <= 0:
        raise ValueError("Las dimensiones deben ser positivas")
    intervals = []
    for box in boxes:
        left, right = max(0.0, box.x1), min(float(width), box.x2)
        if right > left and min(height, box.y2) > max(0, box.y1):
            intervals.append((left, right))
    if not intervals:
        return {"occupancy_percent": None, "empty_percent": None, "empty_regions": [], "review_required": True, "usable_width_px": width, "occupied_width_px": None}
    merged = []
    for left, right in sorted(intervals):
        if merged and left <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], right)
        else:
            merged.append([left, right])
    gaps = []
    cursor = 0.0
    for left, right in merged:
        if left > cursor:
            gaps.append({"x1": cursor, "y1": 0, "x2": left, "y2": height, "width_percent": round(100 * (left - cursor) / width, 2)})
        cursor = right
    if cursor < width:
        gaps.append({"x1": cursor, "y1": 0, "x2": width, "y2": height, "width_percent": round(100 * (width - cursor) / width, 2)})
    occupied = sum(right - left for left, right in merged)
    percent = round(100 * occupied / width, 1)
    return {"occupancy_percent": percent, "empty_percent": round(100 - percent, 1), "empty_regions": gaps, "review_required": False, "usable_width_px": width, "occupied_width_px": round(occupied, 2)}
