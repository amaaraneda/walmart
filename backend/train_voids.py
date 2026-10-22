"""Entrena un detector de huecos candidato; no activa alarmas automáticamente."""

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=ROOT / "data/processed/void_detection_v1/dataset.yaml")
    parser.add_argument("--initial", type=Path, default=ROOT / "artifacts/pretrained/yolo26n.pt")
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=4)
    parser.add_argument("--device", default="cpu")
    args = parser.parse_args()
    if not args.data.is_file() or not args.initial.is_file():
        raise FileNotFoundError("Falta dataset preparado o checkpoint inicial")
    from ultralytics import YOLO

    model = YOLO(str(args.initial))
    model.train(data=str(args.data), epochs=args.epochs, imgsz=args.imgsz, batch=args.batch,
                workers=0, device=args.device, seed=20261021, patience=8,
                project=str(ROOT / "artifacts/runs"), name="void-detection-v1", plots=False)
    best = Path(model.trainer.save_dir) / "weights/best.pt"
    if not best.is_file():
        raise FileNotFoundError(f"No se generó checkpoint: {best}")
    metrics = YOLO(str(best)).val(data=str(args.data), split="test", imgsz=args.imgsz,
                                  batch=args.batch, workers=0, device=args.device, plots=False,
                                  project=str(ROOT / "artifacts/runs"), name="void-detection-v1-test")
    report = {"weights": str(best), "dataset": str(args.data), "test_map50": float(metrics.box.map50),
              "test_map50_95": float(metrics.box.map), "test_precision": float(metrics.box.mp),
              "test_recall": float(metrics.box.mr), "trained_at_utc": datetime.now(timezone.utc).isoformat(),
              "status": "candidate_not_validated_on_project_images",
              "warning": "No mide ocupación ni valida alarma de stock bajo 30 %."}
    (best.parent.parent / "evaluation.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    candidate = ROOT / "artifacts/models/void-yolo26n-candidate.pt"
    candidate.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(best, candidate)
    print(f"Candidato local para revisión: {candidate}")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
