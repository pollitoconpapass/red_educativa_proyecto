
-- ============================================
-- 1. CREACIÓN DE USUARIO
-- ============================================
CREATE USER 'appuser'@'%'
IDENTIFIED BY 'StrongPassword123!';

-- ============================================
-- 2. PERMISOS DE ACCESO
-- ============================================
GRANT ALL PRIVILEGES
ON red_educativa.*
TO 'appuser'@'%';

FLUSH PRIVILEGES;

-- ============================================
-- 3. COMPROBACIÓN DE PERMISOS
-- ============================================
SHOW DATABASES;

SELECT user, host
FROM mysql.user;



-- Primero, verifica los usuarios existentes
SELECT user, host FROM mysql.user;

-- Si ves 'tu_usuario' con host 'localhost', puedes cambiar su host
UPDATE mysql.user SET host = '%' WHERE user = 'appuser' AND host = 'localhost';
FLUSH PRIVILEGES;