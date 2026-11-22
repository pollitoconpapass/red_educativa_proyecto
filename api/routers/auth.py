import pymysql
from config import db
from fastapi import APIRouter, HTTPException
from auth.auth import crear_token, hashear, verificar
from models.schemas import Login, Registro, RegistroOut, Token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login(datos: Login):
    filas = db.consultar(
        "SELECT id_usuario, nombre, rol, clave_hash FROM USUARIO WHERE correo = %s",
        (datos.correo,),
    )
    if not filas or not verificar(datos.clave, filas[0]["clave_hash"]):
        raise HTTPException(401, "Correo o contraseña incorrectos")

    usuario = filas[0]
    db.ejecutar(
        "INSERT INTO AUDITORIA (id_usuario, accion, entidad) VALUES (%s, 'LOGIN', 'USUARIO')",
        (usuario["id_usuario"],),
    )
    return Token(
        access_token=crear_token(usuario["id_usuario"], usuario["rol"]),
        id_usuario=usuario["id_usuario"],
        nombre=usuario["nombre"],
        rol=usuario["rol"],
    )


@router.post("/registro", response_model=RegistroOut, status_code=201)
def registro(datos: Registro):
    if datos.rol == "ESTUDIANTE" and not datos.codigo_universitario:
        raise HTTPException(422, "codigo_universitario es obligatorio para ESTUDIANTE")
    if len(datos.clave.encode()) > 72:
        raise HTTPException(422, "La contraseña no puede superar 72 bytes")

    try:
        with db.transaccion() as cursor:
            cursor.execute(
                "INSERT INTO USUARIO (nombre, correo, clave_hash, rol) VALUES (%s, %s, %s, %s)",
                (datos.nombre, datos.correo, hashear(datos.clave), datos.rol),
            )
            id_usuario = cursor.lastrowid

            if datos.rol == "ESTUDIANTE":
                cursor.execute(
                    "INSERT INTO ESTUDIANTE (id_usuario, codigo_universitario) VALUES (%s, %s)",
                    (id_usuario, datos.codigo_universitario),
                )
            else:
                cursor.execute(
                    "INSERT INTO DOCENTE (id_usuario, area_academica) VALUES (%s, %s)",
                    (id_usuario, datos.area_academica),
                )

            db.auditar(cursor, id_usuario, "REGISTRO", "USUARIO", id_usuario)
    except pymysql.err.IntegrityError:
        raise HTTPException(409, "El correo ya está registrado")

    return RegistroOut(id_usuario=id_usuario, rol=datos.rol)
