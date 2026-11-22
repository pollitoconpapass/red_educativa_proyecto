from config import db
from auth.auth import solo_docente
from models.schemas import AuditoriaOut
from fastapi import APIRouter, Depends, Query

router = APIRouter(prefix="/auditoria", tags=["auditoria"])


@router.get("", response_model=list[AuditoriaOut], dependencies=[Depends(solo_docente)])
def listar(
    id_usuario: int | None = None,
    limite: int = Query(100, ge=1, le=500),
):
    sql = """SELECT a.id_auditoria, a.id_usuario, u.nombre AS usuario,
                    a.accion, a.entidad, a.id_entidad, a.fecha
             FROM AUDITORIA a
             JOIN USUARIO u ON u.id_usuario = a.id_usuario"""
    parametros = []

    if id_usuario is not None:
        sql += " WHERE a.id_usuario = %s"
        parametros.append(id_usuario)

    sql += " ORDER BY a.id_auditoria DESC LIMIT %s"
    parametros.append(limite)
    return db.consultar(sql, tuple(parametros))
