"""Acceso a la BD MySQL de la capa de datos (red_educativa)."""

import os
import pymysql
from pathlib import Path
from urllib.parse import urlparse

RAIZ = Path(__file__).resolve().parents[2]  # raíz del proyecto (donde está .env)
CLAVES = ("SERVER_HOST", "PORT", "DATABASE", "USERNAME", "PASSWORD")

def configuracion():
    """Lee .env de la raíz del proyecto; las variables de entorno tienen prioridad.

    Admite `URL=jdbc:mysql://host:puerto/base` o las claves por separado
    (SERVER_HOST, PORT, DATABASE).
    """
    valores = {}
    archivo = RAIZ / ".env"
    if archivo.exists():
        for linea in archivo.read_text(encoding="utf-8").splitlines():
            linea = linea.strip()
            if "=" in linea and not linea.startswith("#"):
                clave, valor = linea.split("=", 1)
                valores[clave.strip()] = valor.strip().strip("\"'")

    url = valores.get("URL", "").removeprefix("jdbc:")
    if url:
        partes = urlparse(url)
        valores.setdefault("SERVER_HOST", partes.hostname)
        valores.setdefault("PORT", partes.port or 3306)
        valores.setdefault("DATABASE", partes.path.lstrip("/"))

    for clave in CLAVES:
        if os.environ.get(clave):
            valores[clave] = os.environ[clave]
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
