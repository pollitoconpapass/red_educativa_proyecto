import unittest
from config.config import PUERTO_DOC_BASE
from config.politica import reglas_denegadas

class ReglasDenegadasTest(unittest.TestCase):
    HOSTS = [
        {"nombre": "doc", "mac": "aa", "ip": "10.0.0.11", "usuario": 1},
        {"nombre": "est", "mac": "bb", "ip": "10.0.0.12", "usuario": 2},
        {"nombre": "inv", "mac": "cc", "ip": "10.0.0.13", "usuario": None},
    ]

    def test_bloquea_a_quien_no_tiene_fila_de_permiso(self):
        reglas = reglas_denegadas(self.HOSTS, [(301, 1)], {(2, 301)})
        self.assertEqual([r["mac_src"] for r in reglas], ["aa", "cc"])
        self.assertTrue(all(r["ip_dst"] == "10.0.0.11" for r in reglas))
        self.assertTrue(all(r["puerto"] == PUERTO_DOC_BASE + 301 for r in reglas))

    def test_documento_de_autor_fuera_de_la_topologia_se_ignora(self):
        self.assertEqual(reglas_denegadas(self.HOSTS, [(301, 99)], set()), [])


if __name__ == "__main__":
    unittest.main()
