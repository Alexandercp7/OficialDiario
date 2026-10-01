import unittest
from unittest.mock import MagicMock
from backend.cotejo import verificar_cron_secret

class DummyHandler:
    def __init__(self, path="/api/cron/scan", headers=None):
        self.path = path
        self.headers = headers or {}
        self.client_address = ("127.0.0.1", 12345)

class TestCotejoModule(unittest.TestCase):
    def test_verificar_cron_secret_via_header_x_cron_secret(self):
        """Verifica autenticación de cron vía header X-Cron-Secret."""
        handler = DummyHandler(headers={"X-Cron-Secret": "lex_cron_2026_secreto"})
        self.assertTrue(verificar_cron_secret(handler))

    def test_verificar_cron_secret_via_bearer_token(self):
        """Verifica autenticación de cron vía header Authorization Bearer."""
        handler = DummyHandler(headers={"Authorization": "Bearer lex_cron_2026_secreto"})
        self.assertTrue(verificar_cron_secret(handler))

    def test_verificar_cron_secret_via_query_param(self):
        """Verifica autenticación de cron vía query param ?secret= o ?token=."""
        handler1 = DummyHandler(path="/api/cron/scan?secret=lex_cron_2026_secreto")
        self.assertTrue(verificar_cron_secret(handler1))

        handler2 = DummyHandler(path="/api/cron/scan?token=lex_cron_2026_secreto")
        self.assertTrue(verificar_cron_secret(handler2))

    def test_verificar_cron_secret_via_body(self):
        """Verifica autenticación de cron cuando se envía en el cuerpo JSON."""
        handler = DummyHandler()
        body = {"secret": "lex_cron_2026_secreto"}
        self.assertTrue(verificar_cron_secret(handler, body=body))

    def test_verificar_cron_secret_rechazo_invalido(self):
        """Verifica que rechace credenciales inválidas o ausentes."""
        handler_vacio = DummyHandler()
        self.assertFalse(verificar_cron_secret(handler_vacio))

        handler_erroneo = DummyHandler(headers={"X-Cron-Secret": "token_totalmente_falso"})
        self.assertFalse(verificar_cron_secret(handler_erroneo))

        handler_body_erroneo = DummyHandler()
        self.assertFalse(verificar_cron_secret(handler_body_erroneo, body={"secret": "erroneo"}))

if __name__ == "__main__":
    unittest.main()
