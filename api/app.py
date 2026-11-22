from config import db
from fastapi import FastAPI, HTTPException
from routers import auditoria, auth, docente, documentos, estudiante

app = FastAPI(title="EduNet API", version="1.0.0")
app.include_router(auth.router)
app.include_router(estudiante.router)
app.include_router(docente.router)
app.include_router(documentos.router)
app.include_router(auditoria.router)


@app.get("/health", tags=["health"])
def salud():
    try:
        db.consultar("SELECT 1")
    except Exception:
        raise HTTPException(503, "Sin conexión a la base de datos")
    return {"estado": "ok"}
