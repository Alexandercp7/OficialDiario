import unittest
import re
from backend.scraper import descargar_diario, buscar_terminos_en_pdf

class TestScraperModule(unittest.TestCase):
    def test_expediente_regex_patterns(self):
        """Verifica la lógica de detección y matching de números de expediente con ceros a la izquierda."""
        val = "69/2026"
        m_exp = re.match(r'^0*(\d+)/(\d{4})$', val)
        self.assertIsNotNone(m_exp)
        
        # Regex construida idéntica al scraper
        exp_regex = re.compile(rf'(?<!\d)0*{int(m_exp.group(1))}/{m_exp.group(2)}(?!\d)', re.I)

        # Debe coincidir con formato exacto
        self.assertTrue(exp_regex.search("EXPEDIENTE 69/2026 AUTO"))
        # Debe coincidir con ceros a la izquierda (ej. 00069/2026)
        self.assertTrue(exp_regex.search("EXPEDIENTE 069/2026.- SENTENCIA"))
        self.assertTrue(exp_regex.search("EXP. 00069/2026"))

        # No debe coincidir falsamente con otro expediente (ej. 169/2026 o 69/2025)
        self.assertIsNone(exp_regex.search("EXPEDIENTE 169/2026"))
        self.assertIsNone(exp_regex.search("EXPEDIENTE 69/2025"))
        self.assertIsNone(exp_regex.search("FECHA 2026/09/30"))

    def test_multi_token_name_matching(self):
        """Verifica la coincidencia de nombres con múltiples tokens."""
        nombre_buscado = "Cristopher Axel Garcia"
        tokens = [t.lower() for t in nombre_buscado.split()]

        texto_acuerdo = (
            "CRISTOPHER AXEL GARCIA GUTIERREZ, MARIO ALEJANDRO ARANDA ALDANA.- JUICIO EJECUTIVO "
            "MERCANTIL PROMOVIDO POR EL PRIMERO... EXPEDIENTE 203/2026"
        ).lower()

        self.assertTrue(all(t in texto_acuerdo for t in tokens))

        # Texto donde falta uno de los nombres
        texto_incompleto = "CRISTOPHER GUTIERREZ, MARIO ALEJANDRO".lower()
        self.assertFalse(all(t in texto_incompleto for t in tokens))

    def test_descargar_diario_fecha_invalida(self):
        """Verifica que una fecha inexistente retorne código de error limpiamente."""
        ok, msg = descargar_diario("1900-01-01", "temp_inexistente.pdf")
        self.assertFalse(ok)
        self.assertTrue("404" in msg or "no está publicada" in msg or "Error" in msg)

if __name__ == "__main__":
    unittest.main()
