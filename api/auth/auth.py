import bcrypt
import jwt as pyjwt
from config.config import secreto_jwt
from fastapi import Depends, HTTPException
from datetime import datetime, timedelta, timezone
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

ALGORITMO = "HS256"
HORAS_TOKEN = 8
_bearer = HTTPBearer(auto_error=False)


def hashear(clave):
    return bcrypt.hashpw(clave.encode(), bcrypt.gensalt(rounds=12)).decode()


def verificar(clave, hash_guardado):
    try:
        return bcrypt.checkpw(clave.encode(), hash_guardado.encode())
    except ValueError:  # hash con formato inválido (por ejemplo, datos viejos)
        return False


def crear_token(id_usuario, rol):
    expira = datetime.now(timezone.utc) + timedelta(hours=HORAS_TOKEN)
    return pyjwt.encode(
        {"sub": str(id_usuario), "rol": rol, "exp": expira},
        secreto_jwt(),
        algorithm=ALGORITMO,
    )


def usuario_actual(credenciales: HTTPAuthorizationCredentials | None = Depends(_bearer)):
    if credenciales is None:
        raise HTTPException(401, "Falta el token Bearer", headers={"WWW-Authenticate": "Bearer"})
    try:
        datos = pyjwt.decode(credenciales.credentials, secreto_jwt(), algorithms=[ALGORITMO])
    except pyjwt.PyJWTError:
        raise HTTPException(401, "Token inválido o vencido", headers={"WWW-Authenticate": "Bearer"})
    return {"id_usuario": int(datos["sub"]), "rol": datos["rol"]}


def requiere_rol(rol):
    def dependencia(usuario=Depends(usuario_actual)):
        if usuario["rol"] != rol:
            raise HTTPException(403, f"Requiere rol {rol}")
        return usuario

    return dependencia


solo_estudiante = requiere_rol("ESTUDIANTE")
solo_docente = requiere_rol("DOCENTE")
