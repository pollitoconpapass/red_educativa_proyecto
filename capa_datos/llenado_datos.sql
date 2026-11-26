
-- =====================================================
-- PROYECTO: RED TCP/IP EDUCATIVA
-- BASE DE DATOS: red_educativa
-- DATOS DE PRUEBA
-- =====================================================

USE red_educativa;

START TRANSACTION;


-- =====================================================
-- 1. USUARIO
-- 2 DOCENTES + 4 ESTUDIANTES
-- Contraseña de todos los usuarios demo: Demo1234!
-- Los hashes de este archivo son de prueba: ejecuta
-- capa_datos/migracion_api.sql para tener bcrypt reales.
-- =====================================================

INSERT INTO USUARIO
(id_usuario, nombre, correo, clave_hash, rol)
VALUES
(1, 'Carlos Mendoza', 'carlos.docente@example.test',
 'HASH_DE_PRUEBA_DOCENTE_001', 'DOCENTE'),

(2, 'Ana Torres', 'ana.docente@example.test',
 'HASH_DE_PRUEBA_DOCENTE_002', 'DOCENTE'),

(3, 'Luis Ramirez', 'luis.estudiante@example.test',
 'HASH_DE_PRUEBA_ESTUDIANTE_001', 'ESTUDIANTE'),

(4, 'Maria Flores', 'maria.estudiante@example.test',
 'HASH_DE_PRUEBA_ESTUDIANTE_002', 'ESTUDIANTE'),

(5, 'Pedro Castillo', 'pedro.estudiante@example.test',
 'HASH_DE_PRUEBA_ESTUDIANTE_003', 'ESTUDIANTE'),

(6, 'Lucia Vargas', 'lucia.estudiante@example.test',
 'HASH_DE_PRUEBA_ESTUDIANTE_004', 'ESTUDIANTE');


-- =====================================================
-- 2. ESTUDIANTE
-- =====================================================

INSERT INTO ESTUDIANTE
(id_estudiante, id_usuario, codigo_universitario)
VALUES
(101, 3, 'EST-2026-001'),
(102, 4, 'EST-2026-002'),
(103, 5, 'EST-2026-003'),
(104, 6, 'EST-2026-004');


-- =====================================================
-- 3. DOCENTE
-- =====================================================

INSERT INTO DOCENTE
(id_docente, id_usuario, area_academica)
VALUES
(201, 1, 'Ingenieria de Sistemas'),
(202, 2, 'Ciencias de la Computacion');


-- =====================================================
-- 4. DOCUMENTO
-- Documentos publicados por docentes y entregados
-- por estudiantes.
--
-- El binario no se carga aquí: estas filas no tienen
-- fila en DOCUMENTO_CONTENIDO, así que su descarga
-- responde 404 hasta que se suba un archivo real.
-- =====================================================

INSERT INTO DOCUMENTO
(id_documento, id_usuario_autor, nombre_archivo,
 tamano_bytes, fecha_publicacion)
VALUES

-- Material publicado por docentes

(301, 1, 'Introduccion_TCP_IP.pdf',
 2048000, '2026-10-01 09:00:00'),

(302, 2, 'Modelo_OSI.pdf',
 1536000, '2026-10-03 10:30:00'),

-- Documentos entregados por estudiantes

(303, 3, 'Practica_TCP_IP_Luis.pdf',
 1024000, '2026-11-05 14:20:00'),

(304, 4, 'Practica_TCP_IP_Maria.pdf',
 1280000, '2026-11-05 15:10:00'),

(305, 5, 'Practica_OSI_Pedro.pdf',
 980000, '2026-11-06 11:00:00'),

(306, 6, 'Practica_OSI_Lucia.pdf',
 1150000, '2026-11-06 12:30:00');


-- =====================================================
-- 5. ACTIVIDAD
-- Actividades creadas por docentes.
-- =====================================================

INSERT INTO ACTIVIDAD
(id_actividad, id_docente, titulo, fecha_limite)
VALUES

(401, 201, 'Practica: Configuracion TCP/IP',
 '2026-11-10 23:59:00'),

(402, 202, 'Practica: Analisis del modelo OSI',
 '2026-11-12 23:59:00');


-- =====================================================
-- 6. PERMISO_ACCESO
-- Se otorgan permisos para consultar documentos.
-- =====================================================

INSERT INTO PERMISO_ACCESO
(id_permiso, id_usuario, id_documento, tipo_permiso)
VALUES

-- Acceso a Introduccion TCP/IP

(501, 1, 301, 'LECTURA'),
(502, 3, 301, 'LECTURA'),
(503, 4, 301, 'LECTURA'),

-- Acceso a Modelo OSI

(504, 2, 302, 'LECTURA'),
(505, 5, 302, 'LECTURA'),
(506, 6, 302, 'LECTURA'),

-- Acceso de docentes a las entregas

(507, 1, 303, 'LECTURA'),
(508, 1, 304, 'LECTURA');


-- =====================================================
-- 7. ENTREGA
-- Entregas realizadas por los estudiantes.
-- =====================================================

INSERT INTO ENTREGA
(id_entrega, id_actividad, id_estudiante,
 id_documento, fecha_entrega)
VALUES

-- Actividad TCP/IP

(601, 401, 101, 303, '2026-11-05 14:20:00'),
(602, 401, 102, 304, '2026-11-05 15:10:00'),

-- Actividad Modelo OSI

(603, 402, 103, 305, '2026-11-06 11:00:00'),
(604, 402, 104, 306, '2026-11-06 12:30:00');


-- =====================================================
-- CONFIRMAR TRANSACCION
-- =====================================================

COMMIT;
