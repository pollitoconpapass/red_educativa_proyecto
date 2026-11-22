from config import db
from storage import archivos
from auth.auth import solo_estudiante
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from models.schemas import ActividadEstudiante, EntregaOut, EntregaResultado


router = APIRouter(prefix="/estudiante", tags=["estudiante"])


def _id_estudiante(usuario):
    filas = db.consultar(
        "SELECT id_estudiante FROM ESTUDIANTE WHERE id_usuario = %s",
        (usuario["id_usuario"],),
    )
    if not filas:
        raise HTTPException(403, "El usuario no tiene perfil de estudiante")
    return filas[0]["id_estudiante"]


@router.get("/actividades", response_model=list[ActividadEstudiante])
def actividades(usuario=Depends(solo_estudiante)):
    id_estudiante = _id_estudiante(usuario)
    return db.consultar(
        """SELECT a.id_actividad, a.titulo, a.fecha_limite, u.nombre AS docente,
                  en.id_entrega, en.fecha_entrega
           FROM ACTIVIDAD a
           JOIN DOCENTE d ON d.id_docente = a.id_docente
           JOIN USUARIO u ON u.id_usuario = d.id_usuario
           LEFT JOIN ENTREGA en
                  ON en.id_actividad = a.id_actividad AND en.id_estudiante = %s
           ORDER BY a.fecha_limite IS NULL, a.fecha_limite, a.id_actividad""",
        (id_estudiante,),
    )


@router.get("/entregas", response_model=list[EntregaOut])
def entregas(usuario=Depends(solo_estudiante)):
    id_estudiante = _id_estudiante(usuario)
    return db.consultar(
        """SELECT en.id_entrega, en.id_actividad, a.titulo AS actividad,
                  en.id_documento, doc.nombre_archivo, doc.tamano_bytes,
                  en.fecha_entrega
           FROM ENTREGA en
           JOIN ACTIVIDAD a ON a.id_actividad = en.id_actividad
           JOIN DOCUMENTO doc ON doc.id_documento = en.id_documento
           WHERE en.id_estudiante = %s
           ORDER BY en.fecha_entrega DESC""",
        (id_estudiante,),
    )


@router.post(
    "/actividades/{id_actividad}/entrega",
    response_model=EntregaResultado,
    status_code=201,
)
def entregar(
    id_actividad: int,
    archivo: UploadFile = File(...),
    usuario=Depends(solo_estudiante),
):
    id_estudiante = _id_estudiante(usuario)
    actividad = db.consultar(
        """SELECT d.id_usuario AS id_usuario_docente
           FROM ACTIVIDAD a
           JOIN DOCENTE d ON d.id_docente = a.id_docente
           WHERE a.id_actividad = %s""",
        (id_actividad,),
    )
    if not actividad:
        raise HTTPException(404, "Actividad no encontrada")
    id_usuario_docente = actividad[0]["id_usuario_docente"]

    try:
        clave, tamano = archivos.guardar(archivo)
    except ValueError as error:
        raise HTTPException(400, str(error))
    nombre = (archivo.filename or f"entrega_{id_actividad}")[:255]
    clave_vieja = None

    try:
        with db.transaccion() as cursor:
            cursor.execute(
                """SELECT en.id_entrega, en.id_documento, doc.clave_objeto_OCI
                   FROM ENTREGA en
                   JOIN DOCUMENTO doc ON doc.id_documento = en.id_documento
                   WHERE en.id_actividad = %s AND en.id_estudiante = %s
                   FOR UPDATE""",
                (id_actividad, id_estudiante),
            )
            previa = cursor.fetchone()

            if previa:
                id_entrega = previa["id_entrega"]
                id_documento = previa["id_documento"]
                clave_vieja = previa["clave_objeto_OCI"]
                cursor.execute(
                    """UPDATE DOCUMENTO
                       SET nombre_archivo = %s, clave_objeto_OCI = %s,
                           tamano_bytes = %s, fecha_publicacion = NOW()
                       WHERE id_documento = %s""",
                    (nombre, clave, tamano, id_documento),
                )
                cursor.execute(
                    "UPDATE ENTREGA SET fecha_entrega = NOW() WHERE id_entrega = %s",
                    (id_entrega,),
                )
                cursor.execute(
                    """INSERT INTO PERMISO_ACCESO (id_usuario, id_documento, tipo_permiso)
                       VALUES (%s, %s, 'LECTURA')
                       ON DUPLICATE KEY UPDATE tipo_permiso = 'LECTURA'""",
                    (id_usuario_docente, id_documento),
                )
                db.auditar(
                    cursor, usuario["id_usuario"], "ENTREGA_REEMPLAZADA", "ENTREGA", id_entrega
                )
                reemplazada = True
            else:
                cursor.execute(
                    """INSERT INTO DOCUMENTO
                           (id_usuario_autor, nombre_archivo, clave_objeto_OCI, tamano_bytes)
                       VALUES (%s, %s, %s, %s)""",
                    (usuario["id_usuario"], nombre, clave, tamano),
                )
                id_documento = cursor.lastrowid
                cursor.execute(
                    """INSERT INTO ENTREGA (id_actividad, id_estudiante, id_documento)
                       VALUES (%s, %s, %s)""",
                    (id_actividad, id_estudiante, id_documento),
                )
                id_entrega = cursor.lastrowid
                cursor.execute(
                    """INSERT INTO PERMISO_ACCESO (id_usuario, id_documento, tipo_permiso)
                       VALUES (%s, %s, 'LECTURA')""",
                    (id_usuario_docente, id_documento),
                )
                db.auditar(
                    cursor, usuario["id_usuario"], "ENTREGA_SUBIDA", "ENTREGA", id_entrega
                )
                reemplazada = False
    except Exception:
        archivos.borrar(clave)
        raise

    if clave_vieja:
        archivos.borrar(clave_vieja)

    return EntregaResultado(
        id_entrega=id_entrega, id_documento=id_documento, reemplazada=reemplazada
    )
