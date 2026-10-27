"""Copy the 60 supplied pilot photos into the ignored local annotation workspace."""

from __future__ import annotations

import csv
import shutil
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
DATASETS = ROOT / "Datasets-20260912T011718Z-1-001" / "Datasets"
DEST = ROOT / "data" / "stock_ground_truth_v1"
SOURCES = (
    ("grocery", DATASETS / "Grocery Shelves Dataset" / "img"),
    ("supermarket", DATASETS / "Supermarket shelves" / "Supermarket shelves" / "images"),
)


def bootstrap(destination: Path = DEST):
    images = destination / "images"
    images.mkdir(parents=True, exist_ok=True)
    rows = []
    for prefix, source in SOURCES:
        if not source.is_dir():
            raise FileNotFoundError(source)
        for path in sorted(source.iterdir()):
            if path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
                continue
            name = f"{prefix}_{path.name}"
            target = images / name
            if target.exists() and target.read_bytes() != path.read_bytes():
                raise ValueError(f"no se sobrescribirá una imagen diferente: {target}")
            if not target.exists():
                shutil.copy2(path, target)
            with Image.open(path) as image:
                width, height = image.size
            rows.append((name, prefix, str(path.relative_to(ROOT)), width, height,
                         "pendiente", "pendiente", "pendiente"))
    manifest = destination / "inventario_piloto.csv"
    if manifest.exists():
        raise FileExistsError(f"inventario existente; no se sobrescribirá: {manifest}")
    with manifest.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow(("image", "source_dataset", "source_path", "width", "height",
                         "scene_id", "split", "annotation_status"))
        writer.writerows(rows)
    return len(rows), manifest


if __name__ == "__main__":
    count, path = bootstrap()
    print(f"Preparadas {count} fotografías; inventario: {path}")
