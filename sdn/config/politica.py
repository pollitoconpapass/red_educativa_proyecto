"""Cálculo de la ACL de documentos: todo lo que la BD no autoriza se bloquea.

El autor siempre puede leer su documento, igual que en la API, aunque no tenga
fila en PERMISO_ACCESO.
"""

from .config import PUERTO_DOC_BASE


def reglas_denegadas(hosts, documentos, permisos):
    """Tráfico host -> puerto de documento que PERMISO_ACCESO no autoriza.

    hosts:      [{"mac", "ip", "usuario"}]  (usuario = id_usuario o None)
    documentos: [(id_documento, id_usuario_autor)]
    permisos:   {(id_usuario, id_documento)}
    """
    ip_por_usuario = {h["usuario"]: h["ip"] for h in hosts if h["usuario"] is not None}

    reglas = []
    for host in hosts:
        for id_documento, id_autor in documentos:
            ip_autor = ip_por_usuario.get(id_autor)
            if ip_autor is None:  # el autor no está en esta topología
                continue
            if host["usuario"] == id_autor or (host["usuario"], id_documento) in permisos:
                continue
            reglas.append({
                "usuario": host["usuario"],
                "mac_src": host["mac"],
                "ip_dst": ip_autor,
                "puerto": PUERTO_DOC_BASE + id_documento,
                "documento": id_documento,
            })
    return reglas
