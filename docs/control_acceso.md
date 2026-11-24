# Control de acceso en EduNet: API y SDN

La API ([`api/`](../api/)) y la SDN ([`sdn/`](../sdn/)) son **dos features distintos**
que aplican la **misma política** en **capas distintas**. No se juntan como proceso,
pero sí deben coincidir en la regla.

## La diferencia

| | API (`api/`) | SDN (`sdn/`) |
|---|---|---|
| Capa | Aplicación (HTTP) | Red (OpenFlow) |
| Identidad | Usuario real: JWT + rol | Host: MAC fija del equipo |
| Decide con | `PERMISO_ACCESO` + autor | `PERMISO_ACCESO` + autor |
| Protege | Acciones de negocio: login, subir, descargar, crear actividad, auditar | Tráfico TCP hacia `ip_autor:8000+N` |
| Sabe de tokens/roles | Sí | No |
| Funciona fuera de Mininet | Sí | Solo dentro de la topología |
| Se salta con | Token robado / bug en la API | MAC falsificada / documento creado tras arrancar Ryu |

La analogía: la **API** es el bibliotecario que revisa tu carné antes de entregarte
el documento; el **SDN** es la cerradura de la puerta que solo abre las salas a las
que tienes llave. El bibliotecario no controla qué puertas abres, y la cerradura no
sabe quién eres.

## Por qué no se juntan

Son mecanismos de cumplimiento independientes:

- **API**: lógica de negocio (FastAPI, JWT, auditoría).
- **SDN**: plano de control de red (Ryu, switches, ACLs).

Meter Ryu dentro de uvicorn es frágil (eventlet vs asyncio, `sudo`, ciclos de vida
distintos), y además perderías la demo de **defensa en capas**: si la app falla, la
red sigue bloqueando, y viceversa.

## Por qué deben coincidir

La fuente de verdad es la misma BD `red_educativa` (`DOCUMENTO` + `PERMISO_ACCESO`).
Si una capa dice "sí" y la otra "no", el sistema es incoherente. La regla es una
sola: **autor o permiso explícito**.

- `api/auth/permisos.py` → `puede_descargar()`
- `sdn/config/politica.py` → `reglas_denegadas()` (el autor se salta el `drop`)

## Cómo se presenta en el entregable

**Una política, dos puntos de aplicación.** El SDN + servidor demuestra control de
acceso a nivel de red; la API demuestra control a nivel de aplicación sobre los
mismos datos.

## Límites conocidos

- La regla está duplicada: cualquier cambio de política debe hacerse en las dos capas.
- Mientras la ACL viva solo en memoria del controlador, un documento o permiso creado
  por la API después del arranque queda **fail-open** en la red hasta reiniciar Ryu.
