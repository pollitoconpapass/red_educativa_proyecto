# Portal EduNet (capa de presentación)

Interfaz web en HTML, CSS y JavaScript puro, sin dependencias ni compilación.
Consume la API de `api/` y separa estructura (`index.html`), estilos (`css/`) y
lógica (`js/`).

## Arranque

1. Activar las VM de datos y de aplicación
2. Pegar la URL de la VM de la capa de aplicación dentro de `js/config.js`

La URL de la API se define en `js/config.js` (`window.EDUNET_API_URL`). La API
incluye CORS abierto para que el portal se sirva desde otro origen.

## Estructura

| Ruta                 | Responsabilidad                                         |
| -------------------- | ------------------------------------------------------- |
| `index.html`         | Punto de entrada y carga de hojas y scripts.            |
| `css/tokens.css`     | Variables de color y tipografía, reset y utilidades.    |
| `css/layout.css`     | Acceso, shell, barra lateral, cabecera y responsive.    |
| `css/components.css` | Botones, formularios, listas, tablas, avisos y modales. |
| `js/config.js`       | URL base de la API.                                     |
| `js/api.js`          | Sesión, peticiones HTTP, manejo de errores y descargas. |
| `js/ui.js`           | Formato de fechas y tamaños, avisos, estados y modales. |
| `js/auth.js`         | Inicio de sesión, registro y estado de la API.          |
| `js/estudiante.js`   | Actividades, entregas y carga de archivos.              |
| `js/docente.js`      | Actividades, entregas, material y auditoría.            |
| `js/app.js`          | Arranque, ruteo por hash y acciones globales.           |

## Funciones por rol

- **Estudiante**: lista todas las actividades con su estado (pendiente,
  entregada, vencida), sube o reemplaza una entrega y descarga sus archivos.
- **Docente**: crea actividades, revisa y descarga las entregas de cada una,
  publica material y consulta la auditoría con filtros.
- **Acceso**: login, registro con perfil de estudiante o docente, cierre de
  sesión y comprobación de `/health`.
- **Descargas**: se piden con el token Bearer y se guardan con el nombre
  original del archivo.

## Límites conocidos

- La API no expone una lista de material para estudiantes (`GET
/docente/material` es solo del docente). Por eso el portal no muestra esa
  sección al estudiante; haría falta un endpoint de material visible para ese
  rol.
- La fecha límite es informativa: la API no bloquea entregas fuera de plazo.
- Tema claro fijo, sin selector de tema oscuro.

## Comprobación

Las vistas se probaron con un Chrome headless y una API simulada: login,
registro, subida de entrega, creación de actividad, descargas, expiración de
sesión y vistas de escritorio y móvil.
