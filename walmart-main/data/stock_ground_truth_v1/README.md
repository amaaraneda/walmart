# Referencia local de ocupación visual v1

Copiar fotografías originales a `images/` y guardar un JSON por foto en `annotations/`. Ambas carpetas se excluyen de Git para no publicar imágenes del cliente ni sus anotaciones sin autorización. El ejemplo de formato está en `examples/ejemplo.json` y **no es una etiqueta real**.

El piloto incluye las 60 fotos externas entregadas al inicio, copiadas con prefijos `grocery_` y `supermarket_`. `inventario_piloto.csv` registra su origen y dimensiones; `scene_id` y `split` están pendientes de revisión humana. No mezclar esas fotos con una evaluación de la cámara final. Para dibujar las etiquetas, abrir `tools/stock_annotator/index.html` en el navegador, seleccionar una fotografía, marcar nivel y huecos, y guardar el JSON descargado en `annotations/` con el mismo nombre base que la imagen. El navegador no sube las fotos a ningún servidor.

Leer `docs/AUDITORIA_PILOTO_60.md` y `cola_revision.csv` antes de empezar: los 60 archivos incluyen recortes de producto, un duplicado exacto y escenas sin suficiente stock bajo. La cola prioriza los primeros casos a revisar; **no** contiene etiquetas ni particiones definitivas.

Opcional: cargar `artifacts/diagnostics/stock-pilot-triage/propuestas.json` en el etiquetador. Las cajas rojas punteadas son sugerencias del detector y **no se exportan** como etiquetas. Una persona debe decidir si corresponden a huecos reales y dibujar los polígonos confirmados.

Validación: `python -m backend.validate_stock_annotations data/stock_ground_truth_v1`. El comando comprueba geometría, correspondencia con la imagen, revisión y fugas entre particiones; imprime ocupación y alerta de referencia por nivel. No entrena modelos ni habilita alertas en la plataforma.
