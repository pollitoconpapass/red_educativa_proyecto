# API EduNet (FastAPI)

API de la capa de aplicación: estudiantes entregan y consultan tareas; docentes
publican material, crean actividades y descargan entregas. Toda escritura queda
en `AUDITORIA`.

## Requisitos

- Python 3.10+
- La VM de la capa de datos encendida y MySQL accesible en el puerto 3306.
- El `.env` de la API con `URL`, `USERNAME`, `PASSWORD` y `JWT_SECRET` (se busca primero `api/.env`; si no existe, el `.env` de la raíz).

## 1. Migración de la base de datos

Ejecuta **una vez** `capa_datos/migracion_api.sql` en DBeaver sobre
`red_educativa`. Añade `AUDITORIA`, las restricciones que usa la API y
contraseñas bcrypt reales para los usuarios existentes.

- Contraseña de los 6 usuarios demo: `Demo1234!`
- Si algún `ALTER` falla, revisa antes los duplicados con las consultas que
  están comentadas en el propio script.

Las instalaciones nuevas pueden usar `creacion_tablas.sql` + `llenado_datos.sql`

- `migracion_api.sql`.

## 2. Instalación y arranque

Desde la raíz del repositorio:

```bash
pip install -r api/requirements.txt
uvicorn api.app:app --reload --port 8080
```

Documentación interactiva: `http://localhost:8080/docs`
Comprobación de BD: `http://localhost:8080/health`

## Registro y roles

- `POST /auth/registro` crea el usuario y su perfil (`ESTUDIANTE` o `DOCENTE`).
- El estudiante debe enviar `codigo_universitario`.
- El login devuelve un JWT que se manda como `Authorization: Bearer <token>`.

## Endpoints

| Método | Ruta                                   | Rol                                     |
| ------ | -------------------------------------- | --------------------------------------- |
| POST   | `/auth/login`                          | público                                 |
| POST   | `/auth/registro`                       | público                                 |
| GET    | `/estudiante/actividades`              | estudiante                              |
| GET    | `/estudiante/entregas`                 | estudiante                              |
| POST   | `/estudiante/actividades/{id}/entrega` | estudiante (multipart, campo `archivo`) |
| GET    | `/docente/actividades`                 | docente                                 |
| POST   | `/docente/actividades`                 | docente                                 |
| GET    | `/docente/actividades/{id}/entregas`   | docente                                 |
| GET    | `/docente/material`                    | docente                                 |
| POST   | `/docente/material`                    | docente (multipart, campo `archivo`)    |
| GET    | `/documentos/{id}/descarga`            | autor o usuario con permiso             |
| GET    | `/auditoria`                           | docente                                 |
| GET    | `/health`                              | público                                 |

Diseño completo, diagramas y reglas de negocio: [`docs/diseno-api.md`](../docs/diseno-api.md).

## Almacenamiento

Los archivos se guardan en `api/almacenamiento/` y `clave_objeto_OCI` contiene la
clave relativa. Para usar Azure Blob Storage solo se cambia
`api/storage/archivos.py`; el esquema y los routers no cambian.

## Prueba unitaria

Desde la raíz:

```bash
python3 -m unittest discover -s api/tests -v
```
