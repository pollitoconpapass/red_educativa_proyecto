import unittest
from api.auth.permisos import puede_descargar

class PruebaPermisos(unittest.TestCase):
    def test_autor_puede_aunque_no_tenga_permiso(self):
        self.assertTrue(puede_descargar(3, 3, False))

    def test_permiso_concedido(self):
        self.assertTrue(puede_descargar(4, 1, True))

    def test_sin_permiso_ni_autoria(self):
        self.assertFalse(puede_descargar(5, 1, False))


if __name__ == "__main__":
    unittest.main()
