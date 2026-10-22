# MVP beta: análisis visual de góndolas

Este módulo detecta **productos** con el YOLO aportado por un compañero, seleccionado por defecto, en una fotografía completa. YOLO26n queda como comparación. El cálculo anterior de ocupación por fragmentos de riel resultó engañoso y se retiró. La nueva estimación agrupa niveles por bases alineadas de productos y mide ancho frontal cubierto, sin contar envases como porcentaje. La página ahora admite fotos, sin cámara. No identifica SKU ni cuenta inventario.

Se entrenó un candidato separado de segmentación de huecos con máscaras públicas y se adaptó parcialmente usando cajas de productos locales como negativos. Superó pruebas reservadas de los datos públicos, pero en fotografías del proyecto todavía confundió algunos productos con vacíos. **No está conectado a la API operativa**. El informe y las previsualizaciones se describen en [EXPERIMENTO_HUECOS.md](docs/EXPERIMENTO_HUECOS.md).

La API recibe la imagen completa sin coordenadas manuales y devuelve cajas de producto, niveles automáticos y `occupancy_percent` **experimental** cuando el frente parece medible. Es el promedio de ancho útil ocupado por nivel, no inventario físico. Si los límites no son observables devuelve `null`, no cero. `low_stock_candidate` señala niveles estimados bajo el umbral, pero `low_stock_alert=null`, `threshold_applied=false` y `review_required=true`: aún no se envían avisos operativos. Para activarlos hacen falta anotaciones locales de frente útil y huecos, seguidas de evaluación por escena de errores y latencia.

En Análisis visual se puede escoger entre el checkpoint del compañero (`artifacts/models/companero-yolo.pt`) y el YOLO26n anterior. Ambos detectan una clase de producto; el primero usa la etiqueta `Product`, que la API normaliza para procesarla. La selección cambia únicamente la inferencia de cajas y se devuelve como `model_id` en `/api/analyze`. El script de inferencia adjunto al checkpoint del compañero no se usa para declarar stock: delimita cada estante a partir de los propios productos detectados, por lo que puede ignorar espacio vacío en los extremos. En el mismo test de 30 imágenes, el compañero obtuvo mAP50 = 0,8200 frente a 0,4773 del anterior; esas imágenes representan sólo cuatro escenas base y no validan el porcentaje de ocupación.

## Estado real

- **Actualización 18-10-2026:** el modelo activo se entrenó con `data/shelf_products_v2`: 734 imágenes de entrenamiento, 29 de validación y 30 de prueba, agrupadas por escena. Se excluyeron imágenes con clase ambigua y variantes repetidas de evaluación. Corrida inicial: 10 épocas, 416 px, CPU y diez módulos congelados; inferencia a 640 px.
- Comparación sobre las mismas 30 imágenes a 640 px: mAP50 anterior **0,2271**, nuevo **0,4773**; mAP50–95 anterior **0,0639**, nuevo **0,1578**. El nuevo modelo está en `artifacts/models/gondola-yolo26n.pt`; sus métricas y el respaldo del anterior se registran en `metadata.json`. Sigue siendo preliminar.
- La prueba HTTP de productos se mantiene como verificación funcional. No valida detección de vacíos ni exactitud de stock en el hardware de Duoc.
- **Actualización 21-10-2026:** el modelo del compañero es el predeterminado. El dataset nuevo de huecos se preparó por escena para un detector candidato independiente; ver [DATASET_VACIOS_V1.md](docs/DATASET_VACIOS_V1.md). No se ha activado la alerta.
- Para abrir el sistema, ejecutar `INICIAR_MVP.cmd`. Ver preparación, entrenamiento y comparación reproducibles en [ENTRENAMIENTO_SHELF_V2.md](docs/ENTRENAMIENTO_SHELF_V2.md).

### Historial de la primera línea base (28-09-2026)

- El dataset `data/standardized_yolo_v1` contiene 59 imágenes y 9.651 cajas de productos: 41 para entrenamiento, 9 validación y 9 test.
- El dataset se utiliza desde la carpeta local de trabajo; no está empaquetado en la imagen Docker ni en este módulo de código. Quien clone el repositorio debe disponer de él por el canal autorizado.
- La primera línea base se entrenó 20 épocas a 640 px en CPU y quedó respaldada al activar Shelf v2. Los pesos y resultados permanecen ignorados por Git. Si falta el checkpoint activo, la pantalla lo indica y la API responde 503; no se sustituye silenciosamente con pesos COCO.
- En las 9 imágenes de test, este checkpoint obtuvo **mAP50 = 0,2709** y **mAP50–95 = 0,1263** para detección de productos. Detectó al menos un producto en 8 de 9 imágenes con confianza 0,25. Es una línea base débil, no un modelo aprobado para producción.
- Una prueba local de la API con `supermarket_009.jpg` tardó 4,16 s en frío y aproximadamente 0,40 s en las dos solicitudes siguientes, en CPU i5-12600KF. No es una medición p95 ni prueba el requisito de 5 segundos en el hardware final.
- La alerta es una **estimación experimental**. El dataset no marca superficies vacías, regiones de estante ni valores reales de disponibilidad. Antes de operar hay que anotar esos datos y medir falsos positivos/negativos.
- En el escaneo de entrenamiento, Ultralytics descartó automáticamente una caja duplicada en `supermarket_005.jpg` y otra en `supermarket_022.jpg`; conviene corregir esas etiquetas en una nueva versión del dataset, sin alterar los originales de esta corrida.
- Login, roles y CRUD del frontend siguen siendo demostración local en el navegador, **no autenticación segura de producción**.

## Entrenar (PC con GPU o Colab)

Desde la raíz del proyecto, en Python 3.11:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
.\.venv\Scripts\python.exe -m backend.train --data data/shelf_products_v2 --output artifacts/candidates/shelf-v2-gpu/gondola-yolo26n.pt --name shelf-v2-gpu --epochs 50 --imgsz 640 --batch 4 --device 0
```

Para CPU, usa `--device cpu`; será más lento. En Colab, subir `data/shelf_products_v2`, `backend` y los pesos base `artifacts/pretrained/yolo26n.pt`, instalar las dependencias y ejecutar desde la raíz. El script conserva los datos originales y copia el mejor candidato al destino solicitado sólo después de evaluar el test. Los resultados quedan en `artifacts/runs/` (ignorados por Git). Para ajustar hiperparámetros usar validación; reservar test para evaluaciones finales.

## Ejecutar

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.app:app --reload --host 127.0.0.1 --port 8000
```

Abrir `http://127.0.0.1:8000`. Entrar con las cuentas de demostración indicadas en `frontend/README.md`, abrir “Análisis visual” y subir una fotografía completa. La API está en `/api/analyze`; `/api/health` permite comprobar si el checkpoint de productos está presente.

Si entrenas un checkpoint nuevo mientras la API está encendida, reinicia el servidor para cargar los pesos nuevos.

Alternativamente, después de entrenar, `docker compose up --build` sirve la misma app en el puerto 8000 y monta el checkpoint local como solo lectura. El entrenamiento no ocurre dentro del contenedor de inferencia.

## Validación requerida antes de piloto

1. Fotografiar góndolas reales con una cámara y encuadre definidos; separar por tienda/escena para evitar fuga entre train y test.
2. Anotar regiones de estante y porcentaje visible de ocupación (o máscaras de producto/vacío); validar la estimación contra ese dato de referencia.
3. Medir precisión y recall de alertas bajo 30 %, además de latencia en el hardware final. El objetivo de 5 segundos aún **no está verificado**.
4. Definir el protocolo de cámara en vivo, persistencia de eventos y autenticación real antes del despliegue operativo.

## Versión

Al 28-09-2026, [YOLO26 es la última familia publicada de Ultralytics](https://docs.ultralytics.com/models/). La [documentación de YOLO27](https://docs.ultralytics.com/models/yolo27/) es un adelanto: sus pesos y código aún no están disponibles. Se usa `yolo26n.pt` con `ultralytics==8.4.164`, la versión disponible en PyPI al preparar este MVP. El backend carga el checkpoint por `GONDOLA_WEIGHTS`, de modo que se puede sustituir tras evaluar una versión futura.

Antes de usarlo como herramienta interna o comercial de Walmart, revisar la [licencia de Ultralytics](https://www.ultralytics.com/license): el uso académico abierto y el despliegue privado/comercial tienen obligaciones diferentes (AGPL-3.0 o licencia Enterprise, según el caso). No asumir que publicar el código de este prototipo resuelve automáticamente el caso de uso final.
