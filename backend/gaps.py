"""Limpieza de máscaras predichas y extracción de regiones vacías visibles."""

import cv2
import numpy as np
from PIL import Image


def extract_gap_regions(probability: np.ndarray, *, threshold: float = .6) -> tuple[np.ndarray, list[dict]]:
    if probability.ndim != 2 or probability.size == 0:
        raise ValueError("La máscara debe ser bidimensional")
    height, width = probability.shape
    mask = np.ascontiguousarray((probability >= threshold).astype(np.uint8))
    kernel_size = max(3, round(min(width, height) * .005))
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    count, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    cleaned = np.zeros_like(mask)
    regions = []
    min_area = max(80, round(width * height * .002))
    for component in range(1, count):
        x, y, w, h, area = (int(value) for value in stats[component])
        if area < min_area or w < width * .025 or h < height * .025:
            continue
        region_mask = labels[y:y+h, x:x+w] == component
        cleaned[y:y+h, x:x+w][region_mask] = 1
        regions.append({"left": x, "top": y, "right": x+w, "bottom": y+h, "area_px": area, "mean_probability": round(float(probability[y:y+h, x:x+w][region_mask].mean()), 3)})
    regions.sort(key=lambda item: item["area_px"], reverse=True)
    return cleaned, regions


def annotate_gaps(image: Image.Image, mask: np.ndarray, regions: list[dict]) -> Image.Image:
    source = np.asarray(image.convert("RGB")).copy()
    tint = source.copy()
    tint[mask > 0] = (245, 61, 71)
    annotated = cv2.addWeighted(source, .68, tint, .32, 0)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(annotated, contours, -1, (225, 32, 52), max(2, round(image.width / 900)))
    for index, region in enumerate(regions, 1):
        cv2.putText(annotated, str(index), (region["left"] + 4, max(18, region["top"] + 18)), cv2.FONT_HERSHEY_SIMPLEX, .65, (255, 255, 255), 2, cv2.LINE_AA)
    return Image.fromarray(annotated)
