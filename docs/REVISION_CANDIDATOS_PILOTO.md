# Revisión de candidatos de hueco en el piloto — 21-10-2026

Se ejecutó `python -m backend.triage_stock_pilot` con `artifacts/models/void-yolo26n-candidate.pt`, confianza mínima 0,25 e imagen de entrada 512 px. El script conserva propuestas y previsualizaciones en `artifacts/diagnostics/stock-pilot-triage/`; **no crea etiquetas revisadas**. La cola cubre 14 archivos, pero `supermarket_004` y `035` son la misma fotografía: sólo 13 imágenes distintas.

| Imagen | Cajas propuestas | Observación visual |
|---|---:|---|
| `supermarket_021` | 4 | Captura un hueco grande y otros espacios plausibles, pero también marca espacio sobre cajas del primer nivel. |
| `supermarket_022` | 0 | Omite zonas visiblemente poco ocupadas en la sección de bebidas. |
| `supermarket_036` | 5 | Propone varios espacios entre productos; requieren delimitar el frente útil por nivel antes de medir stock. |
| `supermarket_041` | 1 | Falso positivo evidente sobre el cartel FUJIFILM, fuera de toda ROI de producto. |
| `supermarket_001` | 0 | Candidato negativo denso; todavía no certificado como lleno. |
| `supermarket_002` | 3 | Espacios pequeños entre latas; no asumir que todas las cajas son faltantes. |
| `supermarket_012` / `026` | 0 / 0 | Más negativos densos pendientes de revisión. |

En los 14 archivos hubo 29 cajas propuestas; al quitar el duplicado exacto quedan 26 propuestas en 13 imágenes. **Estos conteos no son precisión, recall ni exactitud de alarma**: no existe aún una referencia revisada para comparar. La omisión en `022` y el falso positivo en `041` bastan para mantener desactivado el cálculo operacional del 30 %.

El etiquetador local puede mostrar `propuestas.json` como rectángulos rojos punteados para guiar la inspección. No se incorporan automáticamente al JSON de verdad-terreno. Siguiente paso: revisión humana de ROI y huecos en el primer lote, validación de JSON y evaluación separada por escena. Si el lote confirma estos fallos, incorporar ejemplos negativos de carteles/aire y positivos de niveles parcialmente vacíos al siguiente entrenamiento; mantener `test` sin tocar.
