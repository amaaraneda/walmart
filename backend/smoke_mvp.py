"""Prueba HTTP real de página, modelo y análisis; guarda evidencia local."""

import argparse
import base64
import json
from pathlib import Path
import statistics
import time

import requests


ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8000")
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/smoke_products_only")
    parser.add_argument("--image", type=Path, help="Prueba una fotografía concreta en vez de la selección por defecto")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    health = session.get(args.url + "/api/health", timeout=15)
    health.raise_for_status()
    assert health.json()["weights_loaded"], "El modelo no está disponible"
    for asset in ("/", "/app.js", "/styles.css"):
        session.get(args.url + asset, timeout=15).raise_for_status()
    images = [args.image] if args.image else sorted((ROOT / "data/shelf_products_v2/images/test").glob("*.jpg"))[:3] + sorted((ROOT / "data/standardized_yolo_v1/images/test").glob("*.jpg"))[:3]
    if not images:
        raise ValueError("Faltan imágenes para probar")
    rows = []
    for i, image in enumerate(images):
        started = time.perf_counter()
        with image.open("rb") as stream:
            response = session.post(args.url + "/api/analyze", files={"image": (image.name, stream, "image/jpeg")}, data={"threshold": 30}, timeout=60)
        elapsed = time.perf_counter() - started
        response.raise_for_status()
        result = response.json()
        assert result["occupancy_percent"] is None
        assert result["low_stock_alert"] is None
        assert not result["threshold_applied"]
        (args.output / f"analysis_{i + 1}.jpg").write_bytes(base64.b64decode(result["annotated_image"].split(",", 1)[1]))
        rows.append({"image": str(image), "seconds": round(elapsed, 3), **{k: result[k] for k in ("detections", "visible_detections", "high_confidence_detections", "occupancy_percent", "low_stock_alert", "review_required")}})
    report = {"health": health.json(), "scope": "HTTP local, fotografías completas; verifica detección de productos y que no se emitan alertas no validadas", "results": rows, "median_seconds": round(statistics.median(r["seconds"] for r in rows), 3), "max_seconds": max(r["seconds"] for r in rows)}
    (args.output / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "health"}, indent=2))


if __name__ == "__main__":
    main()
