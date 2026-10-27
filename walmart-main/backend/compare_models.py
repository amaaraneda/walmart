"""Compara detectores sobre el mismo test; no activa pesos automáticamente."""

import argparse
import hashlib
import json
from pathlib import Path

from ultralytics import YOLO


ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, default=ROOT / "artifacts/models/gondola-yolo26n.pt")
    parser.add_argument("--data", type=Path, default=ROOT / "artifacts/config/shelf-v2-cpu.yaml")
    parser.add_argument("--report", type=Path, default=ROOT / "artifacts/candidates/shelf-v2/comparison.json")
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--split", choices=("val", "test"), default="val")
    args = parser.parse_args()
    report = {"imgsz": args.imgsz, "data": str(args.data.resolve()), "split": args.split, "note": "Detección de productos; no valida porcentaje de ocupación ni alertas de stock."}
    for key, path in (("baseline", args.baseline), ("candidate", args.candidate)):
        model = YOLO(str(path))
        if model.names != {0: "product"}:
            raise ValueError(f"Clases incompatibles: {model.names}")
        metrics = model.val(data=str(args.data.resolve()), split=args.split, imgsz=args.imgsz, device="cpu", workers=0, batch=4, max_det=1000, project=str(ROOT / "artifacts/runs"), name=f"compare-{args.split}-{key}", plots=False)
        report[key] = {"weights": str(path.resolve()), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "map50": float(metrics.box.map50), "map50_95": float(metrics.box.map), "precision": float(metrics.box.mp), "recall": float(metrics.box.mr), "speed_ms": metrics.speed}
        print(key, json.dumps(report[key]), flush=True)
    report["candidate_better_map50_95"] = report["candidate"]["map50_95"] > report["baseline"]["map50_95"]
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
