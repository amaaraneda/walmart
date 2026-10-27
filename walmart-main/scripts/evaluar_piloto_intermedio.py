"""Genera evidencias reproducibles del piloto; no calcula exactitud sin etiquetas."""

from __future__ import annotations

import base64
import json
import time
from pathlib import Path

from fastapi.testclient import TestClient
from PIL import Image, ImageDraw, ImageOps

from backend.app import app


ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / "data/stock_ground_truth_v1/images"
OUT = ROOT / "artifacts/diagnostics/informe-intermedio"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    client = TestClient(app)
    cases = []
    for path in sorted(IMAGES.glob("supermarket_*.jpg")):
        if path.stem == "supermarket_035":  # duplicado exacto de 004
            continue
        start = time.perf_counter()
        with path.open("rb") as stream:
            response = client.post("/api/analyze", files={"image": (path.name, stream, "image/jpeg")})
        seconds = time.perf_counter() - start
        row = {"image": path.name, "http_status": response.status_code,
               "elapsed_seconds": round(seconds, 3)}
        if response.status_code == 200:
            result = response.json()
            (OUT / path.name).write_bytes(base64.b64decode(result.pop("annotated_image").split(",", 1)[1]))
            row.update({"detections": result["detections"],
                        "occupancy_percent": result["occupancy_percent"],
                        "shelf_percentages": [s["occupancy_percent"] for s in result["shelves"]],
                        "low_stock_candidate": result["low_stock_candidate"],
                        "low_stock_alert": result["low_stock_alert"],
                        "method": result["method"]})
        else:
            row["error"] = response.text[:300]
        cases.append(row)
        print(json.dumps(row, ensure_ascii=False), flush=True)
    (OUT / "resultados.json").write_text(json.dumps(cases, indent=2, ensure_ascii=False), encoding="utf-8")
    for page_start in range(0, len(cases), 12):
        sheet = Image.new("RGB", (1600, 1200), "#f2f5f8")
        draw = ImageDraw.Draw(sheet)
        for offset, row in enumerate(cases[page_start:page_start + 12]):
            path = OUT / row["image"]
            if not path.exists():
                continue
            with Image.open(path) as source:
                preview = ImageOps.contain(source.convert("RGB"), (380, 340))
            x = (offset % 4) * 400 + (400 - preview.width) // 2
            y = (offset // 4) * 400 + 30
            sheet.paste(preview, (x, y))
            draw.text((x, (offset // 4) * 400 + 370),
                      f"{row['image']}  {row.get('occupancy_percent')}% / {len(row.get('shelf_percentages', []))} niveles",
                      fill="#102f47")
        sheet.save(OUT / f"contacto_{page_start // 12 + 1:02d}.jpg", quality=85)


if __name__ == "__main__":
    main()
