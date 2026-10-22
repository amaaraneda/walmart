# Guion para primera reunión con Walmart

## Objetivo

Validar que cliente y equipo entienden el mismo problema antes de diseñar o entrenar una solución.

## Apertura sugerida

“Entendemos que el objetivo es analizar imágenes reales de góndolas para identificar y cuantificar espacio vacío útil; idealmente por nivel. El MVP debe alertar bajo stock cuando la disponibilidad visual sea inferior al 30 %. Proponemos entregar porcentaje estimado, alerta y evidencia visual. Queremos validar la definición de vacío útil, la fuente de imágenes y el criterio operacional de alerta.”

## Preguntas esenciales

1. ¿Cuál es la decisión operativa que debe habilitar la alerta y quién actúa sobre ella?
2. Confirmamos que la alerta se activa cuando la disponibilidad visual es menor al 30 %. ¿Cómo debe estimarse esa disponibilidad para su operación y debe variar por categoría?
3. ¿Cuál es la unidad de análisis y qué ejemplos representan vacío útil/no útil?
4. ¿Las imágenes llegan desde celular, cámaras existentes o una fuente de prueba? ¿Con qué resolución, frecuencia y ángulo?
5. ¿Qué imágenes se pueden usar, almacenar y etiquetar? ¿Qué restricciones de privacidad y seguridad aplican?
6. ¿Qué latencia de 5 segundos se espera y en qué equipo/red se medirá?
7. ¿Qué infraestructura, sistemas, base de datos, nube o políticas tecnológicas ya existen?
8. ¿Qué error es más costoso: alertar una góndola que no requiere acción u omitir una que sí la requiere?
9. ¿Cómo validarán que el resultado es correcto y quién será contraparte de negocio/técnica?

## Resultado que se debe registrar

- Definición aprobada de espacio vacío útil.
- Alcance del MVP y funcionalidades excluidas.
- Usuarios y responsables.
- Umbral, persistencia y canal de alarma.
- Datos disponibles, permisos, formato y muestra piloto.
- Restricciones de infraestructura, privacidad y despliegue.
- Criterios de aceptación y siguiente reunión.
