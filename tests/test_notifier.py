import unittest
from backend.notifier import (
    escape_tg_html,
    enviar_notificacion_email,
    enviar_mensaje_telegram,
    notificar_usuario_coincidencias,
)

class TestNotifierModule(unittest.TestCase):
    def test_escape_tg_html(self):
        """Verifica que caracteres <, >, & se escapen correctamente para HTML."""
        self.assertEqual(escape_tg_html(None), "")
        self.assertEqual(escape_tg_html(""), "")
        self.assertEqual(escape_tg_html("Juicio & Auto <Acuerdo>"), "Juicio &amp; Auto &lt;Acuerdo&gt;")
        self.assertEqual(escape_tg_html(12345), "12345")

    def test_enviar_email_sin_destinatario(self):
        """Verifica que el envío de correo falle limpiamente sin destinatario."""
        ok, msg = enviar_notificacion_email({}, "Asunto", "Texto", "<p>HTML</p>")
        self.assertFalse(ok)
        self.assertIn("No se especificó un correo de destinatario válido", msg)

        ok2, msg2 = enviar_notificacion_email({"recipient_email": "   "}, "Asunto", "Texto", "<p>HTML</p>")
        self.assertFalse(ok2)
        self.assertIn("No se especificó un correo de destinatario válido", msg2)

    def test_enviar_telegram_sin_token_o_chat_id(self):
        """Verifica que el envío de telegram falle limpiamente con parámetros vacíos."""
        ok, msg = enviar_mensaje_telegram("", "12345", "Hola")
        self.assertFalse(ok)
        self.assertIn("Falta bot_token", msg)

        ok2, msg2 = enviar_mensaje_telegram("12345:ABC", "", "Hola")
        self.assertFalse(ok2)
        self.assertIn("Falta bot_token", msg2)

    def test_notificar_usuario_coincidencias_vacio(self):
        """Verifica respuesta cuando no hay coincidencias."""
        user = {"id": 1, "name": "Abogado Test", "email": "test@despacho.com"}
        cfg = {"channel": "email", "email": {"recipient_email": "test@despacho.com"}}
        res = notificar_usuario_coincidencias(user, cfg, "2026-09-30", [])
        self.assertEqual(res, "Sin coincidencias para notificar.")

    def test_notificar_usuario_canal_desactivado(self):
        """Verifica respuesta cuando el usuario tiene notificaciones apagadas."""
        user = {"id": 1, "name": "Abogado Test", "email": "test@despacho.com"}
        cfg = {"channel": "none"}
        coincidencias = [{"termino": "69/2026", "juzgado": "Juzgado 1 Civil", "pagina": 1, "contexto": "Auto..."}]
        res = notificar_usuario_coincidencias(user, cfg, "2026-09-30", coincidencias)
        self.assertEqual(res, "Notificaciones desactivadas para este usuario.")

if __name__ == "__main__":
    unittest.main()
