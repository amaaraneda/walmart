# Ajuste fino del detector: Shelf v3

El 18-10-2026 se probó continuar desde el checkpoint activo YOLO26n con todas las capas entrenables, entrada de 640 px, AdamW (`lr0=0.0003`), lote 4 y las mismas 734 imágenes de entrenamiento de `shelf_products_v2`. El mejor checkpoint apareció en la época 6. Se cerró la corrida después de ocho épocas completas porque las épocas 7 y 8 no lo superaron y el tiempo por época aumentaba. Los resultados reproducibles están en `artifacts/runs/shelf-v3-unfrozen-640/results.csv` y los pesos candidatos en `artifacts/candidates/shelf-v3-unfrozen-640/`.

| Partición y métrica | Modelo activo | Candidato v3 |
|---|---:|---:|
| Validación: mAP50 | 0,3315 | 0,3723 |
| Validación: mAP50–95 | 0,1141 | 0,1590 |
| Validación: precisión / recall | 0,4172 / 0,3913 | 0,4447 / 0,3884 |
| Prueba: mAP50 | 0,4773 | 0,4628 |
| Prueba: mAP50–95 | 0,1578 | 0,1573 |
| Prueba: precisión / recall | 0,5043 / 0,5169 | 0,4650 / 0,5153 |

El candidato **no se activó**: la mejora en validación no se sostuvo en prueba. La API y la página conservan el checkpoint anterior. La orden de activación fue ensayada y rechazó el candidato antes de cambiar archivos. Los informes completos, incluidos hashes de ambos pesos, están en `validation-comparison.json` y `test-comparison.json` dentro del directorio del candidato. No se harán nuevos ajustes guiados por estas imágenes de prueba sin reservar otro conjunto independiente.

En la imagen de referencia `045_8`, con entrada de 640 px y confianza ≥ 0,25, el activo produjo 72 propuestas y coincidió con las 46 etiquetas; el candidato produjo 59 y coincidió con 45. Con confianza ≥ 0,50, el candidato coincidió con 33 etiquetas frente a 22 del activo. Esto sugiere mejor puntuación de varias detecciones, pero también una omisión adicional al umbral usado por la interfaz. Hay productos visibles sin anotar, sobre todo en la franja inferior, por lo que el número de cajas no equivale por sí solo a precisión real.

La limitación principal es de datos: las 29 imágenes de validación representan sólo cuatro escenas base y las 30 de prueba, otras cuatro. Se requieren fotografías nuevas de góndolas distintas, con cajas completas y revisión humana de omisiones y falsos positivos. Para el objetivo de alerta al 30 % hacen falta, además, límites del área útil y máscaras o regiones de vacío anotadas; entrenar productos no valida ocupación ni stock.

Siguiente iteración recomendada:

1. Revisar y completar anotaciones de las escenas actuales, comenzando por `045_8`, sin mezclar esas correcciones con métricas históricas.
2. Recolectar escenas nuevas con vacíos reales, iluminación, ángulos y niveles de llenado diversos; separar por góndola/escena antes de generar aumentos.
3. Definir un conjunto de prueba nuevo e intocable antes de comparar arquitecturas o hiperparámetros.
4. Entrenar detección de productos y vacío/área útil como tareas evaluadas por separado. Activar el aviso del 30 % sólo tras validar el porcentaje contra anotaciones locales.
