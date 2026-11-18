-- Datos ficticios. Ejecutar una vez en una base de prueba vacía,
-- después de Script.sql. El registro de alerta simula un caso de BD.
BEGIN;
INSERT INTO usuario (usuario_id, correo, rol) VALUES
('10000000-0000-4000-8000-000000000001', 'operador@example.invalid', 'reponedor'),
('10000000-0000-4000-8000-000000000002', 'supervisor@example.invalid', 'supervisor');
INSERT INTO gondola (gondola_id, codigo, local) VALUES
('20000000-0000-4000-8000-000000000001', 'DEMO-01', 'Local ficticio');
INSERT INTO captura (captura_id, gondola_id, creada_por, evidencia_uri, hash_sha256) VALUES
('30000000-0000-4000-8000-000000000001', '20000000-0000-4000-8000-000000000001',
 '10000000-0000-4000-8000-000000000001', 'urn:demo:captura:1', repeat('a',64));
INSERT INTO modelo_version (modelo_version_id, nombre, version, framework) VALUES
('40000000-0000-4000-8000-000000000001', 'Detector ficticio', 'fixture-1', 'YOLO');
INSERT INTO configuracion_alerta (configuracion_id, umbral_porcentaje) VALUES
('50000000-0000-4000-8000-000000000001', 30);
INSERT INTO analisis (analisis_id, captura_id, modelo_version_id, configuracion_id, estado, latencia_ms) VALUES
('60000000-0000-4000-8000-000000000001', '30000000-0000-4000-8000-000000000001',
 '40000000-0000-4000-8000-000000000001', '50000000-0000-4000-8000-000000000001', 'requiere_revision', 700);
INSERT INTO resultado_nivel (resultado_nivel_id, analisis_id, nivel, cobertura_porcentaje) VALUES
('70000000-0000-4000-8000-000000000001', '60000000-0000-4000-8000-000000000001', 1, 24.50),
('70000000-0000-4000-8000-000000000002', '60000000-0000-4000-8000-000000000001', 2, 85.00);
INSERT INTO alerta (alerta_id, resultado_nivel_id, estado) VALUES
('80000000-0000-4000-8000-000000000001', '70000000-0000-4000-8000-000000000001', 'en_revision');
INSERT INTO revision (alerta_id, analisis_id, revisada_por, decision, comentario) VALUES
('80000000-0000-4000-8000-000000000001', '60000000-0000-4000-8000-000000000001',
 '10000000-0000-4000-8000-000000000002', 'requiere_revision', 'Caso ficticio de prueba');
COMMIT;
