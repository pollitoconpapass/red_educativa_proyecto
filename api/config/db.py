import pymysql
from contextlib import contextmanager
from pymysql.cursors import DictCursor
from .config import configuracion_bd

def conectar():
    c = configuracion_bd()
    return pymysql.connect(
        host=c["SERVER_HOST"],
        port=int(c.get("PORT", 3306)),
        user=c["USERNAME"],
        password=c["PASSWORD"],
        database=c["DATABASE"],
        charset="utf8mb4",
        connect_timeout=5,
        cursorclass=DictCursor,
    )


def consultar(sql, parametros=None):
    conexion = conectar()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(sql, parametros)
            return cursor.fetchall()
    finally:
        conexion.close()


def ejecutar(sql, parametros=None):
    conexion = conectar()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(sql, parametros)
            conexion.commit()
            return cursor.lastrowid or 0
    finally:
        conexion.close()


@contextmanager
def transaccion():
    conexion = conectar()
    try:
        with conexion.cursor() as cursor:
            yield cursor
        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()


def auditar(cursor, id_usuario, accion, entidad, id_entidad=None):
    cursor.execute(
        "INSERT INTO AUDITORIA (id_usuario, accion, entidad, id_entidad) VALUES (%s, %s, %s, %s)",
        (id_usuario, accion, entidad, id_entidad),
    )
