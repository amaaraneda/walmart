# Guion de demostración funcional intermedia

**Duración objetivo:** 7 minutos. Grabar pantalla y narración reales en el PC donde corra la aplicación; verificar que no aparezcan credenciales privadas ni fotos sin permiso de difusión. Esta guía **no es el video**.

| Tiempo | Acción en pantalla | Explicación honesta |
|---|---|---|
| 0:00–0:40 | Mostrar raíz del proyecto y `README.md`. | Objetivo: disponibilidad visual, no inventario físico ni identificación de SKU. |
| 0:40–1:30 | Iniciar con `INICIAR_MVP.cmd` o `docker compose up --build`; abrir `/api/health`. | Verificar pesos cargados y estado experimental. No afirmar autenticación real. |
| 1:30–2:20 | Entrar a la web con cuenta de demostración y abrir Análisis visual. | Login/CRUD actuales viven en el navegador; son prototipo. |
| 2:20–3:30 | Analizar `supermarket_027.jpg` si está autorizado. | Mostrar cajas de producto, 4 niveles y 98,8 % experimental; no llamarlo porcentaje de acierto. |
| 3:30–4:50 | Analizar `supermarket_021.jpg`. | Mostrar hueco visible y salida global de 82,8 %. Explicar por qué el promedio puede ocultar un faltante local. |
| 4:50–5:50 | Analizar `supermarket_001.jpg`. | Mostrar «no evaluable», aunque hay productos detectados; es mejor abstenerse que inventar un porcentaje. |
| 5:50–6:40 | Mostrar opción de modelo y, si procede, cajas diagnósticas de huecos. | Comparar sólo detección de producto. Las propuestas de vacío no generan alarmas. |
| 6:40–7:20 | Mostrar README/informe y cierre. | Próximo paso: etiquetar ROI y huecos, medir error y falsos avisos, probar en PC Duoc. |

Antes de entregar: grabar en 1080p o resolución legible, mantener cada resultado en pantalla el tiempo suficiente, comprobar audio y duración entre 5 y 10 minutos, y guardar el archivo o enlace autorizado junto a la documentación del informe. No subir fotos originales, pesos ni video público sin verificar permisos del cliente y de las fuentes.
