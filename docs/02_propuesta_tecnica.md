# Propuesta técnica inicial

## Decisión arquitectónica para el MVP

El MVP usará detección ligera de productos, apoyada por OpenCV y NumPy. Se compararán YOLOv8n y SSD MobileNet V2 FPNLite 320x320 con las mismas cajas normalizadas y el mismo postprocesamiento clásico. U-Net no forma parte de la implementación inicial porque requeriría máscaras de vacío útil que el dataset actual no contiene.

## Flujo de inferencia

```text
Imagen -> control de calidad -> detección/rectificación de góndola
       -> detección de productos -> agrupación por nivel y unión de intervalos
       -> cálculo de porcentaje
       -> regla de alerta -> evidencia visual + resultado trazable
```

La rectificación de perspectiva se evalúa como preprocesamiento. Si no es suficientemente estable, la salida debe reportar porcentaje en el plano visible, con esta limitación explícita.

## Componentes

| Capa | Propuesta inicial | Decisión pendiente |
| --- | --- | --- |
| Ingesta | API HTTP para carga de imagen | Aplicación móvil, cámara fija o carga manual |
| Calidad de imagen | Resolución mínima, desenfoque, exposición y encuadre | Umbrales y mensaje al usuario |
| Visión | Python, OpenCV, NumPy y un detector ligero por seleccionar | Comparar YOLOv8n frente a SSD MobileNet V2 FPNLite; validar licencia y métricas |
| Servicio | FastAPI | Forma de autenticación e integración |
| Persistencia | Base relacional para metadatos; almacenamiento de objetos para imágenes | Servicios disponibles del cliente |
| Entrega | Docker | Nube, servidor local o edge |
| Observabilidad | Registro de latencia, confianza, versión y revisión humana | Herramienta de monitoreo |

## Datos y anotación

1. Definir una guía de etiquetado antes de anotar: góndola, nivel, vacío útil, vacío no utilizable, producto, estructura y zona ambigua.
2. Normalizar formato, resolución/orientación y metadatos de captura.
3. Separar entrenamiento, validación y prueba por local o sesión de captura; nunca distribuir imágenes casi idénticas entre conjuntos.
4. Mantener una muestra de prueba fija, no usada en entrenamiento ni ajuste de umbrales.
5. Registrar desacuerdos entre anotadores y revisar casos ambiguos con el cliente.

Los datasets públicos de Grocery Shelves y Supermarket Shelves pueden aportar preentrenamiento o exploración; no deben asumirse equivalentes a las imágenes de Walmart. Se debe revisar licencia, etiquetas y sesgo de dominio antes de utilizarlos.

## Métricas recomendadas

| Objetivo | Métrica |
| --- | --- |
| Máscara de vacío útil | IoU y F1/Dice por imagen y por nivel |
| Porcentaje de vacío | MAE en puntos porcentuales frente a anotación humana |
| Alerta | Precisión, recall, F1 y matriz de confusión para disponibilidad visual menor al 30 % |
| Operación | p50/p95 de latencia, porcentaje de imágenes rechazadas y tasa de revisión humana |

No se debe declarar exactitud global sin desglosar resultados por ángulo, iluminación, apilamiento y local.

## Aprendizaje continuo seguro

El aprendizaje continuo no será reentrenamiento automático. El ciclo seguro es: capturar casos con baja confianza o corrección humana -> revisar/anonimizar -> etiquetar -> evaluar contra conjunto fijo -> aprobar manualmente -> publicar una nueva versión reversible. Esto evita degradar el modelo con etiquetas erróneas.
