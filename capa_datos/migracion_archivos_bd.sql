-- =====================================================
-- MIGRACIÓN: ARCHIVOS EN LA BASE DE DATOS
-- Ejecutar en DBeaver sobre red_educativa.
--
-- FASE A: crear DOCUMENTO_CONTENIDO y dejar la columna
-- clave_objeto_OCI como nullable, para que el código
-- nuevo y el viejo convivan durante el despliegue.
--
-- Después de la fase A, desde la VPS de aplicación:
--     cd api && python3 migrar_archivos.py
--
-- La FASE B (borrar la columna) va al final del archivo
-- y solo se ejecuta cuando el código nuevo esté
-- desplegado y las descargas funcionen.
-- =====================================================

USE red_educativa;


-- =====================================================
-- 0. REQUISITOS DEL SERVIDOR
--
-- PyMySQL escapa el binario del archivo, así que 10 MB
-- pueden viajar como ~20-40 MB de paquete. Este valor
-- debe ser >= 67108864.
-- =====================================================

SHOW VARIABLES LIKE 'max_allowed_packet';

-- Solo afecta hasta el próximo reinicio de MySQL.
-- Déjalo también en my.cnf si es necesario.
-- SET GLOBAL max_allowed_packet = 67108864;


-- =====================================================
-- 1. TABLA DE CONTENIDO (1:1 con DOCUMENTO)
-- =====================================================

CREATE TABLE IF NOT EXISTS DOCUMENTO_CONTENIDO (
    id_documento INT UNSIGNED PRIMARY KEY,
    contenido MEDIUMBLOB NOT NULL,

    CONSTRAINT fk_contenido_documento
        FOREIGN KEY (id_documento)
        REFERENCES DOCUMENTO(id_documento)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;


-- =====================================================
-- 2. COLUMNA LEGACY NULLABLE
--
-- El código nuevo inserta sin clave_objeto_OCI. En modo
-- estricto MySQL rechazaría el INSERT si sigue NOT NULL.
-- =====================================================

ALTER TABLE DOCUMENTO
    MODIFY clave_objeto_OCI VARCHAR(500) NULL;


-- =====================================================
-- 3. VERIFICACIÓN ANTES DE MIGRAR
--
-- Aquí debe aparecer la fila del archivo real que está
-- en api/almacenamiento/ de la VPS de aplicación.
-- =====================================================

SELECT id_documento, nombre_archivo, clave_objeto_OCI
FROM DOCUMENTO
ORDER BY id_documento;

SHOW TABLES;


-- =====================================================
-- FASE B — EJECUTAR DESPUES DE COMPROBAR FASE A
--
-- Requisitos: código nuevo desplegado, migrar_archivos.py
-- ejecutado y esta consulta sin filas (o solo con filas
-- que aceptaste dejar sin archivo):
--
SELECT d.id_documento, d.nombre_archivo
FROM DOCUMENTO d
LEFT JOIN DOCUMENTO_CONTENIDO c
        ON c.id_documento = d.id_documento
WHERE c.id_documento IS NULL;
-- =====================================================

ALTER TABLE DOCUMENTO DROP COLUMN clave_objeto_OCI;
SHOW COLUMNS FROM DOCUMENTO; 
SELECT COUNT(*) FROM DOCUMENTO_CONTENIDO; 
