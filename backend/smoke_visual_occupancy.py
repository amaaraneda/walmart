"""Exercise the API locally and save its annotated preview for visual QA."""

from __future__ import annotations

import base64
import json
import sys
from pathlib import Path

from fastapi.testclient import TestClient

from .app import app


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "artifacts" / "diagnostics" / "visual-occupancy"


def main(paths):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    client = TestClient(app)
    for name in paths:
        path = Path(name)
        mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
        with path.open("rb") as file:
            response = client.post("/api/analyze", files={"image": (path.name, file, mime)})
        response.raise_for_status()
        data = response.json()
        encoded = data.pop("annotated_image").split(",", 1)[1]
        (OUTPUT / f"{path.stem}.jpg").write_bytes(base64.b64decode(encoded))
        summary = {"image": path.name, "occupancy_percent": data["occupancy_percent"],
                   "shelves": [{"id": s["id"], "occupancy_percent": s["occupancy_percent"],
                                "region": s["region"]} for s in data["shelves"]],
                   "low_stock_candidate": data["low_stock_candidate"],
                   "low_stock_alert": data["low_stock_alert"], "method": data["method"]}
        print(json.dumps(summary, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
