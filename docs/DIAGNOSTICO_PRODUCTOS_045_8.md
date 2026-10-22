# Diagnóstico de productos en `045_8`

La captura de pantalla mostraba 25 cajas verdes pese a que el detector devolvía 72 propuestas. La API ya infería con confianza mínima de 0,25; el servidor sólo dibujaba las superiores a 0,50. Esa discrepancia fue un error de visualización introducido al simplificar la interfaz.

| Configuración a 640 px | Propuestas | Coinciden con 46 cajas etiquetadas (IoU ≥ 0,5) |
|---|---:|---:|
| Confianza ≥ 0,25 | 72 | 46 |
| Confianza ≥ 0,35 | 46 | 38 |
| Confianza ≥ 0,50 | 25 | 22 |
| Imagen completa + cuatro recortes, ≥ 0,25 | 81 | 40 |

El esquema con recortes introdujo cajas duplicadas/incorrectas y redujo coincidencias en esta imagen; **no se activó**. Subir sólo la resolución a 960 o 1280 px tampoco mejoró esta imagen. La imagen original tiene productos visibles que no están entre las 46 etiquetas, especialmente en el borde inferior, por lo que las cajas no coincidentes no son automáticamente falsos positivos. Tampoco se puede inferir disponibilidad de stock a partir de estas cajas.

La página ahora dibuja **todas** las propuestas desde 0,25: ámbar entre 0,25 y 0,50; verde desde 0,50. Se distinguen propuestas de detecciones más seguras, sin presentar ninguna como inventario confirmado. La previsualización HTTP está en `artifacts/smoke_user_045_8/analysis_1.jpg` y la tabla de diagnóstico en `artifacts/diagnostics/045_8_product_tiled.json`.

Reproducir:

```powershell
.\.venv\Scripts\python.exe -m backend.diagnose_product --image data\shelf_products_v2\images\val\045_8_jpeg_jpg.rf.cf4d78bc08b6bee810ccfc30b5497398.jpg --output artifacts\diagnostics\045_8_product_tiled.json --preview-dir artifacts\diagnostics\045_8_tiled --tiles
```

El siguiente aumento real de recall requiere corregir y completar anotaciones de productos y evaluar nuevas fotos de prueba por escena. No se justifica activar inferencia por recortes sólo porque detecte más cajas.
