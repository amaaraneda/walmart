# Planificación referencial del MVP

Esta Carta Gantt está expresada por semanas relativas, porque aún no existe un calendario, tamaño de equipo ni fecha de entrega validados. Se ajustará tras la reunión con el cliente y la planificación académica.

| Etapa | S4 | S5 | S6 | S7 | S8 | S9 | S10 | S11 | S12 | Entregable / criterio de salida |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Validación del problema y alcance | X | X |  |  |  |  |  |  |  | Requisitos y criterio de alerta aprobados |
| Estudio de mercado | X | X |  |  |  |  |  |  |  | Comparativo y diferenciador definidos |
| Estrategia de datos y etiquetado | X | X | X |  |  |  |  |  |  | Guía y dataset piloto revisado |
| Línea base de visión |  | X | X | X |  |  |  |  |  | Métricas iniciales reproducibles |
| Desarrollo de servicio MVP |  |  | X | X | X |  |  |  |  | API contenida y trazable |
| Integración e interfaz mínima |  |  |  |  | X | X |  |  |  | Flujo imagen a alerta operativo |
| QA y evaluación en condiciones reales |  |  |  |  |  | X | X |  |  | Informe de métricas y fallos |
| Ajustes y segunda versión |  |  |  |  |  |  | X | X |  | Modelo/umbral aprobados para demo |
| Documentación y manuales | X | X | X | X | X | X | X | X | X | README, instalación y usuario actualizados |
| Preparación y entrega MVP |  |  |  |  |  |  |  | X | X | Demo, evidencia y retrospectiva |

## Hito inmediato: semana 4

- [x] Revisar desafío, conceptos entregados y comunicado de semana 4.
- [x] Crear documentación inicial y repositorio Git.
- [ ] Ejecutar primera reunión y registrar acuerdos/decisiones.
- [ ] Validar perfiles, RF, cálculo de disponibilidad visual y definición de vacío útil.
- [ ] Confirmar infraestructura, imágenes disponibles, privacidad y responsables.
- [ ] Convertir requisitos validados en historias de usuario o casos de uso.
- [ ] Ajustar este plan con fechas reales, responsables y dependencias.

## Riesgos prioritarios

| Riesgo | Impacto | Mitigación inicial |
| --- | --- | --- |
| Pocas imágenes propias o sin permiso de uso | Alto | Gestionar autorización y dataset piloto desde el inicio |
| Ambigüedad de “vacío útil” | Alto | Guía de etiquetado aprobada con ejemplos límite |
| Diferencia entre datos públicos y locales reales | Alto | Reservar evaluación en imágenes Walmart no usadas para entrenar |
| Latencia mayor a 5 segundos | Medio | Medir desde línea base y elegir modelo/tamaño según hardware |
| Alertas erróneas por ángulo o apilamiento | Alto | Etiquetar estos casos y definir rechazo/revisión humana |
