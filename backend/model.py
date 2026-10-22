"""Carga diferida del detector entrenado; nunca usa COCO como sustituto silencioso."""

import os
import json
from pathlib import Path
from threading import Lock

from .coverage import Box


DEFAULT_WEIGHTS = Path(__file__).resolve().parents[1] / "artifacts/models/gondola-yolo26n.pt"
COMPANION_WEIGHTS = Path(__file__).resolve().parents[1] / "artifacts/models/companero-yolo.pt"
VOID_CANDIDATE_WEIGHTS = Path(__file__).resolve().parents[1] / "artifacts/models/void-yolo26n-candidate.pt"


class Detector:
    def __init__(self, weights: Path | None = None, *, class_name: str = "product", imgsz: int = 640):
        self.weights = weights or Path(os.getenv("GONDOLA_WEIGHTS", DEFAULT_WEIGHTS))
        self.class_name = class_name
        self.imgsz = imgsz
        self._model = None
        self._lock = Lock()

    @property
    def ready(self) -> bool:
        return self.weights.is_file()

    @property
    def metadata(self) -> dict:
        report = self.weights.parent / ("companion_metadata.json" if self.weights == COMPANION_WEIGHTS else "metadata.json")
        if not report.is_file():
            return {}
        try:
            return json.loads(report.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {}

    def predict(self, image):
        if not self.ready:
            raise FileNotFoundError(f"No se encontró el modelo entrenado: {self.weights}")
        with self._lock:
            if self._model is None:
                from ultralytics import YOLO

                self._model = YOLO(str(self.weights))
                names = {int(index): str(name).strip().lower() for index, name in self._model.names.items()}
                if names != {0: self.class_name}:
                    raise ValueError(f"El checkpoint debe detectar únicamente la clase '{self.class_name}'")
            result = self._model.predict(image, conf=0.25, imgsz=self.imgsz, max_det=1000, verbose=False)[0]
        return [Box(*row[:4], row[4]) for row in result.boxes.data.cpu().tolist() if int(row[5]) == 0]
