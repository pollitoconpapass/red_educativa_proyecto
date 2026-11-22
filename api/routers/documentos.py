from config import db
from storage import archivos
from auth.auth import usuario_actual
from auth.permisos import puede_descargar
from fastapi.responses import FileResponse
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter(prefix="/documentos", tags=["documentos"])


@router.get("/{id_documento}/descarga")
def descargar(id_documento: int, usuario=Depends(usuario_actual)):
    filas = db.consultar(
        """SELECT d.id_documento, d.id_usuario_autor, d.nombre_archivo,
                  d.clave_objeto_OCI,
                  EXISTS(SELECT 1 FROM PERMISO_ACCESO p
                         WHERE p.id_usuario = %s
                           AND p.id_documento = d.id_documento) AS tiene_permiso
           FROM DOCUMENTO d
           WHERE d.id_documento = %s""",
        (usuario["id_usuario"], id_documento),
    )
    if not filas:
        raise HTTPException(404, "Documento no encontrado")

    documento = filas[0]
    if not puede_descargar(
        usuario["id_usuario"], documento["id_usuario_autor"], documento["tiene_permiso"]
    ):
        raise HTTPException(403, "Sin permiso para este documento")

    ruta = archivos.ruta(documento["clave_objeto_OCI"])
    if not ruta.is_file():
        raise HTTPException(404, "El archivo no está disponible en el almacenamiento")

    db.ejecutar(
        """INSERT INTO AUDITORIA (id_usuario, accion, entidad, id_entidad)
           VALUES (%s, 'DESCARGA', 'DOCUMENTO', %s)""",
        (usuario["id_usuario"], id_documento),
    )
    return FileResponse(
        ruta,
        media_type="application/octet-stream",
        filename=documento["nombre_archivo"],
    )
