# Protocolo de etiquetado y validación de bajo stock

## Objetivo y decisión

Crear una referencia humana de **ocupación visual por nivel de góndola**. La regla solicitada es avisar cuando la ocupación cae **por debajo** del 30 %; exactamente 30 % no genera aviso. No equivale a inventario físico ni a contar unidades. Hasta validar el sistema con fotografías de las góndolas objetivo, la plataforma debe mantener `occupancy_percent` y `low_stock_alert` sin valor operativo.

## Unidad de análisis

Cada fotografía tiene un `scene_id` estable (tienda, pasillo, cámara y toma original) y uno o más niveles. Cada nivel contiene:

- `roi`: polígono del **frente útil donde podrían exhibirse productos**, delimitado por la geometría visible del nivel. No incluir carteles, etiquetas de precio, soportes, bordes negros, techo de la foto ni espacio libre habitual *sobre* envases bajos. Si el frente útil no puede inferirse, no inventarlo: marcar el nivel `unusable`.
- `gaps`: polígonos de faltantes reales **dentro** de ese frente útil. Un hueco no es una sombra, reflejo, separación normal entre productos o espacio sobre sus tapas. Si el nivel está lleno, usar `gaps: []` después de revisar toda la ROI; nunca dejarlo vacío sólo por omisión.
- `visibility`: `clear`, `occluded` o `unusable`. Los dos últimos se conservan para análisis cualitativo, pero no entran en el indicador ni en la prueba de alertas.

La referencia principal por nivel es **ocupación del ancho frontal**: rasterizar ROI y huecos en resolución original, proyectar ambos sobre el eje horizontal y calcular `100 × (columnas_ROI − columnas_con_hueco) / columnas_ROI`. Los huecos superpuestos no se cuentan dos veces. Se conserva también la ocupación por área como diagnóstico secundario, pero **no** se mezcla con el porcentaje frontal. Esto evita que el aire sobre productos bajos reduzca artificialmente el stock. La alerta de referencia es `ocupación frontal < 30`; exactamente 30 no alerta. Una fotografía con varios niveles produce **una decisión por nivel** y un promedio ponderado por ancho útil; no se toma el porcentaje de la imagen completa. Esta definición es una propuesta operativa para validar con docente/cliente antes de activar avisos.

## Cómo etiquetar

1. Conservar la fotografía original sin aumentos ni recortes, registrar ubicación/cámara/toma y asignar `scene_id`. Fotos consecutivas de la misma escena comparten grupo para la separación.
2. Marcar todos los niveles visibles y el frente útil de cada uno. Si una región muestra productos de distinta altura, ajustar la ROI al área realmente exhibible; no usar un rectángulo vertical que incluya aire de forma sistemática.
3. Marcar huecos dentro de cada ROI. Revisar con especial atención carteles, áreas sobre productos, superficies reflectantes, extremos de góndola y espacios entre envases.
4. Poner `review_status: reviewed` sólo tras comprobar todos los niveles y huecos. Ante ambigüedad, usar `occluded`/`unusable` y dejar nota externa; no forzar una verdad binaria.
5. Hacer segunda revisión de las fotos cercanas al 30 % y de cualquier desacuerdo entre anotadores. Registrar la decisión consensuada; conservar la anotación original para auditarla.

## Muestreo y partición

Incluir niveles llenos sin huecos (negativos), parcialmente vacíos, justo sobre/debajo del umbral y casi vacíos; variar iluminación, ángulo, familias de envases y tiendas/cámaras disponibles. Las ~60 fotos iniciales pueden servir para el piloto, pero no prueban generalización. Registrar cuántas **escenas independientes** hay realmente.

Asignar `train`, `val` o `test` **por escena original antes de cualquier aumento**. Imágenes derivadas, tomas consecutivas de la misma configuración y versiones recortadas no deben cruzar particiones. Mantener `test` reservado y sin ajustar umbrales con él. Si sólo existe una tienda/cámara, declarar explícitamente esa limitación.

## Criterio para activar la alerta

Comparar la predicción con la referencia por nivel claro y revisado: error absoluto de ocupación en puntos porcentuales, precisión y recall de alertas `<30 %`, y tasa de falsos avisos en niveles llenos. Registrar matriz de confusión y resultados por tienda/cámara, además de latencia p50/p95 en el PC de Duoc (incluyendo arranque frío por separado). El objetivo de cinco segundos se comprueba en el flujo extremo a extremo, no sólo en inferencia cálida.

Antes de fijar metas numéricas de precisión/recall o desplegar avisos, acordar con docente/cliente el coste aceptable de falsos avisos y faltantes omitidos. No presentar mAP de cajas de productos o huecos como exactitud de stock. Si la ROI no es fiable, la salida debe ser `requiere revisión`, no un porcentaje inventado.

## Formato local

Ver [estructura y ejemplo](../data/stock_ground_truth_v1/README.md). Cada JSON en `annotations/` corresponde a una imagen en `images/`; `split` y `scene_id` son obligatorios. Validar con `python -m backend.validate_stock_annotations data/stock_ground_truth_v1`. El ejemplo sintético no forma parte del conjunto medido.
