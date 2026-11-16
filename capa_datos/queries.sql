-- =====================================================
-- 1. VERIFICACION DE DATOS
-- =====================================================

-- Consultar todas las tablas

SELECT * FROM USUARIO;
SELECT * FROM ESTUDIANTE;
SELECT * FROM DOCENTE;
SELECT * FROM DOCUMENTO;
SELECT * FROM ACTIVIDAD;
SELECT * FROM PERMISO_ACCESO;
SELECT * FROM ENTREGA;


-- =====================================================
-- 2. CONSULTAS DE PRUEBA
-- =====================================================

-- CONSULTA 1:
-- Listar estudiantes y sus datos de usuario.

SELECT
    e.id_estudiante,
    e.codigo_universitario,
    u.nombre,
    u.correo
FROM ESTUDIANTE e
INNER JOIN USUARIO u
    ON e.id_usuario = u.id_usuario;


-- CONSULTA 2:
-- Listar docentes y sus actividades.

SELECT
    d.id_docente,
    u.nombre AS docente,
    d.area_academica,
    a.titulo AS actividad,
    a.fecha_limite
FROM DOCENTE d
INNER JOIN USUARIO u
    ON d.id_usuario = u.id_usuario
LEFT JOIN ACTIVIDAD a
    ON d.id_docente = a.id_docente;


-- CONSULTA 3:
-- Consultar documentos y sus autores.

SELECT
    doc.id_documento,
    doc.nombre_archivo,
    u.nombre AS autor,
    doc.tamano_bytes,
    doc.fecha_publicacion
FROM DOCUMENTO doc
INNER JOIN USUARIO u
    ON doc.id_usuario_autor = u.id_usuario;


-- CONSULTA 4:
-- Consultar entregas con estudiantes,
-- actividades y documentos.

SELECT
    en.id_entrega,
    u.nombre AS estudiante,
    e.codigo_universitario,
    a.titulo AS actividad,
    doc.nombre_archivo,
    en.fecha_entrega
FROM ENTREGA en
INNER JOIN ESTUDIANTE e
    ON en.id_estudiante = e.id_estudiante
INNER JOIN USUARIO u
    ON e.id_usuario = u.id_usuario
INNER JOIN ACTIVIDAD a
    ON en.id_actividad = a.id_actividad
INNER JOIN DOCUMENTO doc
    ON en.id_documento = doc.id_documento
ORDER BY en.fecha_entrega;


-- CONSULTA 5:
-- Contar entregas por actividad.

SELECT
    a.id_actividad,
    a.titulo,
    COUNT(en.id_entrega) AS total_entregas
FROM ACTIVIDAD a
LEFT JOIN ENTREGA en
    ON a.id_actividad = en.id_actividad
GROUP BY
    a.id_actividad,
    a.titulo;


-- CONSULTA 6:
-- Consultar permisos de acceso a documentos.

SELECT
    p.id_permiso,
    u.nombre AS usuario,
    doc.nombre_archivo,
    p.tipo_permiso
FROM PERMISO_ACCESO p
INNER JOIN USUARIO u
    ON p.id_usuario = u.id_usuario
INNER JOIN DOCUMENTO doc
    ON p.id_documento = doc.id_documento;


-- CONSULTA 7:
-- Obtener cantidad de documentos publicados
-- por cada usuario.

SELECT
    u.nombre,
    COUNT(doc.id_documento) AS total_documentos
FROM USUARIO u
LEFT JOIN DOCUMENTO doc
    ON u.id_usuario = doc.id_usuario_autor
GROUP BY
    u.id_usuario,
    u.nombre;
