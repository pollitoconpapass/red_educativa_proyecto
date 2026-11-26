
-- ============================================
-- 1. CREACIÓN DE LA BASE DE DATOS
-- ============================================

CREATE DATABASE IF NOT EXISTS red_educativa
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE red_educativa;


-- ============================================
-- 2. TABLA: USUARIO
-- ============================================

CREATE TABLE IF NOT EXISTS USUARIO (
    id_usuario INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    correo VARCHAR(150) NOT NULL UNIQUE,
    clave_hash VARCHAR(255) NOT NULL,
    rol VARCHAR(30) NOT NULL
) ENGINE=InnoDB;


-- ============================================
-- 3. TABLA: ESTUDIANTE
-- ============================================

CREATE TABLE IF NOT EXISTS ESTUDIANTE (
    id_estudiante INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT UNSIGNED NOT NULL UNIQUE,
    codigo_universitario VARCHAR(50) NOT NULL,

    CONSTRAINT fk_estudiante_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES USUARIO(id_usuario)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;


-- ============================================
-- 4. TABLA: DOCENTE
-- ============================================

CREATE TABLE IF NOT EXISTS DOCENTE (
    id_docente INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT UNSIGNED NOT NULL UNIQUE,
    area_academica VARCHAR(100),

    CONSTRAINT fk_docente_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES USUARIO(id_usuario)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;


-- ============================================
-- 5. TABLA: DOCUMENTO
-- ============================================

CREATE TABLE IF NOT EXISTS DOCUMENTO (
    id_documento INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_usuario_autor INT UNSIGNED NOT NULL,
    nombre_archivo VARCHAR(255) NOT NULL,
    tamano_bytes BIGINT UNSIGNED NOT NULL,
    fecha_publicacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_documento_usuario
        FOREIGN KEY (id_usuario_autor)
        REFERENCES USUARIO(id_usuario)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    INDEX idx_documento_autor (id_usuario_autor),
    INDEX idx_documento_fecha (fecha_publicacion)
) ENGINE=InnoDB;


-- ============================================
-- 6. TABLA: DOCUMENTO_CONTENIDO
-- El binario del documento, en una tabla aparte
-- para no arrastrarlo en los listados.
-- ============================================

CREATE TABLE IF NOT EXISTS DOCUMENTO_CONTENIDO (
    id_documento INT UNSIGNED PRIMARY KEY,
    contenido MEDIUMBLOB NOT NULL,

    CONSTRAINT fk_contenido_documento
        FOREIGN KEY (id_documento)
        REFERENCES DOCUMENTO(id_documento)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;


-- ============================================
-- 7. TABLA: ACTIVIDAD
-- ============================================

CREATE TABLE IF NOT EXISTS ACTIVIDAD (
    id_actividad INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_docente INT UNSIGNED NOT NULL,
    titulo VARCHAR(200) NOT NULL,
    fecha_limite DATETIME,

    CONSTRAINT fk_actividad_docente
        FOREIGN KEY (id_docente)
        REFERENCES DOCENTE(id_docente)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    INDEX idx_actividad_docente (id_docente)
) ENGINE=InnoDB;


-- ============================================
-- 8. TABLA: PERMISO_ACCESO
-- ============================================

CREATE TABLE IF NOT EXISTS PERMISO_ACCESO (
    id_permiso INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT UNSIGNED NOT NULL,
    id_documento INT UNSIGNED NOT NULL,
    tipo_permiso VARCHAR(30) NOT NULL,

    CONSTRAINT fk_permiso_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES USUARIO(id_usuario)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_permiso_documento
        FOREIGN KEY (id_documento)
        REFERENCES DOCUMENTO(id_documento)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    INDEX idx_permiso_usuario (id_usuario),
    INDEX idx_permiso_documento (id_documento),

    CONSTRAINT uq_permiso_usuario_documento
        UNIQUE (id_usuario, id_documento)
) ENGINE=InnoDB;


-- ============================================
-- 9. TABLA: ENTREGA
-- ============================================

CREATE TABLE IF NOT EXISTS ENTREGA (
    id_entrega INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_actividad INT UNSIGNED NOT NULL,
    id_estudiante INT UNSIGNED NOT NULL,
    id_documento INT UNSIGNED NOT NULL,
    fecha_entrega DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_entrega_actividad
        FOREIGN KEY (id_actividad)
        REFERENCES ACTIVIDAD(id_actividad)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_entrega_estudiante
        FOREIGN KEY (id_estudiante)
        REFERENCES ESTUDIANTE(id_estudiante)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_entrega_documento
        FOREIGN KEY (id_documento)
        REFERENCES DOCUMENTO(id_documento)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    INDEX idx_entrega_actividad (id_actividad),
    INDEX idx_entrega_estudiante (id_estudiante),
    INDEX idx_entrega_documento (id_documento),

    CONSTRAINT uq_entrega_actividad_estudiante
        UNIQUE (id_actividad, id_estudiante)
) ENGINE=InnoDB;


-- ============================================
-- 10. TABLA: AUDITORIA
-- ============================================

CREATE TABLE IF NOT EXISTS AUDITORIA (
    id_auditoria BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT UNSIGNED NOT NULL,
    accion VARCHAR(50) NOT NULL,
    entidad VARCHAR(30) NOT NULL,
    id_entidad INT UNSIGNED,
    fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_auditoria_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES USUARIO(id_usuario)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    INDEX idx_auditoria_usuario_fecha (id_usuario, fecha),
    INDEX idx_auditoria_fecha (fecha)
) ENGINE=InnoDB;


-- ============================================
-- 11. VERIFICACIÓN DE TABLAS
-- ============================================

SHOW TABLES;
