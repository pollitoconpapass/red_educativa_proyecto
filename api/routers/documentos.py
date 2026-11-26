from config import db
from auth.auth import usuario_actual
from auth.permisos import puede_descargar
from fastapi import APIRouter, Depends, HTTPException, Response

router = APIRouter(prefix="/documentos", tags=["documentos"])


@router.get("/{id_documento}/descarga")
def descargar(id_documento: int, usuario=Depends(usuario_actual)):
    filas = db.consultar(
        """SELECT d.id_documento, d.id_usuario_autor, d.nombre_archivo,
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

    contenido = db.consultar(
        "SELECT contenido FROM DOCUMENTO_CONTENIDO WHERE id_documento = %s",
        (id_documento,),
    )
    if not contenido:
        raise HTTPException(404, "El documento no tiene archivo cargado")

    db.ejecutar(
        """INSERT INTO AUDITORIA (id_usuario, accion, entidad, id_entidad)
           VALUES (%s, 'DESCARGA', 'DOCUMENTO', %s)""",
        (usuario["id_usuario"], id_documento),
    )
    nombre = documento["nombre_archivo"].replace('"', "").replace("\r", "").replace("\n", "")
    return Response(
        contenido[0]["contenido"],
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{nombre}"'},
    )
