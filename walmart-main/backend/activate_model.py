"""Activa un candidato evaluado y conserva el modelo anterior para revertir."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", type=Path, default=ROOT / "artifacts/candidates/shelf-v2/gondola-yolo26n.pt")
    parser.add_argument("--comparison", type=Path, default=ROOT / "artifacts/candidates/shelf-v2/comparison.json")
    parser.add_argument("--test-comparison", type=Path, required=True)
    args = parser.parse_args()
    comparison = json.loads(args.comparison.read_text(encoding="utf-8"))
    candidate = args.candidate.resolve()
    if comparison.get("split") != "val":
        raise ValueError("La decisión de activación debe usar el conjunto de validación")
    if Path(comparison["candidate"]["weights"]).resolve() != candidate:
        raise ValueError("El informe corresponde a otro candidato")
    if comparison["candidate"]["map50_95"] <= comparison["baseline"]["map50_95"]:
        raise ValueError("El candidato no supera la línea base en mAP50–95")
    active = ROOT / "artifacts/models/gondola-yolo26n.pt"
    if Path(comparison["baseline"]["weights"]).resolve() != active.resolve():
        raise ValueError("La comparación no corresponde al modelo activo")
    for key, path in (("candidate", candidate), ("baseline", active)):
        expected = comparison[key].get("sha256")
        if not expected or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f"Los pesos de {key} cambiaron desde la comparación")
    report = json.loads((candidate.parent / "metadata.json").read_text(encoding="utf-8"))
    test_report = json.loads(args.test_comparison.read_text(encoding="utf-8"))
    if test_report.get("split") != "test":
        raise ValueError("El segundo informe debe corresponder a prueba")
    for key in ("candidate", "baseline"):
        if test_report[key].get("sha256") != comparison[key]["sha256"]:
            raise ValueError("Las comparaciones usan checkpoints distintos")
    if test_report["candidate"]["map50_95"] <= test_report["baseline"]["map50_95"]:
        raise ValueError("El candidato no supera la línea base en las escenas de prueba")
    from ultralytics import YOLO

    if YOLO(str(candidate)).names != {0: "product"}:
        raise ValueError("El candidato no usa la clase product")
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    backup = ROOT / "artifacts/backups" / timestamp
    backup.mkdir(parents=True)
    for filename in ("gondola-yolo26n.pt", "metadata.json"):
        source = active.parent / filename
        if source.exists():
            shutil.copy2(source, backup / filename)
    report.update(imgsz=comparison["imgsz"], val_map50=round(comparison["candidate"]["map50"], 4), val_map50_95=round(comparison["candidate"]["map50_95"], 4), val_precision=round(comparison["candidate"]["precision"], 4), val_recall=round(comparison["candidate"]["recall"], 4), validation_comparison=comparison, activated_at_utc=timestamp, previous_model_backup=str(backup), sha256=hashlib.sha256(candidate.read_bytes()).hexdigest())
    report.update(test_map50=round(test_report["candidate"]["map50"], 4), test_map50_95=round(test_report["candidate"]["map50_95"], 4), test_precision=round(test_report["candidate"]["precision"], 4), test_recall=round(test_report["candidate"]["recall"], 4), test_comparison=test_report)
    active.parent.mkdir(parents=True, exist_ok=True)
    staged = active.with_suffix(".pt.new")
    shutil.copy2(candidate, staged)
    staged.replace(active)
    (active.parent / "metadata.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Activado: {active}\nRespaldo anterior: {backup}\nReinicia la API para cargar los nuevos pesos.")


if __name__ == "__main__":
    main()
