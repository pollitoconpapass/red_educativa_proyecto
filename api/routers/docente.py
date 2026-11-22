from config import db
from storage import archivos
from auth.auth import solo_docente
from models.schemas import (
    ActividadCreada,
    ActividadDocente,
    ActividadIn,
    EntregaEstudiante,
    MaterialOut,
)
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

router = APIRouter(prefix="/docente", tags=["docente"])


def _id_docente(usuario):
    filas = db.consultar(
        "SELECT id_docente FROM DOCENTE WHERE id_usuario = %s",
        (usuario["id_usuario"],),
    )
    if not filas:
        raise HTTPException(403, "El usuario no tiene perfil de docente")
    return filas[0]["id_docente"]


@router.get("/actividades", response_model=list[ActividadDocente])
def actividades(usuario=Depends(solo_docente)):
    id_docente = _id_docente(usuario)
    return db.consultar(
        """SELECT a.id_actividad, a.titulo, a.fecha_limite,
                  COUNT(en.id_entrega) AS total_entregas
           FROM ACTIVIDAD a
           LEFT JOIN ENTREGA en ON en.id_actividad = a.id_actividad
           WHERE a.id_docente = %s
           GROUP BY a.id_actividad, a.titulo, a.fecha_limite
           ORDER BY a.fecha_limite IS NULL, a.fecha_limite, a.id_actividad""",
        (id_docente,),
    )


@router.post("/actividades", response_model=ActividadCreada, status_code=201)
def crear_actividad(datos: ActividadIn, usuario=Depends(solo_docente)):
    id_docente = _id_docente(usuario)
    with db.transaccion() as cursor:
        cursor.execute(
            "INSERT INTO ACTIVIDAD (id_docente, titulo, fecha_limite) VALUES (%s, %s, %s)",
            (id_docente, datos.titulo, datos.fecha_limite),
        )
        id_actividad = cursor.lastrowid
        db.auditar(cursor, usuario["id_usuario"], "ACTIVIDAD_CREADA", "ACTIVIDAD", id_actividad)
    return ActividadCreada(
        id_actividad=id_actividad, titulo=datos.titulo, fecha_limite=datos.fecha_limite
    )


@router.get(
    "/actividades/{id_actividad}/entregas",
    response_model=list[EntregaEstudiante],
)
def entregas(id_actividad: int, usuario=Depends(solo_docente)):
    id_docente = _id_docente(usuario)
    actividad = db.consultar(
        "SELECT id_docente FROM ACTIVIDAD WHERE id_actividad = %s", (id_actividad,)
    )
    if not actividad:
        raise HTTPException(404, "Actividad no encontrada")
    if actividad[0]["id_docente"] != id_docente:
        raise HTTPException(403, "La actividad no es suya")

    return db.consultar(
        """SELECT en.id_entrega, en.fecha_entrega, en.id_documento,
                  e.codigo_universitario, u.nombre AS estudiante,
                  doc.nombre_archivo, doc.tamano_bytes
           FROM ENTREGA en
           JOIN ESTUDIANTE e ON e.id_estudiante = en.id_estudiante
           JOIN USUARIO u ON u.id_usuario = e.id_usuario
           JOIN DOCUMENTO doc ON doc.id_documento = en.id_documento
           WHERE en.id_actividad = %s
           ORDER BY en.fecha_entrega""",
        (id_actividad,),
    )


@router.get("/material", response_model=list[MaterialOut])
def material(usuario=Depends(solo_docente)):
    return db.consultar(
        """SELECT id_documento, nombre_archivo, tamano_bytes, fecha_publicacion
           FROM DOCUMENTO
           WHERE id_usuario_autor = %s
           ORDER BY fecha_publicacion DESC""",
        (usuario["id_usuario"],),
    )


@router.post("/material", response_model=MaterialOut, status_code=201)
def subir_material(archivo: UploadFile = File(...), usuario=Depends(solo_docente)):
    try:
        clave, tamano = archivos.guardar(archivo)
    except ValueError as error:
        raise HTTPException(400, str(error))
    nombre = (archivo.filename or "material")[:255]

    try:
        with db.transaccion() as cursor:
            cursor.execute(
                """INSERT INTO DOCUMENTO
                       (id_usuario_autor, nombre_archivo, clave_objeto_OCI, tamano_bytes)
                   VALUES (%s, %s, %s, %s)""",
                (usuario["id_usuario"], nombre, clave, tamano),
            )
            id_documento = cursor.lastrowid
            # Todos los estudiantes pueden leer el material (no hay matrícula).
            cursor.execute(
                """INSERT IGNORE INTO PERMISO_ACCESO (id_usuario, id_documento, tipo_permiso)
                   SELECT id_usuario, %s, 'LECTURA' FROM USUARIO WHERE rol = 'ESTUDIANTE'""",
                (id_documento,),
            )
            db.auditar(
                cursor, usuario["id_usuario"], "MATERIAL_SUBIDO", "DOCUMENTO", id_documento
            )
            cursor.execute(
                "SELECT fecha_publicacion FROM DOCUMENTO WHERE id_documento = %s",
                (id_documento,),
            )
            fecha_publicacion = cursor.fetchone()["fecha_publicacion"]
    except Exception:
        archivos.borrar(clave)
        raise

    return MaterialOut(
        id_documento=id_documento,
        nombre_archivo=nombre,
        tamano_bytes=tamano,
        fecha_publicacion=fecha_publicacion,
    )
