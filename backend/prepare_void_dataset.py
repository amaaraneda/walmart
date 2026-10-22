"""Reparte las fotos de huecos por escena original, nunca por aumento Roboflow.

El dataset de origen indica licencia Private: la salida es sólo para uso local.
"""

import argparse
import json
import random
import shutil
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "DATASETS/Espacios vacios/archive/void detection on retail shelves"
OUTPUT = ROOT / "data/processed/void_detection_v1"


def scene_id(path: Path) -> str:
    if "_jpg.rf." not in path.stem:
        raise ValueError(f"Nombre sin identificador de escena Roboflow: {path.name}")
    return path.stem.split("_jpg.rf.", 1)[0]


def collect(source: Path) -> dict[str, list[tuple[Path, Path]]]:
    groups = defaultdict(list)
    for original_split in ("train", "valid", "test"):
        for image in sorted((source / original_split / "images").glob("*.jpg")):
            label = source / original_split / "labels" / f"{image.stem}.txt"
            if not label.is_file():
                raise ValueError(f"Falta etiqueta: {image}")
            for line in label.read_text(encoding="utf-8").splitlines():
                parts = line.split()
                if len(parts) != 5 or parts[0] != "0" or any(not 0 <= float(value) <= 1 for value in parts[1:]):
                    raise ValueError(f"Etiqueta inválida: {label}")
            groups[scene_id(image)].append((image, label))
    if not groups:
        raise ValueError("No hay fotografías en el dataset")
    return dict(groups)


def assign(groups: dict, seed: int = 20261021) -> dict[str, str]:
    scenes = sorted(groups)
    random.Random(seed).shuffle(scenes)
    n_test = max(1, round(len(scenes) * .15))
    n_val = max(1, round(len(scenes) * .15))
    return {scene: ("test" if index < n_test else "val" if index < n_test + n_val else "train") for index, scene in enumerate(scenes)}


def prepare(source: Path = SOURCE, output: Path = OUTPUT) -> dict:
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"La salida ya contiene archivos: {output}")
    groups = collect(source)
    mapping = assign(groups)
    counts = {split: {"scenes": 0, "images": 0, "boxes": 0} for split in ("train", "val", "test")}
    output.mkdir(parents=True, exist_ok=True)
    for scene, entries in groups.items():
        split = mapping[scene]
        counts[split]["scenes"] += 1
        for image, label in entries:
            image_target = output / "images" / split / image.name
            label_target = output / "labels" / split / label.name
            image_target.parent.mkdir(parents=True, exist_ok=True)
            label_target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(image, image_target)
            shutil.copy2(label, label_target)
            counts[split]["images"] += 1
            counts[split]["boxes"] += len(label.read_text(encoding="utf-8").splitlines())
    (output / "dataset.yaml").write_text(
        f"path: {output.resolve().as_posix()}\ntrain: images/train\nval: images/val\ntest: images/test\nnames:\n  0: void\n",
        encoding="utf-8",
    )
    report = {"source": str(source), "source_license": "Private (según data.yaml del origen)", "seed": 20261021,
              "split_unit": "original_scene_before_augmentation", "counts": counts,
              "limitation": "Las cajas de hueco no incluyen máscara de área útil ni stock porcentual."}
    (output / "manifest.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    print(json.dumps(prepare(args.source, args.output), indent=2, ensure_ascii=False))
