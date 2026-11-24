"""Topología y direccionamiento de EduNet.

`usuario` es el id_usuario de la tabla USUARIO; None = host sin cuenta en la BD
(no aparece en PERMISO_ACCESO, así que no puede leer documentos).
"""

# El documento con id_documento=N se sirve en el puerto 8000+N del host de su autor.
PUERTO_DOC_BASE = 8000

SEDES = [
    # Nombres con "_" y sin "-": el CLI de Mininet corta la línea en el guion.
    {"switch": "s1", "hosts": [  # Lima
        {"nombre": "doc_carlos", "ip": "10.0.1.11", "mac": "00:00:00:00:01:01", "usuario": 1},
        {"nombre": "est_luis", "ip": "10.0.1.12", "mac": "00:00:00:00:01:02", "usuario": 3},
    ]},
    {"switch": "s2", "hosts": [  # La Libertad
        {"nombre": "doc_ana", "ip": "10.0.2.11", "mac": "00:00:00:00:02:01", "usuario": 2},
        {"nombre": "est_maria", "ip": "10.0.2.12", "mac": "00:00:00:00:02:02", "usuario": 4},
    ]},
    {"switch": "s3", "hosts": [  # Junin
        {"nombre": "est_pedro", "ip": "10.0.3.11", "mac": "00:00:00:00:03:01", "usuario": 5},
        {"nombre": "invitado_1", "ip": "10.0.3.12", "mac": "00:00:00:00:03:02", "usuario": None},
    ]},
    {"switch": "s4", "hosts": [  # Arequipa
        {"nombre": "est_lucia", "ip": "10.0.4.11", "mac": "00:00:00:00:04:01", "usuario": 6},
        {"nombre": "invitado_2", "ip": "10.0.4.12", "mac": "00:00:00:00:04:02", "usuario": None},
    ]},
    {"switch": "s5", "hosts": [  # Loreto
        {"nombre": "invitado_3", "ip": "10.0.5.11", "mac": "00:00:00:00:05:01", "usuario": None},
        {"nombre": "invitado_4", "ip": "10.0.5.12", "mac": "00:00:00:00:05:02", "usuario": None},
    ]},
]

HOSTS = [host for sede in SEDES for host in sede["hosts"]]
