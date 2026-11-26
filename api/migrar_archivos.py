"""Migra api/almacenamiento/ a DOCUMENTO_CONTENIDO.

Ejecutar desde api/ en la VPS de aplicación, con la VPS de datos encendida:

    cd api && python3 migrar_archivos.py

Es idempotente: solo inserta documentos que aún no tienen contenido.
Requiere que se haya ejecutado la fase A de capa_datos/migracion_archivos_bd.sql.
"""


from config import db
from pathlib import Path
from config.config import configuracion_bd
from storage.archivos import MAX_BYTES

BASE = Path(__file__).resolve().parent / "almacenamiento"


def main():
    config = configuracion_bd()
    print(
        f"BD destino: {config['SERVER_HOST']}:{config.get('PORT', 3306)}"
        f" / {config['DATABASE']}"
    )

    if not BASE.is_dir():
        print(f"No existe {BASE}; nada que migrar")
        return

    base = BASE.resolve()
    referenciados = {
        fila["clave_objeto_OCI"]
        for fila in db.consultar(
            "SELECT clave_objeto_OCI FROM DOCUMENTO WHERE clave_objeto_OCI IS NOT NULL"
        )
    }
    pendientes = db.consultar(
        """SELECT d.id_documento, d.clave_objeto_OCI
           FROM DOCUMENTO d
           WHERE d.clave_objeto_OCI IS NOT NULL
             AND NOT EXISTS (SELECT 1 FROM DOCUMENTO_CONTENIDO c
                             WHERE c.id_documento = d.id_documento)"""
    )

    migrados = 0
    sin_archivo = []
    for fila in pendientes:
        clave = fila["clave_objeto_OCI"]
        ruta = (base / clave).resolve()
        if base not in ruta.parents or not ruta.is_file():
            sin_archivo.append(clave)
            continue
        contenido = ruta.read_bytes()
        if not contenido or len(contenido) > MAX_BYTES:
            print(f"omitido (vacío o mayor a 10 MB): {clave}")
            continue
        with db.transaccion() as cursor:
            cursor.execute(
                "INSERT INTO DOCUMENTO_CONTENIDO (id_documento, contenido) VALUES (%s, %s)",
                (fila["id_documento"], contenido),
            )
        migrados += 1
        print(f"migrado id_documento={fila['id_documento']}: {clave} ({len(contenido)} bytes)")

    huerfanos = [
        p
        for p in base.rglob("*")
        if p.is_file() and p.relative_to(base).as_posix() not in referenciados
    ]

    print(f"\nmigrados: {migrados}")
    print(f"filas sin archivo en disco: {len(sin_archivo)}")
    for clave in sin_archivo:
        print(f"  {clave}")
    print(f"archivos en disco sin fila en DOCUMENTO: {len(huerfanos)}")
    for p in huerfanos:
        print(f"  {p.relative_to(base)}")


if __name__ == "__main__":
    main()
