# Retrospectivas de Fase 2

Proyecto Góndola Visión · Revisión documental al 17 de noviembre de 2026

Estas retrospectivas reconstruyen los aprendizajes de tres incrementos con base en resultados y dificultades documentados. Las acciones de mejora se formulan para el siguiente corte.

## Sprint 1 · Preparación y detección

- **Mantener:** conservar un dataset normalizado y separar las escenas al evaluar los modelos. El informe intermedio compara detectores usando las mismas 30 imágenes de prueba.
- **Cambiar:** registrar desde el inicio dos tipos de referencia. Las cajas de producto permiten evaluar detección. La ocupación frontal requiere marcar los niveles y su frente útil.
- **Acción:** Josseph preparará un piloto de seis escenas anotadas. Se verificará la separación por escena y se revisarán las anotaciones antes de usarlas para medir error. Vinculado a HU-09 y F2-03.

## Sprint 2 · Integración del MVP

- **Mantener:** mostrar al usuario la fotografía anotada y el resultado por nivel. Los casos sin geometría suficiente pueden reportarse como no evaluables.
- **Cambiar:** incorporar al recorrido de demo escenas que puedan revelar falsos avisos: perspectiva oblicua, un nivel con hueco visible y una imagen que el sistema deba rechazar o declarar no evaluable.
- **Acción:** Amaro preparará un recorrido reproducible que indique imagen, modelo, resultado esperado y resultado observado. Josseph seleccionará las escenas y revisará los errores del estimador. Vinculado a HU-04, HU-06 y HU-08.

## Sprint 3 · Evaluación y cierre

- **Mantener:** distinguir detección, estimación y alerta en la documentación. En el barrido previo se obtuvo un porcentaje en 39 de 44 escenas. Esa cifra refleja cuántas escenas pudo evaluar el estimador.
- **Cambiar:** reunir en cada corte evidencia de ejecución de la app y de la BD. Tratar los resultados cercanos al umbral del 30 % como casos que requieren evaluación antes de emitir un aviso.
- **Acción:** el [ensayo SQL con datos ficticios](../Evidencias%20de%20sistema/Base%20de%20datos/Resultado%20base%20de%20datos.json) ya está registrado. Amaro documentará las pruebas en el equipo objetivo. Josseph calculará el error por nivel y los falsos avisos y omisiones cuando haya etiquetas humanas. Vinculado a HU-05, HU-08, F2-03 y F2-04.

La próxima revisión verificará cada acción con un enlace a la evidencia o con el motivo por el que sigue abierta.
