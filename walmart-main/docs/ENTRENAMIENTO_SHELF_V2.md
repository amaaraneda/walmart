# Detector de productos: dataset Shelf v2

La descarga de `MODELO/archive (1)` contiene datos y anotaciones, no pesos entrenados. Se conserva intacta. El modelo sigue usando YOLO26n con una clase `product`; la clasificación por tipo de envase no es necesaria para estimar ocupación.

## Preparación reproducible

Desde la raíz, en PowerShell:

```powershell
.\.venv\Scripts\python.exe -m backend.prepare_shelf_dataset
```

El comando crea `data/shelf_products_v2` y se niega a sobrescribir un destino existente. El manifiesto conserva el origen, SHA256, escena y partición de cada imagen.

- Descarga original: 1.040 imágenes, 120.553 anotaciones, 11 clases.
- Se excluyen 37 imágenes que contienen la clase desconocida `-`. Excluir sólo sus cajas las convertiría incorrectamente en ejemplos de fondo.
- Las diez clases explícitas de producto se convierten en `product`; se eliminan cajas exactamente duplicadas.
- Se agrupan las variantes por el primer número del archivo: 22 grupos de entrenamiento, cuatro de validación y cuatro de prueba. Un grupo adicional queda sin imágenes elegibles. Es una agrupación conservadora inferida del nombre, pendiente de revisión visual integral.
- En validación y prueba se conserva una variante por nombre original, elegida por orden alfabético. No se conoce cuál es la imagen sin transformación.
- Resultado: 734 imágenes / 93.855 cajas de entrenamiento; 29 / 2.313 de validación; 30 / 3.014 de prueba. Ningún grupo ni hash exacto cruza particiones.

La separación ya suministrada mezclaba variantes de escenas entre entrenamiento y prueba. Sus porcentajes originales no se reutilizan.

## Entrenamiento inicial en CPU

```powershell
.\.venv\Scripts\python.exe -m backend.train --data data/shelf_products_v2 --output artifacts/candidates/shelf-v2/gondola-yolo26n.pt --name shelf-v2-cpu --epochs 10 --imgsz 416 --batch 8 --device cpu --workers 0 --freeze 10
```

Se parte de los pesos preentrenados de `artifacts/pretrained/yolo26n.pt`. Congelar los primeros diez módulos reduce el costo en CPU. Diez épocas constituyen una corrida inicial, no una búsqueda exhaustiva ni garantía de convergencia. Los resultados y mejores pesos quedan en `artifacts/runs/`. La corrida histórica evaluó prueba antes de activar; el flujo actual usa validación para seleccionar candidatos y reserva prueba para una comprobación final.

Para entrenamiento posterior con GPU se puede usar un nombre y destino nuevos, aumentar épocas y resolución, y omitir `--freeze 10`. Los conjuntos de prueba deben permanecer reservados; para ajustes sucesivos se usa validación. El ensayo en CPU sin capas congeladas está documentado en [EXPERIMENTO_SHELF_V3.md](EXPERIMENTO_SHELF_V3.md); no reemplazó al modelo activo.

## Comparación antes de activar

```powershell
.\.venv\Scripts\python.exe -m backend.compare_models --candidate artifacts/candidates/shelf-v3-unfrozen-640/gondola-yolo26n.pt --data artifacts/config/shelf-v3-unfrozen-640.yaml --report artifacts/candidates/shelf-v3-unfrozen-640/validation-comparison.json --split val
```

Compara la línea base activa y el candidato con las mismas imágenes de validación, a resolución de inferencia 640 y máximo de 1.000 detecciones. Guarda mAP50, mAP50–95, precisión, recall, tiempos y hashes de los pesos. No cambia automáticamente el modelo activo. El conjunto de prueba sólo debe revisarse al cerrar una iteración, no para escoger nuevos hiperparámetros.

La activación debe respaldar los pesos y metadatos anteriores, copiar conjuntamente los nuevos y reiniciar la API. No se deben comparar las métricas históricas de nueve imágenes con las de estas treinta como si fueran el mismo experimento.

El 18-10-2026 se completó la corrida y se activó el candidato mediante `python -m backend.activate_model`. A 640 px, el modelo anterior obtuvo mAP50=0,2271 y mAP50–95=0,0639; el nuevo obtuvo 0,4773 y 0,1578, con precisión=0,5043 y recall=0,5169. Son métricas de detección, no porcentajes de exactitud de stock. El respaldo está en `artifacts/backups/20261018T195233618635Z/`.

Con la API encendida, `python -m backend.smoke_mvp` comprueba los archivos web y seis subidas de imágenes. La corrida local obtuvo mediana=0,046 s, máximo=2,988 s y detecciones en cinco de seis recortes. El recorte sin detecciones devolvió `review_required=true`; el 0 % no constituye una medición fiable de góndola vacía. Las respuestas y seis imágenes anotadas están en `artifacts/smoke_shelf_v2/`.

## Uso

Abrir `INICIAR_MVP.cmd`, esperar `Application startup complete` y entrar a `http://127.0.0.1:8000/`. En Análisis visual se sube una foto completa. La interfaz muestra detecciones de productos, pero no calcula ocupación ni alarma: la heurística de niveles y huecos se retiró tras encontrar falsos positivos. El ensayo posterior de un segmentador de vacíos está documentado en [EXPERIMENTO_HUECOS.md](EXPERIMENTO_HUECOS.md) y tampoco se activó.

El dataset no contiene máscaras de espacio útil ni porcentajes reales de ocupación. Mejorar la detección no valida automáticamente ese porcentaje o las alertas. El login y el CRUD siguen siendo demostrativos en el navegador; la cámara en vivo aún no forma parte de esta implementación.

## Procedencia

Kickkung, *Shelf detection for COCO format*, versión 2. Licencia declarada CC BY 4.0. Fuente: https://universe.roboflow.com/kickkung/shelf-detection-for-coco-format/dataset/2. Se redistribuyen por separado las modificaciones de etiquetas, selección de imágenes y particiones mediante el manifiesto local. La licencia de los datos es independiente de la licencia de Ultralytics.
