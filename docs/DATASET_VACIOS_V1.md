# Dataset de cajas de espacios vacíos — auditoría 21-10-2026

## Decisión

El modelo del compañero pasa a ser el detector de productos predeterminado. El nuevo dataset de `DATASETS/Espacios vacios/archive/void detection on retail shelves` se utiliza **únicamente para entrenar y evaluar un detector de huecos candidato**, independiente del modelo de productos. No se habilita aún la alerta de ocupación menor al 30 %.

## Calidad y restricciones

- Origen: exportación Roboflow local, 536 fotografías JPG de 640 × 640 px, una clase de cajas `void_detection`. Las 536 tienen archivo de etiquetas; hay 2490 cajas y no se hallaron coordenadas fuera de rango.
- La división original tiene 506/19/11 imágenes en train/valid/test. Los nombres revelan aumentos de una foto base (`*_jpg.rf.*`). **Diez de las once escenas de test también están en train**. Por eso las métricas obtenidas con esa división serían inválidas como prueba independiente.
- `data.yaml` declara licencia **Private**. No publicar las imágenes, etiquetas ni pesos entrenados con esos datos sin comprobar los permisos del propietario.
- Las cajas marcan huecos visibles, pero no marcan la extensión del área útil de cada nivel ni el porcentaje real de stock. Una caja de hueco no es una unidad faltante de inventario.
- Todos los archivos de etiquetas contienen al menos una caja. El dataset no aporta ejemplos certificados de góndolas completamente llenas; por ello no permite medir bien la tasa de falsas alarmas en ese caso crítico.

## Preparación reproducible

`backend.prepare_void_dataset` agrupa por foto base antes de repartir y genera `data/processed/void_detection_v1`, ignorado por Git. Con semilla 20261021 resultan 134 escenas/374 imágenes de entrenamiento, 29/85 de validación y 29/77 de prueba, sin escenas compartidas. Los aumentos de una foto nunca cruzan divisiones. Las cifras y procedencia quedan en `manifest.json`.

La separación elimina la fuga **de aumentos de la misma foto**, pero fotos distintas podrían corresponder al mismo pasillo o a tomas consecutivas. No hay metadatos de tienda/cámara para descartar esa dependencia. El test corregido sigue siendo una evaluación preliminar del dataset externo, no una validación en las góndolas objetivo.

```powershell
.\.venv\Scripts\python.exe -m backend.prepare_void_dataset
.\.venv\Scripts\python.exe -m backend.train_voids --epochs 12 --imgsz 512 --batch 4 --device cpu
```

El segundo comando entrena un detector YOLO26n de **vacíos** desde pesos generales. Es un candidato separado, no mezcla los pesos incompatibles de ambos detectores ni reemplaza al detector de productos. Su informe queda junto a `best.pt` en `artifacts/runs/void-detection-v1/`.

Tras completar la evaluación, el candidato se copia localmente a `artifacts/models/void-yolo26n-candidate.pt`. La web permite solicitar sus **cajas rojas experimentales** junto al detector de productos. Esta opción está deshabilitada si faltan los pesos y nunca activa el porcentaje ni la alarma del 30 %.

Inspección preliminar del mejor checkpoint tras seis épocas: en una imagen de cada escena de prueba local (`014`, `025`, `036`, `041`) produjo respectivamente 0, 2, 1 y 0 cajas con confianza ≥ 0,25. Las dos escenas con cajas parecen contener huecos visibles, pero esa observación **no es una métrica** y no descarta omisiones o falsos positivos en otras fotos. La imagen local `045_8`, antes problemática para el segmentador, produjo 0 cajas. Las previsualizaciones están en `artifacts/diagnostics/void-local-sample-epoch6/` y `artifacts/diagnostics/void-local-045/`.

## Resultado final del candidato de 12 épocas

El mejor checkpoint se evaluó sobre las **77 variantes de 29 escenas reservadas**: mAP@0.5 **0,7376**, mAP@0.5:0.95 **0,3391**, precisión **0,7538**, recall **0,6350** para cajas de hueco. Informe reproducible: `artifacts/runs/void-detection-v1/evaluation.json`. Este test externo sigue sin representar la cámara ni el surtido final de nuestro proyecto.

En la revisión final de cinco fotos locales (`014`, `025`, `036`, `041`, `045_8`) produjo 0, 2, 5, 3 y 0 cajas con confianza ≥ 0,25. **Fallo confirmado:** en `041_1` marcó el cartel superior FUJIFILM y el espacio libre *sobre* los productos como tres huecos de stock, aunque no son faltantes del frente de venta. Ver `artifacts/diagnostics/void-local-final/041_1_jpeg_jpg.rf.eebf90edac5e6b2a5f33408eb762f82a.jpg`. Es un cambio de dominio: el modelo no conoce la geometría del área útil. Por ello las cajas rojas se muestran sólo bajo petición y **no se usarán para calcular el 30 % ni emitir avisos**.

Prueba funcional de la API con ambos modelos en un i5-12600KF: el arranque frío demoró 4,3–5,8 s mediante TestClient y 6,49 s por HTTP local; tras cargar ambos modelos una solicitud HTTP demoró 0,25 s con la misma imagen. Son tiempos exploratorios, no p95 ni garantía de cinco segundos en el PC de Duoc. El arranque frío **superó** la meta de cinco segundos y requiere optimización o precarga si esa meta incluye la primera solicitud.

## Antes de activarlo

1. Revisar visualmente cajas de vacío sobre fotos de góndolas del proyecto, incluidas escenas llenas, parcialmente vacías y casi vacías.
2. Anotar en esas fotos vacíos y área útil por nivel. Reservar escenas independientes para una prueba local; medir huecos falsos por imagen y recall de huecos reales.
3. Definir ocupación visual sobre el área útil detectada, no sobre toda la fotografía ni sólo sobre cajas de productos. Compararla con porcentajes anotados por humanos.
4. Activar alerta `< 30 %` sólo si su precisión/recall, falsos avisos y latencia en el PC de destino cumplen criterios acordados. Hasta entonces API y web muestran `null` para porcentaje y alerta.
