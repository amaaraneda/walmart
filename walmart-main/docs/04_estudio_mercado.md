# Estudio de mercado inicial

## Hallazgo

Existen plataformas comerciales de analítica de góndolas que combinan visión por computador, captura de imágenes, métricas de disponibilidad y tableros de operación. Esto valida la relevancia del problema, pero sus productos suelen cubrir reconocimiento de SKU, ejecución comercial y operación a gran escala: un alcance mayor que el MVP académico.

| Solución / referencia | Funcionalidades publicadas | Relación con el proyecto | Diferenciador propuesto |
| --- | --- | --- | --- |
| [Trax / FORM](https://traxretail.com/technology/) | Visión por computador para información de estantes, ejecución comercial y métricas. | Es un referente de análisis de góndolas a escala. | MVP focalizado en vacío útil visible, evidencia explicable y adaptación a las condiciones acordadas con Walmart Chile. |
| [Trax: geometría y captura](https://traxretail.com/blog/computer-vision-extracts-data-store-images/) | Reconstrucción de estantes, geometría, perspectiva y métricas de espacio. | Confirma que perspectiva y geometría son problemas centrales. | Definir una medición honesta en plano visible y validar rectificación antes de prometer medida física. |
| [Grocery Shelves](https://huggingface.co/datasets/UniDataPro/grocery-shelves) | Dataset público de imágenes de góndolas. | Insumo exploratorio o de preentrenamiento, no producto comercial. | Normalización y prueba con imágenes de dominio Walmart. |
| [Supermarket Shelves Dataset](https://www.kaggle.com/datasets/humansintheloop/supermarket-shelves-dataset) | Dataset público anotado de estantes. | Insumo para prototipar etiquetas y línea base. | Guía de etiquetado específica para vacío útil y estructura. |

## Ventajas y límites de alternativas existentes

- Las plataformas comerciales ofrecen capacidad industrial, más fuentes de datos y módulos de ejecución; normalmente implican integración, licenciamiento y alcance superiores al proyecto.
- Los datasets públicos aceleran experimentación, pero pueden diferir en cámara, surtido, idioma visual, iluminación, configuración de góndolas y definición de etiqueta.
- La propuesta académica agrega valor si logra una solución auditable: resultado visual explicable, umbral configurable, trazabilidad de versión y evaluación honesta en imágenes reales del cliente.

## Próximo paso del estudio

Profundizar en dos o tres alternativas tras confirmar el canal de captura del cliente (móvil, cámara fija o imágenes ya existentes). Para cada una se compararán precio/licencia cuando sea público, despliegue, privacidad, tiempo de respuesta, métrica de vacío y compatibilidad con infraestructura Walmart.
