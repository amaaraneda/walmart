"""API y web del prototipo. No expone un sistema de autenticación de producción."""

from io import BytesIO
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from PIL import Image, ImageDraw, ImageOps, UnidentifiedImageError

from .model import COMPANION_WEIGHTS, VOID_CANDIDATE_WEIGHTS, Detector
from .visual_occupancy import estimate_visual_occupancy


ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"
MAX_BYTES = 12 * 1024 * 1024
detector = Detector()
companion_detector = Detector(COMPANION_WEIGHTS)
void_candidate_detector = Detector(VOID_CANDIDATE_WEIGHTS, class_name="void", imgsz=512)
app = FastAPI(title="Góndola Visión MVP", version="0.1.0")


def model_options():
    return [
        {"id": "companero", "label": "Detector de productos · Principal", "available": companion_detector.ready, "validation": companion_detector.metadata},
        {"id": "principal", "label": "Detector de productos · Comparativo (YOLO26n)", "available": detector.ready, "validation": detector.metadata},
    ]


@app.get("/api/health")
def health():
    return {
        "status": "experimental" if companion_detector.ready else "needs_training",
        "model": "Detector de productos · Principal",
        "weights_loaded": companion_detector.ready,
        "gap_model_status": "candidate_not_validated_on_project_images",
        "occupancy_status": "experimental_frontage_estimate_requires_review",
        "void_candidate_available": void_candidate_detector.ready,
        "validation": companion_detector.metadata if companion_detector.ready else {},
        "models": model_options(),
    }


@app.post("/api/analyze")
async def analyze(
    image: UploadFile = File(...),
    threshold: float = Form(30),
    model_id: str = Form("companero"),
    include_void_candidates: bool = Form(False),
):
    if model_id not in {"principal", "companero"}:
        raise HTTPException(422, "Modelo no reconocido")
    selected_detector = detector if model_id == "principal" else companion_detector
    if not selected_detector.ready:
        raise HTTPException(503, f"Faltan los pesos del modelo {model_id} en artifacts/models.")
    if include_void_candidates and not void_candidate_detector.ready:
        raise HTTPException(503, "El detector experimental de huecos aún no está disponible")
    if not 0 < threshold <= 100:
        raise HTTPException(422, "Umbral inválido")
    if image.content_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise HTTPException(415, "Solo se admiten JPG, PNG o WebP")
    content = await image.read(MAX_BYTES + 1)
    if len(content) > MAX_BYTES:
        raise HTTPException(413, "Imagen demasiado grande (máximo 12 MB)")
    try:
        source = ImageOps.exif_transpose(Image.open(BytesIO(content))).convert("RGB")
        source.load()
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise HTTPException(422, "No se pudo abrir la imagen") from exc
    if max(source.size) > 8000 or min(source.size) < 64:
        raise HTTPException(422, "Resolución fuera de rango (64–8000 px)")
    try:
        boxes = selected_detector.predict(source)
        void_candidates = void_candidate_detector.predict(source) if include_void_candidates else []
        occupancy = estimate_visual_occupancy(boxes, source.width, source.height,
                                              void_candidates if include_void_candidates else None)
    except Exception as exc:
        raise HTTPException(500, f"Error del detector: {type(exc).__name__}") from exc
    # Las fotos del proyecto describen productos, no el área útil ni huecos reales.
    # El detector de huecos externo sólo genera candidatos para revisión.
    annotated = source.copy()
    draw = ImageDraw.Draw(annotated)
    line_width = max(2, round(source.width / 700))
    high_confidence = 0
    for box in boxes:
        if box.confidence >= .5:
            high_confidence += 1
        draw.rectangle((box.x1, box.y1, box.x2, box.y2), outline="#26bd8d" if box.confidence >= .5 else "#e6a828", width=line_width)
    for box in void_candidates:
        draw.rectangle((box.x1, box.y1, box.x2, box.y2), outline="#e03845", width=line_width + 1)
    for shelf in occupancy["shelves"]:
        region = shelf["region"]
        draw.rectangle((region["left"], region["top"], region["right"], region["bottom"]),
                       outline="#1186ce", width=line_width + 2)
        draw.text((region["left"] + 5, region["top"] + 5),
                  f"Nivel {shelf['id']}: {shelf['occupancy_percent']:.1f}% estimado",
                  fill="#ffffff", stroke_width=2, stroke_fill="#0b4264")
    buffer = BytesIO()
    annotated.save(buffer, format="JPEG", quality=82)
    import base64

    return {
        "image_size": {"width": source.width, "height": source.height},
        "occupancy_percent": occupancy["occupancy_percent"],
        "empty_percent": round(100 - occupancy["occupancy_percent"], 1) if occupancy["occupancy_percent"] is not None else None,
        "empty_regions": [],
        "shelves": occupancy["shelves"],
        "threshold_percent": threshold,
        "threshold_applied": False,
        "low_stock_alert": None,
        "low_stock_candidate": any(shelf["occupancy_percent"] < threshold for shelf in occupancy["shelves"]),
        "detections": len(boxes),
        "visible_detections": len(boxes),
        "high_confidence_detections": high_confidence,
        "product_detections": [{"left": round(box.x1), "top": round(box.y1), "right": round(box.x2), "bottom": round(box.y2), "confidence": round(box.confidence, 3)} for box in boxes],
        "void_candidate_detections": len(void_candidates),
        "void_candidate_requested": include_void_candidates,
        "void_candidate_regions": [{"left": round(box.x1), "top": round(box.y1), "right": round(box.x2), "bottom": round(box.y2), "confidence": round(box.confidence, 3)} for box in void_candidates],
        "review_required": True,
        "method": occupancy["reason"],
        "empty_region_method": "complement_of_product_frontage_projection" if occupancy["shelves"] else None,
        "model_id": model_id,
        "model": "Detector de productos · Comparativo (YOLO26n)" if model_id == "principal" else "Detector de productos · Principal",
        "validation": selected_detector.metadata,
        "annotated_image": "data:image/jpeg;base64," + base64.b64encode(buffer.getvalue()).decode("ascii"),
        "note": "El porcentaje es una estimación de la anchura visible ocupada por productos en niveles detectados automáticamente; no mide unidades ni inventario. Puede fallar por productos omitidos o límites de góndola incorrectos. Las cajas rojas son propuestas independientes. La alerta operativa del 30 % permanece desactivada hasta validar la estimación con fotografías etiquetadas.",
    }


@app.get("/")
def index():
    return FileResponse(FRONTEND / "index.html")


@app.get("/{filename}")
def static_file(filename: str):
    if filename not in {"app.js", "styles.css", "favicon.svg"}:
        raise HTTPException(404)
    return FileResponse(FRONTEND / filename)
