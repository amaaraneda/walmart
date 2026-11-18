# Sprint Backlog

Proyecto Góndola Visión · Fase 2 final · Corte del 17 de noviembre de 2026

Los sprints 1 a 3 agrupan incrementos observables a partir del código, el informe intermedio y el seguimiento semanal. Las asignaciones corresponden a la distribución de trabajo propuesta para el cierre. Los IDs remiten al [Product Backlog](Product%20Backlog.md).

## Sprint 1 · Preparación y detección

Objetivo: obtener un primer flujo reproducible de entrada a detecciones de productos.

| Historias | Trabajo seleccionado | Responsable de referencia | Resultado documentado |
|---|---|---|---|
| HU-01, HU-02 | Implementar carga y validación de fotografías. | Amaro | API y formulario operativos en beta. |
| HU-09 | Normalizar el dataset de productos y registrar su estructura. | Josseph | Existe dataset normalizado. Faltan referencias humanas de ocupación. |
| HU-03 | Probar el detector y exponer las cajas resultantes. | Josseph | Detecciones y resultados comparativos disponibles. |

## Sprint 2 · Integración del MVP

Objetivo: recorrer desde la web el análisis de una foto y entender el resultado.

| Historias | Trabajo seleccionado | Responsable de referencia | Resultado documentado |
|---|---|---|---|
| HU-03, HU-07 | Mostrar la imagen anotada y permitir elegir el modelo. | Amaro | Flujo de análisis y estado del modelo visibles. Falta registro de latencia por análisis. |
| HU-04, HU-06 | Calcular la ocupación frontal por nivel y reconocer escenas no evaluables. | Josseph | Estimador experimental con abstención. Falta registro de revisión humana. |
| F2-01, F2-02 | Demostrar login y gestión de usuarios en la interfaz. | Amaro | Prototipo en navegador. Autenticación y persistencia pendientes. |
| HU-08 | Preparar arranque del MVP y configuración Docker. | Amaro | Configuración disponible. Falta evidencia de prueba en el entorno de destino. |

## Sprint 3 · Evaluación y cierre

Objetivo: dejar una demo verificable y relacionar sus resultados con los pendientes técnicos.

| Historias | Trabajo seleccionado | Responsable de referencia | Resultado al corte |
|---|---|---|---|
| HU-04, HU-06 | Comparar casos favorables, difíciles y no evaluables. | Josseph | El barrido previo está documentado: 39 salidas numéricas y 5 abstenciones en 44 escenas. |
| HU-05, F2-03 | Contrastar la estimación cerca del umbral del 30 %. | Josseph | Hay lógica de candidato por nivel. Sin validación contra anotaciones humanas, la alerta sigue desactivada. |
| F2-04 | Consolidar modelos de datos, diccionario y SQL. | Amaro | Esquema, carga ficticia, consulta y restricciones verificados en PostgreSQL embebido. |
| F2-05 | Consolidar la demo y registrar la revisión del cliente. | Amaro | Demo disponible según el equipo. La respuesta del cliente está por verificar. |

## Siguiente incremento · Trabajo seleccionado

| Orden | Historias | Acción y evidencia de término | Responsable propuesto |
|---:|---|---|---|
| 1 | HU-09, F2-03 | Anotar primero un piloto de seis escenas, incluyendo niveles con baja ocupación; contrastar anotaciones y calcular error por nivel. | Josseph |
| 2 | HU-08 | Ejecutar la demo en el equipo objetivo y guardar resultado de salud, inferencia y tiempos. | Amaro |
| 3 | F2-01, F2-02 | Integrar la persistencia de usuarios con el backend y comprobar el control de acceso por rol. | Amaro |
| 4 | HU-05 | Revisar falsos avisos y omisiones por nivel. Decidir la activación sólo después de evaluar los resultados. | Josseph y Amaro |
