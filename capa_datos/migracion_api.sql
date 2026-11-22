-- =====================================================
-- MIGRACIÓN PARA LA API (ejecutar una vez en DBeaver)
-- BD existente: red_educativa
--
-- Añade la tabla de auditoría, las restricciones que
-- necesita la API y contraseñas bcrypt reales para los
-- usuarios de prueba.
--
-- Contraseña de los 6 usuarios demo: Demo1234!
-- =====================================================

USE red_educativa;


-- =====================================================
-- 1. TABLA DE AUDITORÍA
-- =====================================================

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


-- =====================================================
-- 2. RESTRICCIONES QUE USA LA API
--
-- Antes de ejecutar, comprueba que no haya duplicados.
-- Si alguna consulta devuelve filas, bórralas primero:
--
-- SELECT id_actividad, id_estudiante, COUNT(*)
-- FROM ENTREGA
-- GROUP BY id_actividad, id_estudiante
-- HAVING COUNT(*) > 1;
--
-- SELECT id_usuario, id_documento, COUNT(*)
-- FROM PERMISO_ACCESO
-- GROUP BY id_usuario, id_documento
-- HAVING COUNT(*) > 1;
-- =====================================================

ALTER TABLE ENTREGA
    ADD CONSTRAINT uq_entrega_actividad_estudiante
    UNIQUE (id_actividad, id_estudiante);

ALTER TABLE PERMISO_ACCESO
    ADD CONSTRAINT uq_permiso_usuario_documento
    UNIQUE (id_usuario, id_documento);


-- =====================================================
-- 3. CONTRASEÑAS DE LOS USUARIOS EXISTENTES
--
-- Los hashes del llenado original eran de mentira.
-- Estos son bcrypt (coste 12) de Demo1234!
-- La condición por correo evita tocar otras cuentas.
-- =====================================================

UPDATE USUARIO SET clave_hash = '$2b$12$4LQE0V.gd0h83kYjqdM4UOGKWiySshG5rX7254oSKa312bnRURiHS'
WHERE correo = 'carlos.docente@example.test';

UPDATE USUARIO SET clave_hash = '$2b$12$6uYcX5wIG5WMW0Pq4GgyluMY7/N2APoGFctB2qJujsfKyXKRWXDlO'
WHERE correo = 'ana.docente@example.test';

UPDATE USUARIO SET clave_hash = '$2b$12$1kfXqrom9N8iY4Y.kEf51.bUB8.RsYb0Ly8ImEjOHC9Xk6gH2HvXK'
WHERE correo = 'luis.estudiante@example.test';

UPDATE USUARIO SET clave_hash = '$2b$12$ZC1VxpDjnzeTV50NcEJKx.tWjR.qZajXfi7eyg/25EztV/ue.M/Q6'
WHERE correo = 'maria.estudiante@example.test';

UPDATE USUARIO SET clave_hash = '$2b$12$OXkrrt0G2CuCXoSmXXObu.QMPEn37XNLhf5/NZZaTwBliE2q7cN3K'
WHERE correo = 'pedro.estudiante@example.test';

UPDATE USUARIO SET clave_hash = '$2b$12$US5FbIZvBoUVWfKUZVsQhOzjF9AUZJLWAOIXx66I7rplbvOlSt2Bi'
WHERE correo = 'lucia.estudiante@example.test';


-- =====================================================
-- 4. VERIFICACIÓN
-- =====================================================

SHOW TABLES;

SELECT id_usuario, correo, rol,
       LEFT(clave_hash, 7) AS prefijo_hash
FROM USUARIO
ORDER BY id_usuario;

SELECT COUNT(*) AS total_auditoria FROM AUDITORIA;
