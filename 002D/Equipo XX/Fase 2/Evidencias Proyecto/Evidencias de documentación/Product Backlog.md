# Product Backlog

Proyecto Góndola Visión · Fase 2 final · Corte del 17 de noviembre de 2026

Los identificadores HU-01 a HU-10 y F2-01 a F2-02 se conservan para cruzar este backlog con el [seguimiento semanal](RESUMEN%20Estado%20de%20Avance%20Casos%20de%20Uso.xlsx). El orden refleja la prioridad al cierre y las dependencias. Los IDs F2-03 a F2-05 incorporan la validación de ocupación, la prueba de base de datos y el seguimiento de la demo.

| Orden | ID | Historia o necesidad | Criterio de aceptación | Estado al corte |
|---:|---|---|---|---|
| 1 | HU-01 | Como reponedor, quiero cargar una foto de góndola para analizar su frente visible. | Puedo cargar una foto válida y abrir su resultado desde la interfaz. | Beta funcional |
| 2 | HU-02 | Como operador, quiero que el sistema explique por qué no puede procesar una imagen. | La API rechaza archivos incompatibles, dañados o fuera de límites con un mensaje claro. | Beta funcional |
| 3 | HU-03 | Como reponedor, quiero ver los productos detectados para interpretar el análisis. | La web muestra la foto anotada y el modelo usado. | Beta funcional |
| 4 | HU-04 | Como supervisor, quiero ver la ocupación frontal por nivel. | Los niveles medibles muestran un porcentaje experimental. Si falta evidencia, la salida indica «No evaluable». | Experimental |
| 5 | HU-09 | Como equipo, quiero un dataset maestro reproducible. | Existe un manifiesto versionado; se documentan duplicados, particiones y permisos. Para validar ocupación se añaden anotaciones humanas por nivel. | Parcial. Dataset de productos normalizado; anotaciones de ocupación pendientes |
| 6 | F2-03 | Como equipo, quiero validar la estimación de ocupación por nivel. | Un conjunto reservado por escena permite reportar error en puntos porcentuales, tasa de abstención y confusión bajo 30 %. | Pendiente de anotaciones humanas |
| 7 | HU-06 | Como supervisor, quiero revisar casos ambiguos y registrar mi decisión. | Los casos dudosos están señalados y la decisión queda vinculada al análisis. | Parcial. La interfaz señala revisión; falta registro persistente |
| 8 | HU-08 | Como administrador, quiero ejecutar el MVP con Docker. | La demo arranca en el equipo objetivo con pesos autorizados. Una foto se procesa y la evidencia queda registrada. | Parcial. Docker disponible; prueba en destino sin acreditar |
| 9 | HU-07 | Como administrador, quiero consultar versión y latencia de cada análisis. | Cada resultado identifica el modelo utilizado y registra la latencia de la solicitud. | Parcial. Modelo visible; falta trazabilidad de latencia por análisis |
| 10 | HU-05 | Como supervisor, quiero recibir un aviso cuando un nivel quede bajo 30 %. | Se valida el umbral por nivel y se verifica que la aplicación emita el aviso en casos elegibles. | Pendiente de F2-03. Candidato técnico disponible |
| 11 | F2-01 | Como usuario, quiero iniciar sesión con los permisos de mi rol. | El servidor autentica la sesión e impide acciones de roles no autorizados. | Demo local en navegador |
| 12 | F2-02 | Como administrador, quiero crear, consultar, editar y desactivar usuarios. | Los cambios se guardan en BD y se conservan al reiniciar el servicio. | Demo local en navegador |
| 13 | F2-04 | Como equipo, quiero probar la base de datos documentada. | Se ejecuta el esquema en un entorno de prueba, se cargan datos ficticios y se verifican consultas y restricciones. | Verificado en PostgreSQL embebido con datos ficticios |
| 14 | HU-10 | Como revisor, quiero registrar correcciones que sirvan para mejorar el modelo. | Cada corrección queda asociada a la imagen, el nivel y el responsable, y se puede exportar para revisión. | Pendiente de persistencia y flujo de revisión |
| 15 | F2-05 | Como equipo, quiero revisar la retroalimentación del cliente sobre la demo. | Cada observación recibida se vincula con una historia, una decisión y un estado. | Por verificar con evidencia de entrega y respuesta |
