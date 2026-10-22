"""Automatic *experimental* shelf-front coverage, never physical inventory."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .coverage import Box, union_length


@dataclass(frozen=True)
class Front:
    y: int
    top: int
    boxes: list[Box]


def _fronts(boxes: list[Box], height: int) -> list[Front]:
    """Find rows supported by several product bottoms, not arbitrary rail fragments."""
    if len(boxes) < 3:
        return []
    bin_px = max(4, round(height / 250))
    counts = np.zeros(height // bin_px + 3, dtype=float)
    for box in boxes:
        if box.y2 > box.y1 and 0 <= box.y2 <= height:
            counts[min(len(counts) - 1, round(box.y2 / bin_px))] += 1
    sigma = max(1.0, .012 * height / bin_px)
    offsets = np.arange(-round(3 * sigma), round(3 * sigma) + 1)
    kernel = np.exp(-.5 * (offsets / sigma) ** 2)
    smooth = np.convolve(counts, kernel / kernel.sum(), mode="same")
    radius = max(1, round(.075 * height / bin_px))
    threshold = max(.5, .01 * len(boxes))
    candidates = []
    for i in range(1, len(smooth) - 1):
        if smooth[i] >= threshold and smooth[i] >= smooth[i - 1] and smooth[i] > smooth[i + 1]:
            candidates.append((float(smooth[i]), i * bin_px))
    selected = []
    for strength, y in sorted(candidates, reverse=True):
        if all(abs(y - old_y) >= radius * bin_px for old_y in selected):
            selected.append(y)
    fronts = []
    for y in sorted(selected):
        aligned = [box for box in boxes if abs(box.y2 - y) <= .04 * height]
        if len(aligned) < 3:
            continue
        tops = sorted(box.y1 for box in aligned)
        top = max(0, round(tops[max(0, round(.15 * (len(tops) - 1)))] - .01 * height))
        if y - top < .035 * height:
            continue
        if top < .02 * height:
            # The upper face is cut by the photo edge; its actual front is unknown.
            continue
        fronts.append(Front(round(y), top, aligned))
    return fronts


def estimate_visual_occupancy(boxes: list[Box], width: int, height: int,
                              void_boxes: list[Box] | None = None) -> dict:
    """Estimate occupied frontage width per shelf; keep all alerts unvalidated."""
    if width <= 0 or height <= 0:
        raise ValueError("image dimensions must be positive")
    fronts = _fronts(boxes, height)
    if not fronts:
        return {"occupancy_percent": None, "shelves": [], "reason": "no_stable_shelf_rows"}
    global_left = min(box.x1 for box in boxes)
    global_right = max(box.x2 for box in boxes)
    # A shelf only becomes measurable if another observed row establishes a
    # wide, full-frame front. A row's own product span cannot define its width:
    # that would make a nearly empty row look 100% occupied.
    wide_reference = any(len(front.boxes) >= 6 and
                         max(box.x2 for box in front.boxes) - min(box.x1 for box in front.boxes) >= .75 * width
                         for front in fronts)
    frame_supported = global_left <= .12 * width and global_right >= .88 * width and wide_reference
    if not frame_supported:
        return {"occupancy_percent": None, "shelves": [], "reason": "shelf_width_not_observable"}
    margin = round(.02 * width)
    left, right = margin, width - margin
    usable = right - left
    results = []
    occupied_sum = 0.0
    for index, front in enumerate(fronts, 1):
        intervals = [(max(left, b.x1), min(right, b.x2)) for b in front.boxes
                     if b.x2 > left and b.x1 < right]
        covered = union_length(intervals)
        if not intervals:
            continue
        percent = round(100 * covered / usable, 1)
        candidate_intervals = []
        for candidate in void_boxes or []:
            cy = (candidate.y1 + candidate.y2) / 2
            if front.top <= cy <= front.y and candidate.x2 > left and candidate.x1 < right:
                candidate_intervals.append((max(left, candidate.x1), min(right, candidate.x2)))
        results.append({"id": index, "region": {"left": left, "top": front.top,
                        "right": right, "bottom": min(height, front.y)},
                        "detections": len(front.boxes), "occupancy_percent": percent,
                        "empty_percent": round(100 - percent, 1),
                        "void_candidate_percent": round(100 * union_length(candidate_intervals) / usable, 1)
                        if void_boxes is not None else None,
                        "low_stock_candidate": percent < 30,
                        "low_stock_alert": None, "review_required": True,
                        "method": "product_box_frontage_projection"})
        occupied_sum += covered
    if not results:
        return {"occupancy_percent": None, "shelves": [], "reason": "no_measurable_rows"}
    overall = round(100 * occupied_sum / (usable * len(results)), 1)
    return {"occupancy_percent": overall, "shelves": results,
            "reason": "experimental_frontage_coverage_not_inventory"}
