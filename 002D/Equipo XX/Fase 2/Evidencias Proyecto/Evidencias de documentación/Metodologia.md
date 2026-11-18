# Metodología de trabajo

Proyecto Góndola Visión · Fase 2 final · Corte del 17 de noviembre de 2026

Declaramos un enfoque ágil e iterativo inspirado en Scrum, adaptado a un equipo de dos personas. Organizamos el trabajo mediante un Product Backlog priorizado, objetivos por sprint y revisión del incremento con evidencia. Para el cierre agrupamos los hitos técnicos registrados en tres sprints de referencia. Esta reconstrucción documenta la evolución del MVP. Las ceremonias y fechas de los sprints se formalizan a partir de este corte.

## Justificación

El rendimiento de un detector en un conjunto de prueba no predice por sí solo la calidad de una alerta. Perspectiva, reflejos y productos omitidos pueden cambiar la estimación de frente ocupado. Por eso dividimos el proyecto en incrementos que puedan probarse por separado: primero detectar productos, luego mostrar resultados en la aplicación y finalmente evaluar la ocupación por nivel. Así podemos entregar una demo utilizable mientras medimos el riesgo de automatizar avisos de reposición.

## Aplicación del enfoque

| Actividad | Cómo se organiza | Evidencia |
|---|---|---|
| Priorizar | Ordenar historias por valor para la demo, dependencias y riesgo técnico. | [Product Backlog](Product%20Backlog.md) |
| Planificar | Seleccionar historias que cumplan un objetivo común, identificar su responsable y acordar el criterio de salida. | [Sprint Backlog](Sprint%20Backlog.md) |
| Desarrollar y probar | Integrar cambios en incrementos pequeños y documentar el comando de prueba, entradas y resultados. | Código, historial Git y pruebas automatizadas |
| Revisar | Mostrar el flujo con una imagen evaluable y otra no evaluable. Registrar los bloqueos y la retroalimentación que llegue del cliente. | Demo e informes de avance |
| Mejorar | Registrar qué mantener, qué cambiar y cómo verificar cada acción en el siguiente corte. | [Retrospectivas](Retrospectivas.md) |

## Criterio de término

Una historia queda terminada dentro de su alcance cuando cumple el criterio de aceptación, cuenta con evidencia reproducible y sus límites están documentados. Un resultado experimental conserva ese estado mientras falte validación. Una función simulada en la interfaz queda como demo local hasta contar con respaldo del servidor cuando corresponda.

La alerta bajo 30 % requiere imágenes con anotación humana, evaluación de falsos avisos y omisiones por nivel, y un criterio de aceptación acordado antes de activar notificaciones.
