import uuid
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / "almacenamiento"
MAX_BYTES = 10 * 1024 * 1024


def _extension(nombre):
    sufijo = Path(nombre or "").suffix.lower()
    return sufijo if sufijo[1:].isalnum() and len(sufijo) <= 10 else ""


def guardar(archivo):
    datos = archivo.file.read(MAX_BYTES + 1)
    if not datos:
        raise ValueError("El archivo está vacío")
    if len(datos) > MAX_BYTES:
        raise ValueError("El archivo supera el límite de 10 MB")

    clave = f"documentos/{uuid.uuid4().hex}{_extension(archivo.filename)}"
    destino = BASE / clave
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_bytes(datos)
    return clave, len(datos)


def ruta(clave):
    return BASE / clave


def borrar(clave):
    try:
        (BASE / clave).unlink()
    except FileNotFoundError:
        pass
