# Experimento de detección de espacios vacíos — 18-10-2026

## Decisión

El candidato de segmentación de huecos **no se activó** en la aplicación. El porcentaje anterior calculado como complemento de cajas YOLO tampoco se usa: ausencia de una detección no demuestra ausencia de producto. La aplicación vigente devuelve `null` para ocupación y alerta, y `threshold_applied=false`.

## Datos y experimento reproducible

- Fuente externa: [gapDetection/gapDetectionDatasets](https://github.com/gapDetection/gapDetectionDatasets), dataset publicado junto a Santra, Ghosh y Mukherjee, *Pattern Recognition* (2022). Se usaron `GroZi-120` y `WebMarket` con máscaras binarias de huecos. La fuente solicita citar su artículo y repositorio; no incluye una licencia permisiva explícita visible, por lo que no se redistribuye automáticamente aquí.
- Entrenamiento: 71 fotos; validación: 18; test externo reservado: 59. U-Net pequeño, 320 × 320 px, BCE + Dice, 12 épocas; la época 9 obtuvo el mejor IoU de validación. Código: `backend/train_gaps.py` y `backend/gap_model.py`.
- Adaptación: fotos de entrenamiento de `data/shelf_products_v2`; sólo el interior de cajas locales etiquetadas como producto se supervisó como **no vacío**. El fondo sin etiqueta se ignoró. Código: `backend/adapt_gaps.py`.
- Resultado final en test externo: IoU de píxeles vacíos **0,7201**, precisión **0,8387**, recall **0,8358**. En cajas de productos del test local, 1,12 % de los píxeles interiores fueron marcados como vacíos; esta última métrica **no mide la precisión de huecos locales**.

Para reproducir, obtener el repositorio público en `data/gap_detection_public` con `GroZi-120` y `WebMarket` y ejecutar:

```powershell
.\.venv\Scripts\python.exe -m backend.train_gaps --epochs 12 --output artifacts\candidates\gap-unet\gap-unet.pt
.\.venv\Scripts\python.exe -m backend.adapt_gaps --initial artifacts\candidates\gap-unet\gap-unet.pt --output artifacts\candidates\gap-adapted\gap-unet.pt --epochs 5
.\.venv\Scripts\python.exe -m backend.inspect_gaps --weights artifacts\candidates\gap-adapted\gap-unet.pt --output artifacts\gap_inspection_adapted
```

Los pesos y previsualizaciones quedan en `artifacts/`, fuera de Git por tamaño. Las métricas detalladas están en `artifacts/candidates/gap-adapted/gap-unet.json`.

## Revisión visual del dominio objetivo

En `artifacts/gap_inspection_adapted/example_02.jpg`, la foto `014_2` muestra zonas rojas sobre envases, verduras y bandejas que **no son vacíos**. Es una falla de generalización entre los supermercados públicos y las fotos objetivo, aunque la métrica del test externo sea razonable. Tampoco existe un test local con máscaras de vacío para medir cuántos huecos reales se omiten. Activar el modelo o emitir alertas con esos datos sería engañoso.

## Condición para reactivar el 30 %

1. Reunir fotos representativas del encuadre final: góndolas llenas, parcialmente vacías y casi vacías; incluir distintos productos e iluminación.
2. Anotar en cada foto **máscara de huecos visibles** y **área útil de cada nivel**, separando escenas/tiendas entre entrenamiento y prueba. Las cajas de producto existentes no sustituyen estas etiquetas.
3. Ajustar el segmentador en entrenamiento y elegir umbral con validación. Reservar prueba local sin modificar para medir IoU, precisión/recall de huecos y falsos positivos por imagen.
4. Calcular ocupación sólo dentro del área útil anotada/detectada, evaluar específicamente la alarma `<30 %` y medir latencia en el PC de destino. No activar si hay falsos avisos sobre productos como en la previsualización citada.

La delimitación manual es necesaria **al preparar datos de entrenamiento**, no durante la inferencia del usuario final.
