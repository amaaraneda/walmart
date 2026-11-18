-- Modelo físico inicial del MVP
-- Proyecto: Detección de espacios vacíos en góndolas
-- Motor objetivo: PostgreSQL 16 o compatible

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE usuario (
    usuario_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    correo VARCHAR(254) NOT NULL UNIQUE,
    rol VARCHAR(40) NOT NULL CHECK (rol IN ('reponedor', 'supervisor', 'administrador_tecnico')),
    creado_en TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE gondola (
    gondola_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    codigo VARCHAR(80) NOT NULL UNIQUE,
    local VARCHAR(120),
    descripcion VARCHAR(255)
);

CREATE TABLE captura (
    captura_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    gondola_id UUID REFERENCES gondola(gondola_id),
    creada_por UUID REFERENCES usuario(usuario_id),
    evidencia_uri TEXT NOT NULL,
    hash_sha256 CHAR(64) NOT NULL UNIQUE,
    estado_privacidad VARCHAR(30) NOT NULL DEFAULT 'pendiente_revision'
        CHECK (estado_privacidad IN ('permitida', 'pendiente_revision', 'restringida')),
    capturada_en TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE modelo_version (
    modelo_version_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nombre VARCHAR(100) NOT NULL,
    version VARCHAR(80) NOT NULL,
    framework VARCHAR(80) NOT NULL,
    estado VARCHAR(30) NOT NULL DEFAULT 'candidato'
        CHECK (estado IN ('candidato', 'evaluado', 'aprobado', 'retirado')),
    metricas_uri TEXT,
    UNIQUE (nombre, version)
);

CREATE TABLE configuracion_alerta (
    configuracion_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    umbral_porcentaje NUMERIC(5,2) NOT NULL CHECK (umbral_porcentaje >= 0 AND umbral_porcentaje <= 100),
    vigente_desde TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    vigente_hasta TIMESTAMPTZ,
    creada_por UUID REFERENCES usuario(usuario_id),
    CHECK (vigente_hasta IS NULL OR vigente_hasta > vigente_desde)
);

CREATE TABLE analisis (
    analisis_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    captura_id UUID NOT NULL REFERENCES captura(captura_id),
    modelo_version_id UUID NOT NULL REFERENCES modelo_version(modelo_version_id),
    configuracion_id UUID NOT NULL REFERENCES configuracion_alerta(configuracion_id),
    estado VARCHAR(30) NOT NULL CHECK (estado IN ('completado', 'requiere_revision', 'fallido')),
    latencia_ms INTEGER NOT NULL CHECK (latencia_ms >= 0),
    creado_en TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE resultado_nivel (
    resultado_nivel_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analisis_id UUID NOT NULL REFERENCES analisis(analisis_id) ON DELETE CASCADE,
    nivel SMALLINT NOT NULL CHECK (nivel >= 1),
    cobertura_porcentaje NUMERIC(5,2) NOT NULL CHECK (cobertura_porcentaje >= 0 AND cobertura_porcentaje <= 100),
    confianza NUMERIC(5,4) CHECK (confianza >= 0 AND confianza <= 1),
    evidencia_uri TEXT,
    UNIQUE (analisis_id, nivel)
);

CREATE TABLE alerta (
    alerta_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    resultado_nivel_id UUID NOT NULL UNIQUE REFERENCES resultado_nivel(resultado_nivel_id),
    estado VARCHAR(30) NOT NULL DEFAULT 'pendiente'
        CHECK (estado IN ('pendiente', 'en_revision', 'confirmada', 'descartada')),
    creada_en TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE revision (
    revision_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    alerta_id UUID REFERENCES alerta(alerta_id),
    analisis_id UUID REFERENCES analisis(analisis_id),
    revisada_por UUID NOT NULL REFERENCES usuario(usuario_id),
    decision VARCHAR(30) NOT NULL CHECK (decision IN ('confirmada', 'descartada', 'requiere_revision')),
    comentario TEXT,
    revisada_en TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (alerta_id IS NOT NULL OR analisis_id IS NOT NULL)
);

CREATE INDEX ix_analisis_captura ON analisis(captura_id);
CREATE INDEX ix_resultado_analisis ON resultado_nivel(analisis_id);
CREATE INDEX ix_alerta_estado ON alerta(estado);
