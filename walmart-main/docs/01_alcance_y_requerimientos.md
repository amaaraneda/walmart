# Alcance y requisitos iniciales

## Problema confirmado

El cliente busca identificar espacios vacíos en góndolas de supermercado usando imágenes reales tomadas en distintos locales, y determinar cuánto espacio libre existe. El análisis por nivel de góndola es deseable. El entorno presenta ángulos no frontales, iluminación variable y productos apilados.

## Definición operativa propuesta

Para una góndola o nivel, se propone medir:

`porcentaje de vacío útil = área visible etiquetada como vacía y aprovechable / área útil visible de la góndola o nivel × 100`

Esta fórmula debe validarse porque una imagen no permite inferir inventario oculto ni profundidad real. Los huecos estructurales, separadores y zonas no utilizables deben excluirse explícitamente.

## Alcance del MVP

**Entrada:** una imagen de una góndola o de una zona delimitada de góndola.

**Salida mínima:** porcentaje de vacío útil, alerta según umbral configurable, confianza del resultado y evidencia visual con la zona marcada.

**Salida deseable:** porcentaje y alerta para cada nivel del estante.

**Fuera de alcance inicial:** conteo de SKU, identificación de cada producto, predicción de reposición, lectura de inventario del ERP, video en tiempo real y automatización de compra. Podrán evaluarse después de que el MVP sea validado.

## Perfiles de usuario preliminares

| Perfil | Necesidad principal | Acciones esperadas |
| --- | --- | --- |
| Operador de tienda | Conocer góndolas con quiebre visible | Cargar/capturar imagen y revisar alerta |
| Supervisor | Priorizar reposición y revisar evidencia | Consultar resultados por local, góndola y nivel |
| Administrador técnico | Mantener la solución confiable | Configurar umbral, revisar calidad y versionar modelo |

## Requerimientos funcionales iniciales

| ID | Requerimiento | Estado |
| --- | --- | --- |
| RF-01 | El sistema debe recibir una imagen de góndola. | Propuesto |
| RF-02 | Debe validar formato, tamaño y calidad mínima de imagen antes de inferir. | Propuesto |
| RF-03 | Debe identificar la región útil de la góndola y, si es viable, sus niveles. | Propuesto |
| RF-04 | Debe estimar el porcentaje de espacio vacío útil por góndola. | Confirmado por desafío |
| RF-05 | Debe emitir una alerta de bajo stock cuando la disponibilidad visual estimada sea inferior al 30 %. | Confirmado por cliente |
| RF-06 | Debe guardar resultado, fecha, identificador de imagen, versión del modelo y evidencia visual. | Propuesto |
| RF-07 | Debe mostrar o exportar un resultado interpretable para el usuario. | Propuesto |
| RF-08 | Debe permitir incorporar imágenes revisadas para una futura mejora controlada del modelo. | Propuesto; no automática en MVP |

## Requerimientos no funcionales iniciales

| ID | Requerimiento | Criterio inicial |
| --- | --- | --- |
| RNF-01 | Latencia | Resultado en un máximo de 5 segundos por imagen bajo condiciones de referencia por acordar. |
| RNF-02 | Trazabilidad | Toda inferencia conserva versión de modelo y parámetros. |
| RNF-03 | Privacidad | Evitar o anonimizar personas identificables y no versionar imágenes privadas. |
| RNF-04 | Reproducibilidad | Datos, etiquetas, configuración y evaluación deben poder reconstruirse. |
| RNF-05 | Despliegue | La solución debe ejecutarse en contenedor Docker. |
| RNF-06 | Calidad | Las métricas se reportan por conjunto de prueba independiente y por condición de captura. |

## Decisiones que requieren validación del cliente

1. ¿La unidad de análisis será una góndola completa, un módulo, un nivel o los tres?
2. ¿Qué distingue un vacío útil de un hueco estructural o de un producto apilado?
3. La alerta de bajo stock se activa bajo 30 % de disponibilidad visual. Falta validar cómo se calculará y si el umbral cambia por categoría.
4. ¿Qué alerta necesita el negocio además del umbral: prioridad, persistencia durante 5 segundos, canal de notificación y responsable?
5. ¿Cómo se identifican local, pasillo, góndola y momento de captura?
6. ¿Habrá imágenes, cámara, almacenamiento o infraestructura ya disponibles?
7. ¿Qué precisión, tasa de falsas alertas y condiciones de operación consideran aceptables?
