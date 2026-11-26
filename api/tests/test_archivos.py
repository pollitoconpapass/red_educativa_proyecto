import unittest
from io import BytesIO
from types import SimpleNamespace

from api.storage.archivos import MAX_BYTES, leer


def archivo_falso(datos):
    return SimpleNamespace(file=BytesIO(datos))


class PruebaArchivos(unittest.TestCase):
    def test_vacio(self):
        with self.assertRaises(ValueError):
            leer(archivo_falso(b""))

    def test_limite_exacto(self):
        self.assertEqual(len(leer(archivo_falso(b"x" * MAX_BYTES))), MAX_BYTES)

    def test_supera_limite(self):
        with self.assertRaises(ValueError):
            leer(archivo_falso(b"x" * (MAX_BYTES + 1)))


if __name__ == "__main__":
    unittest.main()
