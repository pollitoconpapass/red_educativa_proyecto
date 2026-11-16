#!/usr/bin/env python3
"""Sirve en este host los documentos que la BD le asigna como autor.

Uso (dentro de Mininet):  doc-carlos python3 servidor_documentos.py 1
"""

import sys
import threading
import http.server
import socketserver
from config import db
from config import config as cfg

class Manejador(http.server.BaseHTTPRequestHandler):
    contenido = b""

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(self.contenido)))
        self.end_headers()
        self.wfile.write(self.contenido)

    def log_message(self, *args):
        pass


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 1

    id_usuario = int(sys.argv[1])
    documentos = db.documentos_del_autor(id_usuario)
    if not documentos:
        print(f"El usuario {id_usuario} no tiene documentos publicados en la BD")
        return 1

    socketserver.TCPServer.allow_reuse_address = True
    for id_documento, nombre_archivo in documentos:
        puerto = cfg.PUERTO_DOC_BASE + id_documento
        # Un servidor HTTP por documento: el puerto identifica el documento en OpenFlow.
        handler = type(f"Doc{id_documento}", (Manejador,), {
            "contenido": f"{nombre_archivo} (id_documento {id_documento})\n".encode(),
        })
        servidor = socketserver.TCPServer(("0.0.0.0", puerto), handler)
        threading.Thread(target=servidor.serve_forever, daemon=True).start()
        print(f"http://0.0.0.0:{puerto}/ -> {nombre_archivo}")

    threading.Event().wait()
    return 0


if __name__ == "__main__":
    sys.exit(main())
