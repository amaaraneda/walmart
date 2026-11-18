SELECT g.codigo, n.nivel, n.cobertura_porcentaje, cfg.umbral_porcentaje,
       n.cobertura_porcentaje < cfg.umbral_porcentaje AS bajo_umbral,
       al.estado AS estado_alerta, r.decision
FROM resultado_nivel n
JOIN analisis a USING (analisis_id)
JOIN captura c USING (captura_id)
JOIN gondola g USING (gondola_id)
JOIN configuracion_alerta cfg USING (configuracion_id)
LEFT JOIN alerta al USING (resultado_nivel_id)
LEFT JOIN revision r ON r.alerta_id = al.alerta_id AND r.analisis_id = a.analisis_id
WHERE g.codigo = 'DEMO-01'
ORDER BY n.nivel;
