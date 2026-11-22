import os
from pathlib import Path
from urllib.parse import urlparse


def _buscar_env():
    for carpeta in Path(__file__).resolve().parents:
        archivo = carpeta / ".env"
        if archivo.exists():
            return archivo
    return None


def _leer_env():
    archivo = _buscar_env()
    valores = {}
    if archivo is None:
        return valores
    for linea in archivo.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if "=" in linea and not linea.startswith("#"):
            clave, valor = linea.split("=", 1)
            valores[clave.strip()] = valor.strip().strip("\"'")
    return valores


def configuracion_bd():
    valores = _leer_env()

    url = valores.get("URL", "").removeprefix("jdbc:")
    if url:
        partes = urlparse(url)
        valores.setdefault("SERVER_HOST", partes.hostname)
        valores.setdefault("PORT", partes.port or 3306)
        valores.setdefault("DATABASE", partes.path.lstrip("/"))

    for clave in ("SERVER_HOST", "PORT", "DATABASE", "USERNAME", "PASSWORD"):
        if os.environ.get(clave):
            valores[clave] = os.environ[clave]

    faltan = [
        clave
        for clave in ("SERVER_HOST", "USERNAME", "PASSWORD", "DATABASE")
        if not valores.get(clave)
    ]
    if faltan:
        raise RuntimeError(
            f"Faltan {', '.join(faltan)} para conectar a la BD. "
            f".env usado: {_buscar_env() or 'ninguno encontrado'}. "
            "Formato: URL=jdbc:mysql://host:3306/red_educativa + USERNAME + PASSWORD."
        )
    return valores


def secreto_jwt():
    secreto = os.environ.get("JWT_SECRET") or _leer_env().get("JWT_SECRET")
    if not secreto:
        raise RuntimeError(
            "Falta JWT_SECRET. Agrégalo a api/.env o al .env de la raíz, "
            "o expórtalo como variable de entorno."
        )
    return secreto
