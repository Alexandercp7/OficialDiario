import unittest
from backend.juzgados import (
    LISTA_JUZGADOS_YUCATAN,
    normalize_court_name,
    court_matches,
)

class TestJuzgadosModule(unittest.TestCase):
    def test_lista_juzgados_estructura(self):
        """Verifica que la lista de juzgados tenga el formato esperado y elementos únicos."""
        self.assertGreater(len(LISTA_JUZGADOS_YUCATAN), 10)
        ids = set()
        for j in LISTA_JUZGADOS_YUCATAN:
            self.assertIn("id", j)
            self.assertIn("nombre", j)
            self.assertIn("label", j)
            self.assertIn("shortName", j)
            self.assertIn("materia", j)
            self.assertIn("sede", j)
            self.assertNotIn(j["id"], ids, f"ID duplicado: {j['id']}")
            ids.add(j["id"])

    def test_normalize_court_name(self):
        """Verifica la normalización de acentos, mayúsculas y prefijos."""
        self.assertEqual(normalize_court_name(""), "")
        self.assertEqual(normalize_court_name(None), "")
        
        # Debe remover acentos y pasar a mayúsculas
        norm = normalize_court_name("Juzgado Primero de Oralidad Familiar de Mérida")
        self.assertIn("JUZGADO PRIMERO DE ORALIDAD FAMILIAR DE MERIDA", norm)
        self.assertNotIn("É", norm)

        # Debe remover el prefijo 'NOTIFICACIONES DEL'
        raw = "NOTIFICACIONES DEL JUZGADO SEGUNDO MERCANTIL"
        self.assertEqual(normalize_court_name(raw), "JUZGADO SEGUNDO MERCANTIL")

        raw2 = "NOTIFICACIONES DE TRIBUNAL SUPERIOR"
        self.assertEqual(normalize_court_name(raw2), "TRIBUNAL SUPERIOR")

    def test_court_matches_wildcard(self):
        """Verifica que 'Todos', 'Todos los Juzgados' o None coincidan con cualquier juzgado."""
        self.assertTrue(court_matches("Juzgado Primero Civil", "Todos"))
        self.assertTrue(court_matches("Juzgado Primero Civil", "Todos los Juzgados"))
        self.assertTrue(court_matches("Juzgado Primero Civil", "Cualquier Juzgado"))
        self.assertTrue(court_matches("Juzgado Primero Civil", ""))
        self.assertTrue(court_matches("Juzgado Primero Civil", None))

    def test_court_matches_exact_and_partial(self):
        """Verifica coincidencias exactas e insensibles a acentos/mayúsculas."""
        # Mismo juzgado con ligeras variaciones
        self.assertTrue(court_matches(
            "Juzgado Segundo Mercantil",
            "Juzgado Segundo Mercantil"
        ))
        self.assertTrue(court_matches(
            "NOTIFICACIONES DEL JUZGADO SEGUNDO MERCANTIL",
            "Juzgado Segundo Mercantil"
        ))
        self.assertTrue(court_matches(
            "Juzgado Segundo Mercantil",
            "NOTIFICACIONES DEL JUZGADO SEGUNDO MERCANTIL"
        ))
        self.assertTrue(court_matches(
            "juzgado primero de oralidad familiar",
            "JUZGADO PRIMERO DE ORALIDAD FAMILIAR"
        ))

    def test_court_matches_negative(self):
        """Verifica que juzgados diferentes no coincidan falsamente."""
        self.assertFalse(court_matches(
            "Juzgado Primero Mercantil",
            "Juzgado Segundo Mercantil"
        ))
        self.assertFalse(court_matches(
            "Juzgado Primero Civil",
            "Tribunal Superior de Justicia"
        ))
        self.assertFalse(court_matches(
            None,
            "Juzgado Primero Civil"
        ))

if __name__ == "__main__":
    unittest.main()
