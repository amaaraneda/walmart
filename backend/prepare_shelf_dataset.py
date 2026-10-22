"""Crea una copia YOLO monoclase con escenas disjuntas; preserva el original."""

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import random
import shutil


ROOT = Path(__file__).resolve().parents[1]


def prepare(source: Path, output: Path, seed: int = 20261018):
    if output.exists():
        raise FileExistsError(f"El destino ya existe: {output}")
    records = []
    excluded = Counter()
    for image in sorted(source.glob("*/images/*")):
        if image.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
            continue
        label = image.parent.parent / "labels" / (image.stem + ".txt")
        if not label.is_file():
            raise ValueError(f"Falta etiqueta: {image}")
        rows = [list(map(float, line.split())) for line in label.read_text().splitlines() if line.strip()]
        for row in rows:
            if len(row) != 5:
                raise ValueError(f"Etiqueta inválida: {label}")
            c, x, y, w, h = row
            if not (c.is_integer() and 0 <= c <= 10 and 0 <= x <= 1 and 0 <= y <= 1 and 0 < w <= 1 and 0 < h <= 1):
                raise ValueError(f"Coordenadas/clase inválidas: {label}")
        # No convertir objetos desconocidos en fondo: se excluye la imagen entera.
        if any(row[0] == 0 for row in rows):
            excluded["ambiguous_class_images"] += 1
            continue
        original = image.stem.split(".rf.")[0]
        scene = original.split("_")[0]
        records.append((image, original, scene, rows))
    if not records:
        raise ValueError("No hay imágenes utilizables")
    scenes = sorted({row[2] for row in records})
    if len(scenes) < 7:
        raise ValueError("Se requieren al menos siete escenas")
    random.Random(seed).shuffle(scenes)
    n_test = max(1, round(len(scenes) * .15))
    n_val = max(1, round(len(scenes) * .15))
    assignments = {s: "test" if i < n_test else "val" if i < n_test + n_val else "train" for i, s in enumerate(scenes)}
    output.mkdir(parents=True)
    seen_hashes = set()
    seen_eval_originals = set()
    counts = defaultdict(Counter)
    manifest = []
    for image, original, scene, rows in records:
        split = assignments[scene]
        digest = hashlib.sha256(image.read_bytes()).hexdigest()
        if digest in seen_hashes:
            excluded["exact_duplicates"] += 1
            continue
        if split != "train" and original in seen_eval_originals:
            excluded["evaluation_variants"] += 1
            continue
        seen_hashes.add(digest)
        if split != "train":
            seen_eval_originals.add(original)
        for folder in ("images", "labels"):
            (output / folder / split).mkdir(parents=True, exist_ok=True)
        shutil.copy2(image, output / "images" / split / image.name)
        # Todas las clases explícitas de producto se unifican; se quitan cajas idénticas.
        lines = sorted({"0 " + " ".join(f"{v:.8f}" for v in row[1:]) for row in rows})
        (output / "labels" / split / (image.stem + ".txt")).write_text("\n".join(lines) + "\n", encoding="utf-8")
        counts[split].update(images=1, boxes=len(lines))
        manifest.append({"image": image.name, "source": str(image.resolve()), "sha256": digest, "original": original, "scene": scene, "split": split})
    config = "train: images/train\nval: images/val\ntest: images/test\nnames:\n  0: product\n"
    (output / "dataset.yaml").write_text(config, encoding="utf-8")
    report = {"seed": seed, "source": str(source.resolve()), "license_declared": "CC BY 4.0", "attribution": "kickkung / Shelf detection for COCO format v2", "source_url": "https://universe.roboflow.com/kickkung/shelf-detection-for-coco-format/dataset/2", "grouping": "numeric filename prefix, conservative scene grouping; requires manual scene review", "evaluation_variant": "first eligible filename in lexical order; original untransformed version unknown", "counts": {k: dict(v) for k, v in counts.items()}, "excluded": dict(excluded), "scene_assignments": assignments, "manifest": manifest}
    (output / "manifest.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k not in {"manifest", "scene_assignments"}}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=ROOT / "MODELO/archive (1)")
    parser.add_argument("--output", type=Path, default=ROOT / "data/shelf_products_v2")
    args = parser.parse_args()
    prepare(args.source, args.output)
