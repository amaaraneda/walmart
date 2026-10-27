# Decisión arquitectónica del sistema de visión

> **Actualización 28-09-2026:** esta comparación registra una decisión previa, hoy superada por la instrucción de implementar el MVP con la familia YOLO más reciente utilizable. El prototipo actual emplea YOLO26n; YOLO27 aún no tiene pesos/código públicos. La elección para producción sigue condicionada a métricas de alerta, latencia y licencia. Ver `MVP_GONDOLAS.md` en la raíz del proyecto.

## Decisión vigente de arquitectura y validación pendiente del detector

El MVP usará un sistema híbrido de detección y postprocesamiento clásico. El detector específico se elegirá mediante una prueba técnica acotada antes de implementar el MVP completo:

```text
Imagen fija
  -> OpenCV: validación de calidad y región o niveles de góndola
  -> detector ligero: detección de productos mediante cajas
  -> NumPy: agrupación por nivel y unión de intervalos horizontales
  -> Regla de negocio: disponibilidad visual menor a 30 %
  -> FastAPI y Docker: respuesta trazable e instalable
```

**La arquitectura principal está decidida; el detector aún no.** YOLOv8n y SSD MobileNet V2 FPNLite 320x320 serán evaluados con el mismo conjunto de datos, la misma partición y el mismo postprocesamiento. El detector ganador se convertirá en el único detector del MVP.

U-Net no forma parte de la implementación inicial porque las etiquetas actuales no son máscaras. No se agregará un tercer detector salvo que ambos candidatos fallen el criterio de aceptación.

## Evidencia del proyecto

La decisión se basa en material disponible en el repositorio, no en una sugerencia aislada.

| Fuente | Hecho relevante | Implicancia |
| --- | --- | --- |
| `Walmart_Resumen Primera Reunión.pdf` | El problema busca identificar dónde y cuándo hay quiebre, no clasificar SKU. Recomienda solución modular, visión clásica, scripts estructurados, 2 a 5 segundos por imagen y evaluación contra dataset oculto. | El detector debe ser ligero y el cálculo debe ser explicable. |
| `Deteccion_Espacios_Vacios_Gondolas_IA.pdf` | Se solicita detectar y cuantificar espacio vacío. La alternativa funcional admite una alarma cuando hay menos de 30 % de productos disponibles. | La salida principal es una alarma operacional, no una segmentación de SKU. |
| Dataset cargado | Hay 60 imágenes: 45 de Supermarket Shelves con cajas `Product`/`Price`, y 15 de Grocery Shelves con polígonos de `Box`. | El dato disponible entrena detección por cajas, no segmentación semántica de vacío útil. |
| Conceptos entregados | Incluyen YOLO, Keras/TensorFlow, Docker, estandarización de formato y procesamiento en cinco segundos. | YOLO es una alternativa sugerida compatible con las anotaciones actuales; Docker y trazabilidad son obligatorios para el diseño. |

## Comparación de alternativas

| Alternativa | Ajuste a las etiquetas actuales | Recursos y latencia | Explicabilidad para la alarma | Riesgo principal | Decisión |
| --- | --- | --- | --- | --- | --- |
| YOLOv8n + OpenCV/NumPy | Alto. Consume directamente cajas de producto y permite entrenar por transferencia. | Alto. Variante nano apta para GPU de Colab y prueba en PC de sede. | Alto. Las cajas se transforman en intervalos auditables por nivel. | Licencia AGPL-3.0 de Ultralytics. | Candidato A. |
| U-Net | Bajo. Requiere máscaras de producto, vacío útil y zona no utilizable que los 60 datos no contienen. | Medio. Añade etiquetado y entrenamiento más costosos. | Alto si existieran máscaras, pero no resuelve la falta de datos. | Desalineada del formato disponible. | No usar en MVP. |
| SSD MobileNet TensorFlow | Alto. También consume cajas. | Alto. Es ligero y posee licencia permisiva. | Alto con el mismo postprocesamiento. | Más trabajo de integración inicial. | Candidato B. |
| Sólo OpenCV | Bajo para detectar productos variados, reflejos y ángulos reales. | Muy alto. | Alto. | No tiene percepción suficientemente robusta por sí sola. | Se usa como apoyo, no como detector. |

## Regla de cálculo propuesta

Para cada nivel `L` de una góndola:

1. Se determina el intervalo horizontal útil `[x_inicio, x_fin]` del nivel.
2. Se asigna cada caja de producto al nivel correspondiente mediante la base de la caja y la geometría del estante.
3. Se proyecta cada caja a un intervalo horizontal `[x_min, x_max]` y se recorta al área útil.
4. Se unen los intervalos superpuestos. Una región cubierta por varias cajas cuenta una sola vez.
5. Se calcula la disponibilidad visual:

`disponibilidad_visual = longitud_horizontal_cubierta / longitud_horizontal_util * 100`

6. Se emite alarma si `disponibilidad_visual < 30`.

La métrica representa cobertura horizontal visible, no inventario físico ni volumen tridimensional. Si no se puede reconocer el nivel o el área útil con calidad suficiente, el resultado debe ser `requiere_revision` y no una alerta automática.

## Restricciones y controles

- El agrupamiento por `y_max` es una línea base, no una garantía. Debe combinarse con líneas de estante, agrupamiento robusto o una región de nivel configurada.
- No se aplicarán correcciones inversas agresivas de fisheye como aumentación. Las variaciones sintéticas sólo se aplican al conjunto de entrenamiento y deben representar condiciones plausibles.
- Los 60 datos públicos se usan para preparar el pipeline. No prueban desempeño sobre imágenes reales ocultas de Walmart.
- Se debe construir y versionar `dataset_maestro.json` antes de entrenar. La carpeta actual no contiene aún ese archivo ni el módulo de postprocesamiento afirmado en conversaciones previas.
- La implementación Ultralytics debe revisarse contra la política de licencia antes de cualquier transferencia comercial o repositorio cerrado. Para el prototipo académico, se mantendrá el código fuente visible y se documentarán dependencias y licencias.

## Protocolo de selección del detector

No se elegirá una herramienta por haber sido nombrada por el cliente, por popularidad o por una imagen de demo. Se entrenarán ambos candidatos sobre el mismo `dataset_maestro.json`, con fotos originales separadas antes de toda aumentación. Luego se medirá:

1. Precisión, recall y mAP para la detección de producto.
2. Latencia p50 y p95 del flujo completo en el PC de sede.
3. Consumo de memoria de entrenamiento e inferencia.
4. F1 de la alarma bajo 30 % sobre imágenes con nivel y cobertura verificados manualmente.
5. Compatibilidad de licencia con el modo de entrega acordado.

Se elegirá el modelo que cumpla el límite de cinco segundos y entregue la mayor F1 de alarma. En caso de diferencia marginal, se prefiere la alternativa con licencia más simple y menor complejidad de mantenimiento. Hasta obtener esa evidencia, **YOLOv8n no está seleccionado como modelo final**.
