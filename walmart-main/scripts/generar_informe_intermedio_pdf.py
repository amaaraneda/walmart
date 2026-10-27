"""Compone el informe PDF a partir de evidencia local sin publicar fotos en Git."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, Image, KeepTogether, PageBreak, PageTemplate,
    Paragraph, Spacer, Table, TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "artifacts/diagnostics/informe-intermedio"
INPUT = ROOT / "data/stock_ground_truth_v1/images"
OUT = ROOT / "outputs/informe_intermedio/Informe_Intermedio_Walmart_2026-10-21.pdf"

BEST = [
    ("003", "Tres niveles propuestos en un frente de envases alineados; cobertura alta visualmente plausible.", "Confirmar manualmente límites y cobertura por nivel."),
    ("004", "Frente denso de latas; cajas y dos niveles interpretables.", "Verificar si faltan niveles fuera de los propuestos."),
    ("006", "Cinco niveles reconocibles en bandejas de fruta.", "Reflejos del refrigerador pueden alterar cajas."),
    ("010", "Cuatro niveles de bolsas con cobertura frontal aparentemente alta.", "No prueba ausencia de huecos pequeños."),
    ("013", "Filas alineadas de cartones y botellas; salida coherente a simple vista.", "Etiquetas de precio y reflejos pueden confundir."),
    ("015", "Cinco niveles en lácteos, ocupación visual alta aparente.", "Vitrina y productos detrás del frente visible."),
    ("017", "Cinco niveles reconocibles en cajas de cereal.", "Algunas uniones horizontales pueden saturarse."),
    ("018", "Tres niveles de productos refrigerados y cajas visibles.", "Requiere comparación con referencia humana."),
    ("025", "Ocho niveles propuestos en latas apiladas.", "Validar que los ocho sean rieles reales."),
    ("027", "Cuatro filas densas de latas; indicador alto plausible.", "Cajas contiguas pueden sobreestimar el ancho cubierto."),
]

WORST = [
    ("001", "No evaluable pese a exhibición densa.", "El agrupamiento no estabiliza bases de niveles; probar geometría de estante independiente."),
    ("002", "916 detecciones y ningún nivel medible.", "Repetición y solapamiento de cajas; deduplicar y estimar rieles por separado."),
    ("011", "Estante pequeño rodeado de pared; ancho no observable.", "Protocolo de encuadre o detector de región de góndola."),
    ("012", "Latas apiladas sin niveles aceptados.", "Revisar agrupamiento de bases repetitivas."),
    ("020", "Porcentaje emitido con vitrina distante y ocluida.", "Clasificar escena no apta antes de medir; controlar reflejos."),
    ("021", "Hueco visible en cereales; promedio global permanece alto.", "Comparar cada nivel con máscaras humanas; no decidir con promedio."),
    ("022", "Huecos parciales; detector opcional de vacíos omitió todos.", "Añadir positivos locales y revisar geometría para envases de distintas alturas."),
    ("023", "Fruta muy densa sin porcentaje.", "Cajas superpuestas y patrón irregular; explorar segmentación/riel."),
    ("033", "Varios niveles de verdura, pero sólo uno medido.", "Verificar recuento de niveles y evitar ocultar exclusiones."),
    ("036", "Nivel inferior escaso; promedio global alto.", "Priorizar mínimo por nivel y revisión humana de cinco huecos propuestos."),
]


def fit_image(path: Path, max_w: float, max_h: float) -> Image:
    cache = EVIDENCE / "pdf-cache"
    cache.mkdir(parents=True, exist_ok=True)
    label = "entrada" if path.parent == INPUT else "salida"
    compact = cache / f"{label}_{path.stem}.jpg"
    with PILImage.open(path) as im:
        rgb = im.convert("RGB")
        rgb.thumbnail((1200, 1500))
        rgb.save(compact, "JPEG", quality=78, optimize=True)
        w, h = rgb.size
    scale = min(max_w / w, max_h / h)
    return Image(str(compact), width=w * scale, height=h * scale)


def page_header(canvas, doc):
    canvas.saveState()
    canvas.setFont("Arial", 8)
    canvas.setFillColor(colors.HexColor("#506578"))
    canvas.drawString(17 * mm, 282 * mm, "Walmart Computer Vision  |  Informe intermedio  |  21.10.2026")
    canvas.drawRightString(193 * mm, 12 * mm, str(doc.page))
    canvas.restoreState()


def main():
    pdfmetrics.registerFont(TTFont("Arial", r"C:\Windows\Fonts\arial.ttf"))
    pdfmetrics.registerFont(TTFont("Arial-Bold", r"C:\Windows\Fonts\arialbd.ttf"))
    pdfmetrics.registerFontFamily("Arial", normal="Arial", bold="Arial-Bold")
    rows = {x["image"]: x for x in json.loads((EVIDENCE / "resultados.json").read_text(encoding="utf-8"))}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = BaseDocTemplate(str(OUT), pagesize=A4, leftMargin=17 * mm,
                          rightMargin=17 * mm, topMargin=21 * mm, bottomMargin=20 * mm)
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="main")
    doc.addPageTemplates(PageTemplate(id="report", frames=[frame], onPage=page_header))
    s = getSampleStyleSheet()
    s.add(ParagraphStyle(name="TitleX", fontName="Arial-Bold", fontSize=20, leading=25,
                         textColor=colors.HexColor("#102f47"), spaceAfter=12))
    s.add(ParagraphStyle(name="HeadingX", fontName="Arial-Bold", fontSize=12, leading=16,
                         textColor=colors.HexColor("#102f47"), spaceBefore=12, spaceAfter=7))
    s.add(ParagraphStyle(name="BodyX", fontName="Arial", fontSize=9.2, leading=13.5,
                         spaceAfter=7, alignment=TA_LEFT))
    s.add(ParagraphStyle(name="SmallX", fontName="Arial", fontSize=8, leading=11,
                         textColor=colors.HexColor("#425365"), spaceAfter=5))
    s.add(ParagraphStyle(name="CaptionX", fontName="Arial-Bold", fontSize=8, leading=11,
                         textColor=colors.HexColor("#234a65"), alignment=TA_CENTER))
    story = []
    P = lambda text, style="BodyX": Paragraph(text, s[style])
    story += [Spacer(1, 20 * mm), P("Informe intermedio de avance del proyecto", "TitleX"),
              P("Walmart Computer Vision", "HeadingX"),
              P("Corte de información: 21 de octubre de 2026. MVP beta.", "SmallX"),
              Spacer(1, 8 * mm), P("Resultado principal", "HeadingX"),
              P("La aplicación ya analiza fotografías de góndolas, detecta productos y calcula una cobertura frontal experimental por nivel. Todavía no mide stock físico ni envía alertas operativas. Para activar el aviso bajo 30 % faltan etiquetas humanas de ocupación, evaluación de errores y validación en el equipo de destino."),
              P("En 44 escenas únicas del piloto, la API respondió en todas, entregó un porcentaje en 39 y declaró 5 no evaluables. Esta tasa de salida numérica (88,6 %) no es precisión. Ningún nivel quedó bajo 30 % en este barrido. El test de detección de productos de 30 imágenes dio mAP50 de 0,8200 para el modelo predeterminado, pero no mide acierto de stock."),
              P("Alcance de este informe", "HeadingX"),
              P("Estado de módulos, planificación propuesta, arquitectura, reproducibilidad, 10 casos favorables y 10 problemáticos, riesgos y plan de mejora. Las fotografías originales y las previsualizaciones son evidencia local; sus permisos de publicación deben aclararse antes de subirlas a un repositorio público."),
              PageBreak()]
    story += [P("1  Estado actual y planificación", "TitleX")]
    mod = [
        ["Módulo", "Estado / avance estimado", "Principal pendiente"],
        ["Web", "Beta / 75 %", "Pruebas de uso y PC Duoc"],
        ["API e inferencia", "Beta / 80 %", "Carga y hardware final"],
        ["Detección de productos", "Experimental / 70 %", "Generalización fuera de pocas escenas"],
        ["Ocupación por nivel", "Experimental / 40 %", "Error frente a etiquetas humanas"],
        ["Huecos", "Candidato / 25 %", "Omisiones y falsos positivos"],
        ["Alerta 30 %", "Pendiente / 10 %", "No activada sin validación"],
        ["Login y CRUD", "Demo local / 25 %", "Auth y base de datos reales"],
        ["Docker y docs", "Beta / 60 %", "Reproducción externa"],
    ]
    t = Table([[P(str(c), "SmallX") for c in row] for row in mod], colWidths=[40*mm, 50*mm, 86*mm], repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), colors.HexColor("#dcebf5")),
                           ("GRID", (0,0), (-1,-1), 0.25, colors.HexColor("#cbd5dd")),
                           ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
                           ("LEFTPADDING", (0,0), (-1,-1), 6), ("RIGHTPADDING", (0,0), (-1,-1), 6),
                           ("TOPPADDING", (0,0), (-1,-1), 6), ("BOTTOMPADDING", (0,0), (-1,-1), 6)]))
    story += [P("Porcentajes de avance de ingeniería, no tasas de rendimiento. Se basan en funciones operativas versus trabajo pendiente para el MVP.", "SmallX"), t,
              P("Carta Gantt propuesta", "HeadingX"),
              P("21 oct: flujo foto-API-detección cumplido en beta. 23 oct: seis escenas con ROI y huecos revisados. 26 oct: error de ocupación y matriz de alertas. 28 oct: iteración del estimador y test congelado. 30 oct: autenticación/persistencia y prueba en PC Duoc. Los responsables nominales deben asignarse en reunión; no se calculan retrasos sin línea base confirmada de Fase 2."),
              P("Riesgos técnicos", "HeadingX"),
              P("El dataset de productos no etiqueta frente útil ni stock. La perspectiva, los reflejos, la oclusión, los envases de altura variable y el solapamiento de cajas afectan la estimación. La alarma sigue suspendida; cada resultado requiere revisión humana."),
              PageBreak()]
    story += [P("2  Solución técnica y evidencia", "TitleX"),
              P("Flujo: fotografía → FastAPI y validación de archivo → YOLO de producto → agrupación automática de niveles → unión de proyecciones horizontales → porcentaje experimental y salida anotada. Un detector adicional de huecos sólo propone cajas diagnósticas. La alerta y el historial persistente son trabajo pendiente."),
              P("YOLO se eligió para obtener cajas de producto comparables y rápidas; FastAPI separa inferencia e interfaz; Docker facilita ejecución reproducible. El porcentaje de frente ocupado evita equiparar conteo de productos con stock, pero no representa unidades ni profundidad. Login y CRUD actuales guardan estado en el navegador y no ofrecen seguridad multiusuario."),
              P("Datos y método", "HeadingX"),
              P("Piloto recibido: 60 fotos, 59 únicas tras quitar duplicado 004/035; 15 recortes y 45 escenas. Dataset de productos v2: 734 train, 29 val, 30 test, agrupado por escena. El barrido de este informe usa 44 escenas únicas y el modelo predeterminado con umbral de confianza 0,25. Resultados reproducibles: <font face='Arial-Bold'>artifacts/diagnostics/informe-intermedio/resultados.json</font>. No hay etiquetas humanas revisadas de porcentaje de stock."),
              P("Comprobación y límites", "HeadingX"),
              P("Tiempo mediano del barrido local con modelo cargado: aproximadamente 0,32 s; primera solicitud: 4,66 s. No equivalen a p95 ni al rendimiento del PC Duoc. El historial Git local visible no permite acreditar aportes individuales de todo el equipo. Los checkpoints y fotografías permanecen fuera de Git hasta aclarar acceso y licencias."),
              P("Las páginas siguientes muestran cada entrada junto a la salida real anotada. «Mejor» significa comportamiento visual aparente, no exactitud medida. «Peor» señala error, omisión o riesgo observable. El resultado esperado es preliminar y debe validarse por dos revisores."),
              PageBreak()]

    for kind, cases in (("Casos de mejor comportamiento aparente", BEST),
                        ("Casos problemáticos", WORST)):
        for idx, (case_id, assessment, action) in enumerate(cases, 1):
            name = f"supermarket_{case_id}.jpg"
            row = rows[name]
            status = "No evaluable" if row["occupancy_percent"] is None else f"{row['occupancy_percent']:.1f} % experimental"
            story += [P(f"{kind}  {idx}/10", "HeadingX"),
                      P(f"{name}  —  {status}", "TitleX"),
                      P(f"Detecciones: {row['detections']}; niveles propuestos: {len(row['shelf_percentages'])}; alerta operativa: ninguna.", "SmallX")]
            original = fit_image(INPUT / name, 82*mm, 135*mm)
            result = fit_image(EVIDENCE / name, 82*mm, 135*mm)
            pictures = Table([[original, result], [P("Entrada original", "CaptionX"), P("Resultado de la aplicación", "CaptionX")]],
                             colWidths=[88*mm, 88*mm])
            pictures.setStyle(TableStyle([("VALIGN", (0,0), (-1,-1), "MIDDLE"),
                                          ("ALIGN", (0,0), (-1,-1), "CENTER"),
                                          ("BOTTOMPADDING", (0,0), (-1,0), 6)]))
            story += [pictures, Spacer(1, 5*mm),
                      P(("Por qué se considera favorable: " if kind.startswith("Casos de mejor") else "Error o dificultad: ") + assessment),
                      P(("Criterio pendiente: " if kind.startswith("Casos de mejor") else "Causa probable y mejora: ") + action),
                      P("Criterio común: coherencia visual de cajas y niveles frente a la entrada; sin verdad-terreno de ocupación. El número mostrado no es un valor esperado ni una tasa de acierto.", "SmallX"),
                      PageBreak()]
    story += [P("3  Conclusión y plan de mejora", "TitleX"),
              P("Los frentes rectos y densos producen niveles aparentemente coherentes. El apilamiento repetitivo y los productos irregulares causan abstenciones o niveles omitidos. Los huecos visibles de 021, 022 y 036 pueden quedar ocultos por un promedio alto. El detector opcional también confundió un cartel FUJIFILM con vacío en 041. Estos patrones justifican conservar revisión humana y bloquear la alarma."),
              P("Prioridad 1: etiquetar seis escenas piloto con ROI, niveles y huecos, con doble revisión. Prioridad 2: medir error absoluto de porcentaje por nivel, falsos positivos/negativos bajo 30 %, tasa de no evaluables y latencia en PC Duoc; separar por escena. Prioridad 3: ajustar geometría y modelo sin usar el test reservado para calibración. Prioridad 4: implementar autenticación y persistencia reales. Sólo activar avisos si cliente y equipo aceptan el error medido."),
              P("Viabilidad", "HeadingX"),
              P("El MVP de apoyo visual es viable si se limita a una cámara/encuadre definido y el sistema puede abstenerse. Un aviso automático fiable bajo 30 % todavía no está demostrado. Si las nuevas etiquetas muestran demasiados errores, el entregable debe permanecer como herramienta de inspección, no como alarma operacional."),
              P("Demostración de 5 a 10 minutos", "HeadingX"),
              P("El equipo debe grabar un recorrido real siguiendo docs/GUIA_DEMO_INTERMEDIA.md: arranque, salud de la API, análisis de un frente denso, caso 021 con hueco, caso no evaluable, límites y siguiente paso. El video no se declara producido en este informe."),
              P("Evidencias verificables", "HeadingX"),
              P("README.md; docs/INFORME_INTERMEDIO_2026-10-21.md; scripts/evaluar_piloto_intermedio.py; artifacts/diagnostics/informe-intermedio/resultados.json; backend/app.py; backend/visual_occupancy.py. Fotografías y pesos son locales y no deben subirse a un repositorio público sin permiso."),
              ]
    doc.build(story)
    print(OUT)


if __name__ == "__main__":
    main()
