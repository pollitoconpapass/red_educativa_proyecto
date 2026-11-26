MAX_BYTES = 10 * 1024 * 1024


def leer(archivo):
    datos = archivo.file.read(MAX_BYTES + 1)
    if not datos:
        raise ValueError("El archivo está vacío")
    if len(datos) > MAX_BYTES:
        raise ValueError("El archivo supera el límite de 10 MB")
    return datos
