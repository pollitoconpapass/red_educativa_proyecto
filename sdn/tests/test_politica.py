import unittest
from config.config import PUERTO_DOC_BASE
from config.politica import reglas_denegadas

class ReglasDenegadasTest(unittest.TestCase):
    HOSTS = [
        {"nombre": "doc", "mac": "aa", "ip": "10.0.0.11", "usuario": 1},
        {"nombre": "est", "mac": "bb", "ip": "10.0.0.12", "usuario": 2},
        {"nombre": "inv", "mac": "cc", "ip": "10.0.0.13", "usuario": None},
    ]

    def test_autor_sin_fila_de_permiso_puede_leer_su_documento(self):
        reglas = reglas_denegadas(self.HOSTS, [(301, 1)], set())
        self.assertEqual([r["mac_src"] for r in reglas], ["bb", "cc"])

    def test_bloquea_a_quien_no_es_autor_ni_tiene_permiso(self):
        reglas = reglas_denegadas(self.HOSTS, [(301, 1)], {(2, 301)})
        self.assertEqual([r["mac_src"] for r in reglas], ["cc"])
        self.assertEqual(reglas[0]["ip_dst"], "10.0.0.11")
        self.assertEqual(reglas[0]["puerto"], PUERTO_DOC_BASE + 301)

    def test_documento_de_autor_fuera_de_la_topologia_se_ignora(self):
        self.assertEqual(reglas_denegadas(self.HOSTS, [(301, 99)], set()), [])


if __name__ == "__main__":
    unittest.main()
