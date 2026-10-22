"""Entrenamiento reproducible sobre el dataset estandarizado local."""

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/standardized_yolo_v1"
OUTPUT = ROOT / "artifacts/models/gondola-yolo26n.pt"
PRETRAINED = ROOT / "artifacts/pretrained/yolo26n.pt"


def preflight(data):
    if not (data / "dataset.yaml").is_file():
        raise FileNotFoundError(f"Falta {data / 'dataset.yaml'}")
    import yaml

    names = yaml.safe_load((data / "dataset.yaml").read_text(encoding="utf-8")).get("names")
    if names not in ({0: "product"}, ["product"]):
        raise ValueError("El dataset debe estar estandarizado a una clase product")
    for split in ("train", "val", "test"):
        images = list((data / "images" / split).glob("*.jpg")) + list((data / "images" / split).glob("*.png")) + list((data / "images" / split).glob("*.jpeg"))
        if not images or any(not (data / "labels" / split / (p.stem + ".txt")).is_file() for p in images):
            raise ValueError(f"Split {split}: faltan imágenes o etiquetas")


def main():
    parser = argparse.ArgumentParser(description="Fine-tuning de YOLO26n para productos en góndola")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=4)
    parser.add_argument("--device", default=None, help="cpu, 0 (GPU) o vacío para autodetectar")
    parser.add_argument("--data", type=Path, default=DATA)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--name", default="yolo26n-products")
    parser.add_argument("--workers", type=int, default=0)
    parser.add_argument("--freeze", type=int, default=0)
    parser.add_argument("--initial-weights", type=Path, default=PRETRAINED)
    parser.add_argument("--lr0", type=float, default=0.001)
    parser.add_argument("--patience", type=int, default=20)
    parser.add_argument("--evaluation-split", choices=("val", "test"), default="val")
    args = parser.parse_args()
    data = args.data.resolve()
    preflight(data)
    from ultralytics import YOLO

    initial_weights = args.initial_weights.resolve()
    if not initial_weights.is_file():
        raise FileNotFoundError(f"Faltan los pesos iniciales: {initial_weights}")
    runtime_yaml = ROOT / "artifacts/config" / f"{args.name}.yaml"
    runtime_yaml.parent.mkdir(parents=True, exist_ok=True)
    runtime_yaml.write_text(
        f"path: {data.as_posix()}\ntrain: images/train\nval: images/val\ntest: images/test\nnames:\n  0: product\n",
        encoding="utf-8",
    )
    model = YOLO(str(initial_weights))
    model.train(
        data=str(runtime_yaml),
        epochs=args.epochs,
        imgsz=args.imgsz,
        max_det=1000,
        batch=args.batch,
        workers=args.workers,
        freeze=args.freeze,
        device=args.device,
        patience=args.patience,
        optimizer="AdamW",
        lr0=args.lr0,
        mosaic=0.5,
        mixup=0.0,
        copy_paste=0.0,
        seed=20260912,
        project=str(ROOT / "artifacts/runs"),
        name=args.name,
    )
    best = Path(model.trainer.save_dir) / "weights/best.pt"
    if not best.is_file():
        raise FileNotFoundError(f"Entrenamiento terminado sin checkpoint: {best}")
    # Evaluar primero: no publicar un checkpoint sin su evaluación terminada.
    metrics = YOLO(str(best)).val(
        data=str(runtime_yaml),
        split=args.evaluation_split,
        imgsz=args.imgsz,
        max_det=1000,
        project=str(ROOT / "artifacts/runs"),
        name=f"{args.name}-{args.evaluation_split}",
        device=args.device,
        workers=args.workers,
        batch=args.batch,
    )
    report = {
        "model": "YOLO26n",
        "dataset": data.name,
        "epochs": args.epochs,
        "imgsz": args.imgsz,
        "evaluation_split": args.evaluation_split,
        "evaluation_map50": round(float(metrics.box.map50), 4),
        "evaluation_map50_95": round(float(metrics.box.map), 4),
        "initial_weights": str(initial_weights),
        "freeze": args.freeze,
        "lr0": args.lr0,
        "trained_at_utc": datetime.now(timezone.utc).isoformat(),
        "validation_status": "preliminary_detection_only",
        "run": str(model.trainer.save_dir),
        "weights": str(best),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(best, args.output)
    (args.output.parent / "metadata.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Checkpoint listo: {args.output}")
    print(f"{args.evaluation_split} mAP50={metrics.box.map50:.4f}, mAP50-95={metrics.box.map:.4f}")


if __name__ == "__main__":
    main()
