# Auditoría visual del piloto de 60 fotos — 21-10-2026

## Hallazgo principal

Las 60 imágenes entregadas **no son 60 ejemplos independientes de bajo stock**. Son 15 recortes cercanos de productos (`grocery_*`) y 45 escenas variadas de supermercado (`supermarket_*`). La mayoría de las escenas amplias están bastante llenas. Hay **un duplicado exacto**: `supermarket_004.jpg` y `supermarket_035.jpg` (mismo SHA-256); no pueden contarse como dos muestras ni ir a particiones distintas. No se detectaron otros pares con dHash a distancia ≤5, lo cual **no descarta** escenas tomadas en el mismo lugar o fotos similares con otro encuadre.

La inspección fue visual mediante cuatro hojas de contacto (`artifacts/diagnostics/stock-pilot-audit/contacto_01.jpg` a `contacto_04.jpg`) y revisión ampliada de casos prioritarios. No se generaron etiquetas de verdad-terreno ni porcentajes de stock. Las notas siguientes son **triaje**, no anotaciones verificadas.

## Cola de revisión inicial

| Fotos | Utilidad prevista | Precaución |
|---|---|---|
| `supermarket_021` | Hueco grande en nivel de cereales; primer caso positivo para definir ROI/hueco. | Hay varios niveles: no clasificar toda la foto con un único porcentaje. |
| `supermarket_022` | Zonas parcialmente vacías en bebidas; positivo con envases de distintas alturas. | Espacio libre sobre paquetes bajos no debe contarse automáticamente como faltante. |
| `supermarket_036` | Huecos intermedios y zona inferior muy poco ocupada. | Separar cada nivel; no interpretar sombras tras los envases como huecos. |
| `supermarket_041` | Negativo difícil y caso de regresión. | El detector anterior marcó cartel FUJIFILM y espacio sobre productos como huecos falsos. |
| `supermarket_001`, `002`, `012`, `025`, `026` | Negativos aparentemente llenos para medir falsos avisos. | Confirmar cada nivel: «lleno» no significa todos los píxeles cubiertos. |
| `supermarket_020` | Robustez frente a cristal, reflejos y obstrucción. | Puede requerir `occluded`/`unusable`; no forzar porcentaje. |
| `supermarket_031`, `032` | Revisar posible relación entre escenas de lácteos. | Agrupar si son misma cámara/local; no separarlas entre train y test antes de verificar. |
| `supermarket_004`, `035` | Un solo ejemplar útil. | Duplicado exacto; retirar uno de cualquier evaluación. |
| `grocery_*` (15) | Recortes útiles para observar productos y confusores. | En general no muestran un nivel completo con sus límites laterales; **no** usarlos para evaluar porcentaje de ocupación de góndola completa sin definir claramente una ROI parcial. |

El [inventario completo](../data/stock_ground_truth_v1/inventario_piloto.csv) mantiene las 60 imágenes con estado pendiente. No se asignó `scene_id` ni `split` de forma automática: hacerlo por nombre de archivo daría una falsa garantía de independencia.

## Decisión para el siguiente ciclo

1. Etiquetar primero `021`, `022`, `036` y los negativos `001`, `002` y `041` con la [herramienta local](../tools/stock_annotator/index.html); hacer una segunda revisión visual antes de cambiar `draft` a `reviewed`.
2. Registrar escenas relacionadas y separar por escena; conservar una prueba que no participe en ajuste de umbral ni entrenamiento.
3. Conseguir fotos adicionales de la góndola/cámara objetivo con niveles llenos, cercanos al 30 % y casi vacíos. Estas fotos externas no bastan para afirmar que la alarma funciona en Duoc o en la tienda del cliente.
4. Sólo con anotaciones revisadas, medir error de ocupación, matriz de alertas y falsos avisos. Hasta entonces mantener la alarma deshabilitada.

El documento no atribuye licencia nueva ni autoriza publicar las fotos originales; la copia de trabajo está excluida de Git.

La ejecución posterior del detector sobre la cola se documenta en [Revisión de candidatos del piloto](REVISION_CANDIDATOS_PILOTO.md); sus cajas son propuestas, no etiquetas ni mediciones de ocupación.
