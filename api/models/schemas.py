from typing import Literal
from datetime import datetime
from pydantic import BaseModel, Field


class Login(BaseModel):
    correo: str = Field(min_length=3, max_length=150)
    clave: str = Field(min_length=1, max_length=100)


class Registro(BaseModel):
    nombre: str = Field(min_length=2, max_length=150)
    correo: str = Field(min_length=3, max_length=150)
    clave: str = Field(min_length=8, max_length=100)
    rol: Literal["ESTUDIANTE", "DOCENTE"]
    codigo_universitario: str | None = Field(default=None, max_length=50)
    area_academica: str | None = Field(default=None, max_length=100)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    id_usuario: int
    nombre: str
    rol: str


class RegistroOut(BaseModel):
    id_usuario: int
    rol: str


class ActividadIn(BaseModel):
    titulo: str = Field(min_length=1, max_length=200)
    fecha_limite: datetime | None = None


class ActividadCreada(BaseModel):
    id_actividad: int
    titulo: str
    fecha_limite: datetime | None


class ActividadEstudiante(BaseModel):
    id_actividad: int
    titulo: str
    fecha_limite: datetime | None
    docente: str
    id_entrega: int | None
    fecha_entrega: datetime | None


class ActividadDocente(BaseModel):
    id_actividad: int
    titulo: str
    fecha_limite: datetime | None
    total_entregas: int


class EntregaOut(BaseModel):
    id_entrega: int
    id_actividad: int
    actividad: str
    id_documento: int
    nombre_archivo: str
    tamano_bytes: int
    fecha_entrega: datetime


class EntregaEstudiante(BaseModel):
    id_entrega: int
    fecha_entrega: datetime
    id_documento: int
    nombre_archivo: str
    tamano_bytes: int
    codigo_universitario: str
    estudiante: str


class EntregaResultado(BaseModel):
    id_entrega: int
    id_documento: int
    reemplazada: bool


class MaterialOut(BaseModel):
    id_documento: int
    nombre_archivo: str
    tamano_bytes: int
    fecha_publicacion: datetime


class AuditoriaOut(BaseModel):
    id_auditoria: int
    id_usuario: int
    usuario: str
    accion: str
    entidad: str
    id_entidad: int | None
    fecha: datetime
