"""Acceso a la BD MySQL de la capa de datos (red_educativa)."""

import os
import pymysql
from pathlib import Path
from urllib.parse import urlparse

RAIZ = Path(__file__).resolve().parents[1]  # capa_aplicacion/
CLAVES = ("SERVER_HOST", "PORT", "DATABASE", "USERNAME", "PASSWORD")
OBLIGATORIAS = ("SERVER_HOST", "USERNAME", "PASSWORD", "DATABASE")


def _parsear(archivo):
    valores = {}
    for linea in archivo.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if "=" in linea and not linea.startswith("#"):
            clave, valor = linea.split("=", 1)
            valores[clave.strip()] = valor.strip().strip("\"'")
    return valores


def _leer_env(desde):
    """Primer `.env` encontrado desde `desde` hacia arriba."""
    desde = Path(desde).resolve()
    for carpeta in (desde, *desde.parents):
        archivo = carpeta / ".env"
        if archivo.exists():
            return archivo, _parsear(archivo)
    return None, {}


def configuracion():
    """Config de la BD desde el `.env` más cercano hacia arriba.

    Admite `URL=jdbc:mysql://host:puerto/base` o las claves por separado
    (SERVER_HOST, PORT, DATABASE). Las variables de entorno tienen prioridad.
    """
    archivo, valores = _leer_env(__file__)

    url = valores.get("URL", "").removeprefix("jdbc:")
    if url:
        partes = urlparse(url)
        valores.setdefault("SERVER_HOST", partes.hostname)
        valores.setdefault("PORT", partes.port or 3306)
        valores.setdefault("DATABASE", partes.path.lstrip("/"))

    for clave in CLAVES:
        if os.environ.get(clave):
            valores[clave] = os.environ[clave]

    faltan = [clave for clave in OBLIGATORIAS if not valores.get(clave)]
    if faltan:
        raise RuntimeError(
            f"Faltan {', '.join(faltan)} para conectar a la BD. "
            f".env usado: {archivo or 'ninguno encontrado desde ' + str(RAIZ)}. "
            f"Claves leidas: {sorted(valores)}. "
            "Formato: URL=jdbc:mysql://host:3306/red_educativa + USERNAME + PASSWORD."
        )
    return valores


def conectar():
    c = configuracion()
    return pymysql.connect(
        host=c["SERVER_HOST"],
        port=int(c.get("PORT", 3306)),
        user=c["USERNAME"],
        password=c["PASSWORD"],
        database=c["DATABASE"],
        charset="utf8mb4",
        connect_timeout=5,
    )


def consultar(sql, parametros=None):
    conexion = conectar()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(sql, parametros)
            return cursor.fetchall()
    finally:
        conexion.close()


def cargar_estado():
    """Devuelve (documentos, permisos) tal como están en la BD.

    documentos: [(id_documento, id_usuario_autor)]
    permisos:   {(id_usuario, id_documento)} de PERMISO_ACCESO
    """
    documentos = consultar("SELECT id_documento, id_usuario_autor FROM DOCUMENTO")
    permisos = set(consultar("SELECT id_usuario, id_documento FROM PERMISO_ACCESO"))
    return documentos, permisos


def documentos_del_autor(id_usuario):
    return consultar(
        "SELECT id_documento, nombre_archivo FROM DOCUMENTO WHERE id_usuario_autor = %s",
        (id_usuario,),
    )
