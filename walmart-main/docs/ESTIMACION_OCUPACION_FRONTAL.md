# Porcentaje visual experimental de góndola

La API ya calcula un **porcentaje estimado de frente visible ocupado** sin pedir al usuario que delimite manualmente la góndola. No es porcentaje de unidades de inventario ni una alerta validada.

## Cálculo

1. YOLO detecta envases visibles. Se agrupan las bases (`y2`) de varias cajas para proponer niveles horizontales. No se aceptan fragmentos aislados de riel como un nivel completo; se excluye la fila superior cortada por el borde de la foto.
2. Sólo se mide si las detecciones de la foto permiten inferir que el frente abarca casi todo el ancho. Se descarta un margen lateral de 2 %. Cuando el ancho no es observable, se devuelve `null` con un motivo, no un cero ni un 100 %.
3. Por nivel: `ocupación = 100 × ancho de la unión de proyecciones horizontales de cajas de producto / ancho útil estimado`. Una caja superpuesta no suma dos veces. El promedio de niveles medidos es `occupancy_percent` de la imagen. Esto mide **frente exhibido**, no número de cajas, área completa de la fotografía ni unidades físicas detrás de la primera fila.
4. `low_stock_candidate` señala un nivel cuyo estimado cae bajo el umbral, pero **no envía aviso**. `low_stock_alert` sigue `null`, `threshold_applied=false` y `review_required=true`. Las cajas del detector independiente de huecos siguen siendo diagnósticas; todavía no modifican el porcentaje.

## Comprobación funcional local

Con el modelo del compañero y las fotos del piloto, el flujo completo de la API devolvió: `supermarket_021`: 82,8 % en cuatro frentes propuestos; `022`: 85,1 % en cuatro; `041`: 89,7 % en tres; `001`: no evaluable porque no se estabilizaron filas. **Son salidas de software, no exactitudes medidas contra verdad-terreno.** Se excluyó una fila de `021` cortada por el borde superior. Las previsualizaciones diagnósticas están en `artifacts/diagnostics/visual-occupancy/`.

## Limitaciones antes de activar el 30 %

- Un producto omitido por YOLO parece espacio libre; una caja falsa parece ocupación. El detector de huecos tampoco es fiable por sí solo: confundió un cartel y omitió zonas parcialmente vacías.
- El supuesto de frente casi completo excluye fotos lejanas, oblicuas o donde la góndola ocupa una parte pequeña de la imagen. Una góndola enteramente vacía sin productos tampoco permite inferir automáticamente su ancho con este método y queda `no evaluable`.
- Promediar niveles puede ocultar uno muy vacío; por eso la web muestra cada nivel y el candidato bajo umbral se evalúa **por nivel**, no por promedio global.
- El umbral y la métrica de ancho frontal deben contrastarse con [anotaciones humanas por nivel](PROTOCOLO_ETIQUETADO_GONDOLAS.md), separadas por escena. Medir error absoluto de porcentaje, precisión/recall de candidatos bajo 30 %, falsos avisos en niveles llenos y latencia en el PC objetivo. Sólo después decidir si la alerta puede activarse.
