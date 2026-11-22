def puede_descargar(id_usuario, id_usuario_autor, tiene_permiso):
    return id_usuario == id_usuario_autor or bool(tiene_permiso)
