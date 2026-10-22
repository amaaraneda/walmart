"""Validate human shelf-front and empty-space polygons before model evaluation."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


def _polygon(value, width: int, height: int, label: str):
    if not isinstance(value, list) or len(value) < 3:
        raise ValueError(f"{label}: se requieren al menos tres puntos")
    points = []
    for point in value:
        if not isinstance(point, list) or len(point) != 2:
            raise ValueError(f"{label}: punto inválido")
        x, y = point
        if (isinstance(x, bool) or isinstance(y, bool) or
                not isinstance(x, (int, float)) or not isinstance(y, (int, float)) or
                not math.isfinite(x) or not math.isfinite(y) or
                not 0 <= x < width or not 0 <= y < height):
            raise ValueError(f"{label}: coordenada fuera de imagen")
        points.append((x, y))
    return points


def _mask(size, polygons):
    mask = Image.new("1", size, 0)
    draw = ImageDraw.Draw(mask)
    for polygon in polygons:
        draw.polygon(polygon, fill=1)
    return mask


def measure_shelf(shelf: dict, width: int, height: int):
    """Return reference occupancy and alert for a clear, fully reviewed level."""
    roi = _polygon(shelf.get("roi"), width, height, "roi")
    gaps = shelf.get("gaps")
    if not isinstance(gaps, list):
        raise ValueError("gaps debe ser una lista; [] significa lleno y revisado")
    gap_polygons = [_polygon(g, width, height, f"gap {i}") for i, g in enumerate(gaps)]
    roi_mask = _mask((width, height), [roi])
    gap_mask = _mask((width, height), gap_polygons)
    roi_array = np.asarray(roi_mask, dtype=bool)
    gap_array = np.asarray(gap_mask, dtype=bool)
    roi_area = int(roi_array.sum())
    gap_area = int(gap_array.sum())
    if roi_area == 0:
        raise ValueError("roi tiene área cero")
    outside_area = int(np.logical_and(gap_array, ~roi_array).sum())
    if outside_area:
        raise ValueError(f"{outside_area} píxeles de huecos fuera de roi")
    roi_columns = int(roi_array.any(axis=0).sum())
    gap_columns = int(gap_array.any(axis=0).sum())
    occupancy = 100 * (roi_columns - gap_columns) / roi_columns
    area_occupancy = 100 * (roi_area - gap_area) / roi_area
    return {"occupancy_percent": occupancy, "area_occupancy_percent": area_occupancy,
            "low_stock_alert": occupancy < 30}


def validate_record(record: dict, root: Path, *, require_reviewed: bool = True):
    if not isinstance(record, dict) or record.get("version") != 1:
        raise ValueError("version debe ser 1")
    image_name = record.get("image")
    if not isinstance(image_name, str) or Path(image_name).name != image_name or image_name in ("", ".", ".."):
        raise ValueError("image debe ser un nombre de archivo simple")
    image_path = root / "images" / image_name
    if not image_path.is_file():
        raise ValueError(f"no existe la imagen {image_path}")
    with Image.open(image_path) as image:
        width, height = image.size
    if record.get("width") != width or record.get("height") != height:
        raise ValueError(f"dimensiones JSON distintas de imagen ({width}×{height})")
    scene_id = record.get("scene_id")
    if not isinstance(scene_id, str) or not scene_id.strip():
        raise ValueError("scene_id obligatorio")
    split = record.get("split")
    if split not in ("train", "val", "test"):
        raise ValueError("split debe ser train, val o test")
    status = record.get("review_status")
    if status not in ("draft", "reviewed") or (require_reviewed and status != "reviewed"):
        raise ValueError("la anotación debe estar revisada")
    shelves = record.get("shelves")
    if not isinstance(shelves, list) or not shelves:
        raise ValueError("shelves debe incluir al menos un nivel")
    ids = set()
    results = []
    for shelf in shelves:
        if not isinstance(shelf, dict):
            raise ValueError("nivel inválido")
        shelf_id = shelf.get("id")
        if not isinstance(shelf_id, str) or not shelf_id or shelf_id in ids:
            raise ValueError("id de nivel ausente o duplicado")
        ids.add(shelf_id)
        visibility = shelf.get("visibility")
        if visibility not in ("clear", "occluded", "unusable"):
            raise ValueError(f"{shelf_id}: visibility inválida")
        if visibility == "clear":
            metric = measure_shelf(shelf, width, height)
            results.append({"shelf_id": shelf_id, **metric})
        else:
            results.append({"shelf_id": shelf_id, "excluded": visibility})
    return {"image": image_name, "scene_id": scene_id, "split": split, "shelves": results}


def validate_dataset(root: Path, *, require_reviewed: bool = True):
    annotation_paths = sorted((root / "annotations").glob("*.json"))
    if not annotation_paths:
        raise ValueError("no hay anotaciones reales en annotations/")
    records = []
    scenes = {}
    images = set()
    image_hashes = {}
    for path in annotation_paths:
        try:
            result = validate_record(json.loads(path.read_text(encoding="utf-8")), root,
                                     require_reviewed=require_reviewed)
        except (ValueError, OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"{path.name}: {exc}") from exc
        if result["image"] in images:
            raise ValueError(f"imagen duplicada: {result['image']}")
        images.add(result["image"])
        digest = hashlib.sha256((root / "images" / result["image"]).read_bytes()).hexdigest()
        if digest in image_hashes:
            raise ValueError(f"imágenes idénticas: {image_hashes[digest]} y {result['image']}")
        image_hashes[digest] = result["image"]
        scene = result["scene_id"]
        if scene in scenes and scenes[scene] != result["split"]:
            raise ValueError(f"fuga de escena {scene}: {scenes[scene]} / {result['split']}")
        scenes[scene] = result["split"]
        records.append(result)
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="directorio con images/ y annotations/")
    parser.add_argument("--allow-drafts", action="store_true")
    args = parser.parse_args()
    try:
        records = validate_dataset(args.root, require_reviewed=not args.allow_drafts)
    except ValueError as exc:
        parser.exit(1, f"ERROR: {exc}\n")
    counts = Counter(record["split"] for record in records)
    print(f"Válido: {len(records)} imágenes; escenas: {len(set(r['scene_id'] for r in records))}; splits: {dict(counts)}")
    for record in records:
        for shelf in record["shelves"]:
            if "excluded" in shelf:
                print(f"{record['image']} / {shelf['shelf_id']}: excluido ({shelf['excluded']})")
            else:
                print(f"{record['image']} / {shelf['shelf_id']}: {shelf['occupancy_percent']:.2f}% ; alerta={shelf['low_stock_alert']}")


if __name__ == "__main__":
    main()
